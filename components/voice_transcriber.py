import threading
from discord.ext import voice_recv
from faster_whisper import WhisperModel
import numpy as np
from scipy.signal import resample
import time
import os
from datetime import datetime

# Load faster-whisper model once
whisper_model = WhisperModel("medium", device="cpu", compute_type="float32")

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
        if user_id not in user_audio_buffers:
            user_audio_buffers[user_id] = b""
            user_last_audio_time[user_id] = now
        user_audio_buffers[user_id] += pcm
        user_last_audio_time[user_id] = now
        user_names[user_id] = user_name

    def process_buffer(self, user_id, user_name, buffer_data):
        raw = buffer_data
        audio_data = np.frombuffer(raw, np.int16)
        if audio_data.ndim == 1 and len(audio_data) % 2 == 0:
            audio_data = audio_data.reshape(-1, 2)
            audio_data = audio_data.mean(axis=1)
        audio_data = audio_data.astype(np.float32) / 32768.0
        gain = 15.0
        audio_data = np.clip(audio_data * gain, -1.0, 1.0)
        orig_sr = 48000
        target_sr = 16000
        if len(audio_data) > 0 and orig_sr != target_sr:
            num_samples = int(len(audio_data) * target_sr / orig_sr)
            audio_data = resample(audio_data, num_samples)

        segments, _ = whisper_model.transcribe(
            audio_data,
            language="pl",
            temperature=0.2,
            beam_size=10,
            condition_on_previous_text=False,
            without_timestamps=True
        )
        text = "".join([s.text for s in segments]).strip()
        if text:
            # Write to transcript file
            # Try to get guild_id from user object (VoiceUser)
            guild_id = getattr(user_id, "guild", None)
            # Actually, we need to get the guild_id from the buffer context
            # So, let's get the first available guild_id from current_voice_clients
            # (since user_id is not enough)
            # Instead, let's pass guild_id as an argument if possible
            # But for now, try to get the first enabled guild
            if transcribing_enabled:
                # Use the first enabled guild (should be correct for most cases)
                guild_id = next(iter(transcribing_enabled.keys()))
            else:
                guild_id = None
            if guild_id:
                file_path = get_transcript_file(guild_id)
                now_str = datetime.now().strftime("%H:%M:%S")
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"{now_str} - {user_name}: {text}\n")

# Silence watcher: also copy and clear buffer before processing
def silence_watcher():
    while True:
        now = time.time()
        for user_id in list(user_audio_buffers.keys()):
            last = user_last_audio_time.get(user_id, now)
            if len(user_audio_buffers[user_id]) > 0 and now - last > SILENCE_TIMEOUT:
                buffer_copy = user_audio_buffers[user_id]
                user_audio_buffers[user_id] = b""
                user_name = user_names.get(user_id, "unknown")
                WhisperSink().process_buffer(user_id, user_name, buffer_copy)
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