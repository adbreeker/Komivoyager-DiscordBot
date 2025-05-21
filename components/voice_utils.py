import asyncio
import discord
import imageio_ffmpeg

async def play_quiet_noise(voice_client):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    while True:
        if not voice_client.is_connected():
            break
        if not voice_client.is_playing():
            source = discord.FFmpegPCMAudio("assets/sounds/quiet_noise.wav", executable=ffmpeg_path, pipe=False)
            voice_client.play(source)
        await asyncio.sleep(3)