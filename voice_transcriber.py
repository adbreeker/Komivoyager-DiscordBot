from discord.ext import voice_recv
from faster_whisper import WhisperModel
import numpy as np
import wave
import os
from scipy.signal import resample

# Load faster-whisper model once
whisper_model = WhisperModel("medium", device="cpu")

user_audio_buffers = {}

class WhisperSink(voice_recv.BasicSink):
    def __init__(self):
        super().__init__(self.callback)

    def callback(self, user, data: voice_recv.VoiceData):
        if user is None:
            return
        user_id = user.id
        user_name = user.name
        pcm = data.pcm
        if user_id not in user_audio_buffers:
            user_audio_buffers[user_id] = b""
        user_audio_buffers[user_id] += pcm

        # 48000 samples/sec * 2 bytes/sample * 5 sec = 480000 bytes (mono)
        if len(user_audio_buffers[user_id]) >= 48000 * 2 * 10:
            raw = user_audio_buffers[user_id]
            audio_data = np.frombuffer(raw, np.int16)

            # If stereo, convert to mono by averaging channels
            if audio_data.ndim == 1 and len(audio_data) % 2 == 0:
                audio_data = audio_data.reshape(-1, 2)
                audio_data = audio_data.mean(axis=1)

            # Normalize to float32 in range [-1, 1]
            audio_data = audio_data.astype(np.float32) / 32768.0

            # Optional: Amplify (not too much)
            gain = 15.0
            audio_data = np.clip(audio_data * gain, -1.0, 1.0)

            # Resample to 16kHz for Whisper
            orig_sr = 48000
            target_sr = 16000
            if len(audio_data) > 0 and orig_sr != target_sr:
                num_samples = int(len(audio_data) * target_sr / orig_sr)
                audio_data = resample(audio_data, num_samples)

            # Save resampled audio to WAV for debugging
            save_dir = "debug_audio"
            os.makedirs(save_dir, exist_ok=True)
            wav_path = os.path.join(save_dir, f"{user_name}_{user_id}_amplified_16k.wav")
            audio_to_save = (audio_data * 32767.0).astype(np.int16)
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(16000)
                wf.writeframes(audio_to_save.tobytes())

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

            # Clear buffer after processing
            user_audio_buffers[user_id] = b""

async def start_recording(vc):
    if not isinstance(vc, voice_recv.VoiceRecvClient):
        return
    vc.listen(WhisperSink())