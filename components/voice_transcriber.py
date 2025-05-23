import asyncio
import threading
import concurrent.futures
from discord.ext import voice_recv
from faster_whisper import WhisperModel
import numpy as np
from scipy.signal import resample, butter, filtfilt, wiener
import time
import os
from datetime import datetime
import torch


print("cuda available:", torch.cuda.is_available())
print("cuDNN available:", torch.backends.cudnn.is_available())

# Load faster-whisper model once
whisper_model = WhisperModel("turbo", device="cuda", compute_type="float32")

user_audio_buffers = {}
user_last_audio_time = {}
user_names = {}
SILENCE_TIMEOUT = 0.5  #seconds

transcribing_enabled = {}  # guild_id: bool
current_voice_clients = {}  # guild_id: voice_client

# Track the current transcript file per guild
transcript_files = {}  # guild_id: (file_path, start_datetime)

def get_transcript_file(guild_id):
    # If already open, return path
    if guild_id in transcript_files:
        return transcript_files[guild_id][0]
    # Otherwise, create new file
    start_dt = datetime.now()
    date_str = start_dt.strftime("%Y-%m-%d")
    os.makedirs("transcripts", exist_ok=True)
    os.makedirs(f"transcripts/Guild_{guild_id}", exist_ok=True)
    file_path = os.path.join("transcripts", f"Guild_{guild_id}", f"{date_str}.txt")
    transcript_files[guild_id] = (file_path, start_dt)
    # Touch the file
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"# Transcription started at {start_dt.isoformat()}\n")
    return file_path

def close_transcript_file(guild_id):
    if guild_id in transcript_files:
        file_path, start_dt = transcript_files[guild_id]
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"# Transcription ended at {datetime.now().isoformat()}\n")
        del transcript_files[guild_id]

class WhisperSink(voice_recv.BasicSink):
    def __init__(self):
        super().__init__(self.callback)

    def callback(self, user, data: voice_recv.VoiceData):
        guild_id = user.guild.id if hasattr(user, "guild") else None
        if guild_id and not is_transcribing(guild_id):
            return
        if user is None:
            return
        user_id = user.id
        user_name = user.name
        pcm = data.pcm
        now = time.time()
        # Use (user_id, guild_id) as the key
        key = (user_id, guild_id)
        if key not in user_audio_buffers:
            user_audio_buffers[key] = b""
            user_last_audio_time[key] = now
        user_audio_buffers[key] += pcm
        user_last_audio_time[key] = now
        user_names[key] = user_name

    def process_buffer(self, guild_id, user_id, user_name, buffer_data):
        try:
            raw = buffer_data
            audio_data = np.frombuffer(raw, np.int16)
            if audio_data.ndim == 1 and len(audio_data) % 2 == 0:
                audio_data = audio_data.reshape(-1, 2)
                audio_data = audio_data.mean(axis=1)
            audio_data = audio_data.astype(np.float32) / 32768.0
            
            # --- ADD RMS THRESHOLD CHECK ---
            rms = np.sqrt(np.mean(audio_data ** 2))
            if rms < 0.004:  # Skip very quiet audio (adjust as needed)
                return
            
            gain = 15.0
            audio_data = np.clip(audio_data * gain, -1.0, 1.0)
            orig_sr = 48000
            target_sr = 16000
            if len(audio_data) > 0 and orig_sr != target_sr:
                num_samples = int(len(audio_data) * target_sr / orig_sr)
                audio_data = resample(audio_data, num_samples)

            # Add noise reduction and normalization
            def enhance_audio(audio_data):
                # Normalize to prevent clipping
                max_val = np.max(np.abs(audio_data))
                if max_val > 0:
                    audio_data = audio_data / max_val * 0.95

                # High-pass filter (remove low-frequency noise)
                b, a = butter(4, 100, btype='high', fs=16000)  # Slightly higher cutoff
                audio_data = filtfilt(b, a, audio_data)
                
                # Low-pass filter (remove high-frequency noise)
                b, a = butter(4, 7000, btype='low', fs=16000)
                audio_data = filtfilt(b, a, audio_data)
                
                # Apply Wiener filter for noise reduction (optional)
                try:
                    audio_data = wiener(audio_data, noise=0.01)
                except:
                    pass  # Skip if wiener filter fails
                
                return audio_data.astype(np.float32)

            # Use it before transcription:
            audio_data = enhance_audio(audio_data)

            segments, _ = whisper_model.transcribe(
                audio_data,
                language="pl",
                task="transcribe",
                temperature=0.3,  # Lower temperature = more conservative
                beam_size=25,      # Reduce beam size for faster, more focused results
                best_of=25,                
                patience=2.0,     # Lower patience
                condition_on_previous_text=False, 
                without_timestamps=True,
                no_repeat_ngram_size=4,
                log_prob_threshold=-1.5,     # Higher threshold = stricter filtering
                compression_ratio_threshold=2.0,  # Lower = stricter
                no_speech_threshold=0.4,     # Lower = more likely to detect speech
                vad_filter=True,
                vad_parameters={
                    "threshold": 0.6, 
                    "min_speech_duration_ms": 250,  # Minimum speech duration
                    "min_silence_duration_ms": 100 
                }, 
            )
            text = "".join([s.text for s in segments]).strip()
            if text and guild_id:
                file_path = get_transcript_file(guild_id)
                now_str = datetime.now().strftime("%H:%M:%S")
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"{now_str} - {user_name}: {text}\n")
        except Exception as e:
            print(f"[ERROR] Exception in process_buffer for {user_name} ({guild_id}): {e}")

# Create a dictionary to hold per-user executors
user_executors = {}

def get_user_executor(user_id):
    # Each user gets their own single-thread executor
    if user_id not in user_executors:
        user_executors[user_id] = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    return user_executors[user_id]

# Silence watcher: also copy and clear buffer before processing
def silence_watcher():
    while True:
        now = time.time()
        for key in list(user_audio_buffers.keys()):
            user_id, guild_id = key
            last = user_last_audio_time.get(key, now)
            if len(user_audio_buffers[key]) > 0 and now - last > SILENCE_TIMEOUT:
                buffer_copy = user_audio_buffers[key]
                user_audio_buffers[key] = b""
                user_name = user_names.get(key, "unknown")
                executor = get_user_executor(user_id)
                try:
                    executor.submit(WhisperSink().process_buffer, guild_id, user_id, user_name, buffer_copy)
                except Exception as e:
                    print(f"[ERROR] Failed to submit process_buffer for {user_name} ({guild_id}): {e}")
        time.sleep(0.2)

threading.Thread(target=silence_watcher, daemon=True).start()

def is_transcribing(guild_id):
    return transcribing_enabled.get(guild_id, False)

def set_transcribing(guild_id, value):
    transcribing_enabled[guild_id] = value
    if not value:
        close_transcript_file(guild_id)

async def start_recording(vc):
    guild_id = vc.guild.id
    current_voice_clients[guild_id] = vc
    try:
        vc.stop_listening()
    except Exception:
        pass
    if is_transcribing(guild_id):
        get_transcript_file(guild_id)  # Ensure file is created
        vc.listen(WhisperSink())

async def stop_recording(guild_id):
    vc = current_voice_clients.get(guild_id)
    if vc:
        try:
            vc.stop_listening()
        except Exception:
            pass
        current_voice_clients.pop(guild_id, None)
    close_transcript_file(guild_id)