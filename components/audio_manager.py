import asyncio
import discord
import imageio_ffmpeg
from mutagen.mp3 import MP3
from components.voice_transcriber import is_transcribing

# Global audio state management
current_background_music = {}  # guild_id: background_music_source
current_voice_sources = {}  # guild_id: audio_source
music_volumes = {}  # guild_id: volume (0.0-1.0)
background_volumes = {}  # guild_id: float

# Music queue system
music_queues = {}  # guild_id: list of (YTDLSource, title, uploader)
current_youtube_players = {}  # guild_id: current_youtube_source

def is_playing_youtube(guild_id):
    """Check if YouTube music is currently playing"""
    return guild_id in current_youtube_players and current_youtube_players[guild_id] is not None

def is_playing_voice(guild_id):
    """Check if voice source is currently playing"""
    return guild_id in current_voice_sources and current_voice_sources[guild_id] is not None

def is_playing_background(guild_id):
    """Check if background music is currently playing"""
    return guild_id in current_background_music and current_background_music[guild_id] is not None

def get_current_audio_type(guild_id):
    """Get what type of audio is currently playing"""
    if is_playing_youtube(guild_id):
        return "youtube"
    elif is_playing_background(guild_id):
        return "background"
    elif is_playing_voice(guild_id):
        return "voice"
    else:
        return None
    
def stop_audio(voice_client):
    guild_id = voice_client.guild.id
    is_transcribing_now = is_transcribing(guild_id)
    
    if is_transcribing_now:
        # If transcribing, only stop the audio source, don't call voice_client.stop()
        if voice_client.is_playing():
            # Get the current source and stop it manually
            for storage in [current_background_music, current_voice_sources, current_youtube_players]:
                source = storage.get(guild_id)
                if source:
                    try:
                        source.cleanup()
                    except Exception as e:
                        print(f"Error stopping source: {e}")
            # Force stop by setting internal state (this is a workaround)
            voice_client._player = None
        # Keep the voice receiver active - don't restart listening
    else:
        # If not transcribing, use the normal stop method
        voice_client.stop()

async def play_background(voice_client):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    mp3_path = "assets/sounds/flute-background.mp3"
    guild_id = voice_client.guild.id
    print("Preparing to play background music in", voice_client.channel.name)

    async def play_next(counter):
        await asyncio.sleep(0.5)
        if voice_client.is_connected():
            if voice_client.is_playing():
                if counter % 60 == 0:
                    print(f"Waiting to start background music in {voice_client.channel.name}")
                await asyncio.sleep(1)
                await play_next(counter+1)
            else:
                print(f"Playing background music in {voice_client.channel.name}")
                volume = background_volumes.get(guild_id, 0.0)
                ffmpeg_source = discord.FFmpegPCMAudio(
                    mp3_path,
                    executable=ffmpeg_path,
                    pipe=False,
                )
                source = discord.PCMVolumeTransformer(ffmpeg_source, volume=volume)
                current_background_music[guild_id] = source
                loop = asyncio.get_running_loop()
                def after_callback(e):
                    # Clean up the source reference
                    current_background_music.pop(guild_id, None)
                    # Don't restart listening - it's already active during transcription
                    asyncio.run_coroutine_threadsafe(play_next(0), loop)
                voice_client.play(source, after=after_callback)
        else:
            print(f"Voice client is not connected in {voice_client.channel.name}")
            return

    await play_next(0)

def set_background_volume(guild_id, volume):
    background_volumes[guild_id] = volume
    if is_playing_background(guild_id):
        source = current_background_music.get(guild_id)
        if source:
            try:
                source.volume = volume
            except Exception as e:
                print(f"Error setting background volume: {e}")