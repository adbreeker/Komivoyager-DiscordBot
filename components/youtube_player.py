import discord
import yt_dlp
import asyncio
import imageio_ffmpeg
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import components.audio_manager as audio_mgr

# Get bundled FFmpeg executable
ffmpeg_executable = imageio_ffmpeg.get_ffmpeg_exe()

# yt-dlp options
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        
        # Use bundled FFmpeg executable
        source = FFmpegPCMAudio(
            filename, 
            executable=ffmpeg_executable,
            **ffmpeg_options
        )
        
        return cls(source, data=data)
    
async def play(voice_client, guild_id, source):
    """Play a song in the voice channel"""
    try:            
            # Set volume if specified
        if guild_id in audio_mgr.music_volumes:
            source.volume = audio_mgr.music_volumes[guild_id]
            
        audio_mgr.current_youtube_players[guild_id] = source
        loop = asyncio.get_running_loop()

        def after_playing(error):
            if error:
                print(f'Player error: {error}')
            audio_mgr.current_youtube_players.pop(guild_id, None)
            fut = asyncio.run_coroutine_threadsafe(play_next(voice_client, guild_id), loop)
            
        # Stop whatever is playing
        audio_mgr.stop_audio(voice_client)
        voice_client.play(source, after=after_playing)
    except Exception as e:
        print(f"Error playing song: {e}")

async def play_instantly(voice_client, guild_id, url):
    """Play a song instantly (stops current music)"""
    try:        
        source = await YTDLSource.from_url(url, stream=True)
        await play(voice_client, guild_id, source)
        return source.title, source.uploader
    except Exception as e:
        print(f"Error playing instantly: {e}")
        return None, None
    
async def play_next(voice_client, guild_id):
    """Play the next song in the queue"""
    try:
        await asyncio.sleep(0.1)  # Allow time for cleanup
        if guild_id in audio_mgr.music_queues and audio_mgr.music_queues[guild_id]:
            if audio_mgr.get_current_audio_type(guild_id) in ['background', None]:
                source = audio_mgr.music_queues[guild_id].pop(0)
                await play(voice_client, guild_id, source)
                return source.title, source.uploader
            elif audio_mgr.get_current_audio_type(guild_id) != 'youtube':
                loop = asyncio.get_running_loop()
                fut = asyncio.run_coroutine_threadsafe(play_next(voice_client, guild_id), loop)
    except Exception as e:
        print(f"Error playing next song: {e}")
    return None, None
    
async def add_to_queue(guild_id, url):
    """Add a song to the queue (enqueue)"""
    try:
        source = await YTDLSource.from_url(url, stream=True)
        if guild_id not in audio_mgr.music_queues:
            audio_mgr.music_queues[guild_id] = []
        audio_mgr.music_queues[guild_id].append(source)
        return source.title, source.uploader
    except Exception as e:
        print(f"Error adding to queue: {e}")
        return None, None

def get_queue(guild_id):
    """Get current queue for a guild"""
    return audio_mgr.music_queues.get(guild_id, [])

def clear_queue(guild_id):
    """Clear the queue for a guild"""
    if guild_id in audio_mgr.music_queues:
        audio_mgr.music_queues[guild_id] = []

def get_current_song_info(guild_id):
    """Get currently playing song"""
    source = audio_mgr.current_youtube_players.get(guild_id)
    if source:
        return source.title, source.uploader
    return None, None

def set_volume(guild_id, volume):
    """Set volume for current and future songs"""
    audio_mgr.music_volumes[guild_id] = volume
    if guild_id in audio_mgr.current_youtube_players:
        audio_mgr.current_youtube_players[guild_id].volume = volume

def get_volume(guild_id):
    """Get current volume"""
    return audio_mgr.music_volumes.get(guild_id, 0.5)

def stop_music(guild_id):
    """Stop music and clear queue"""
    clear_queue(guild_id)
    audio_mgr.current_youtube_players.pop(guild_id, None)