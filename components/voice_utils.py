import asyncio
import discord
import imageio_ffmpeg
from mutagen.mp3 import MP3
import components.voice_transcriber as vt

background_volumes = {}  # guild_id: float

async def play_background(voice_client):
    if voice_client.is_playing():
        stop_voice(voice_client)
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    mp3_path = "assets/sounds/flute-background.mp3"
    guild_id = voice_client.guild.id
    print("Preparing to play background music in", voice_client.channel.name)

    async def play_next(_):
        await asyncio.sleep(0.1)
        if voice_client.is_connected():
            if voice_client.is_playing():
                print(f"Waiting for background music to finish in {voice_client.channel.name}")
                await asyncio.sleep(1)
                play_next(None)
            else:
                print(f"Playing background music in {voice_client.channel.name}")
                volume = background_volumes.get(guild_id, 0.0)
                source = discord.FFmpegPCMAudio(
                    mp3_path,
                    executable=ffmpeg_path,
                    pipe=False,
                    options=f'-filter:a "volume={volume}"'
                )
                loop = asyncio.get_running_loop()
                def after_callback(e):
                    asyncio.run_coroutine_threadsafe(play_next(e), loop)
                voice_client.play(source, after=after_callback)
        else:
            print(f"Voice client is not connected in {voice_client.channel.name}")
            return


    await play_next(None)

async def set_background_volume(guild_id, volume, voice_client):
    background_volumes[guild_id] = volume
    if voice_client and voice_client.is_playing():
        await stop_voice(voice_client)

def stop_voice(voice_client):
    voice_client.stop()
    if vt.is_transcribing(voice_client.guild.id):
        voice_client.listen(vt.WhisperSink())