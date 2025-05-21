import threading
from discord.ext import voice_recv
from faster_whisper import WhisperModel
import numpy as np
from scipy.signal import resample
import time

# Load faster-whisper model once
whisper_model = WhisperModel("medium", device="cpu")

user_audio_buffers = {}
user_last_audio_time = {}
user_names = {}
SILENCE_TIMEOUT = 1.0  #seconds

class WhisperSink(voice_recv.BasicSink):
    def __init__(self):
        super().__init__(self.callback)

    def callback(self, user, data: voice_recv.VoiceData):
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
        text = "".join([s.text for s in segments])
        print(f"Transcription from user {user_name}: {text}")

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

async def start_recording(vc):
    if not isinstance(vc, voice_recv.VoiceRecvClient):
        return
    vc.listen(WhisperSink())