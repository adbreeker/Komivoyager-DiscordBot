# debug_transcribe.py
import numpy as np
import wave
from faster_whisper import WhisperModel
from scipy.signal import resample

# Path to your saved WAV file
wav_path = "debug_audio/adbreeker_341312346515570688_amplified.wav"  # Replace with actual file name

# Load audio from WAV
with wave.open(wav_path, "rb") as wf:
    n_channels = wf.getnchannels()
    framerate = wf.getframerate()
    n_frames = wf.getnframes()
    audio_bytes = wf.readframes(n_frames)

audio_data = np.frombuffer(audio_bytes, np.int16)
if n_channels == 2:
    audio_data = audio_data.reshape(-1, 2)
    audio_data = audio_data.mean(axis=1)
audio_data = audio_data.astype(np.float32) / 32768.0

# Resample to 16000 Hz for Whisper
target_sr = 16000
if framerate != target_sr:
    num_samples = int(len(audio_data) * target_sr / framerate)
    audio_data = resample(audio_data, num_samples)

# Debugging information
print("Shape:", audio_data.shape)
print("Min:", audio_data.min(), "Max:", audio_data.max())
print("Duration (s):", len(audio_data) / target_sr)

# Load model
whisper_model = WhisperModel("base", device="cpu")

# Transcribe
segments, _ = whisper_model.transcribe(
    audio_data,
    language="pl",
    temperature=0.2,
    beam_size=10,
    condition_on_previous_text=False,
    without_timestamps=True
)
text = "".join([s.text for s in segments])
print("Transcription:", text)