import discord
import yt_dlp
import asyncio
import imageio_ffmpeg
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import components.audio_manager as audio_mgr
from datetime import datetime
import time

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

class YTAudio:
    def __init__(self, source, data, time_played=0):
        self.source = source
        self.data = data  # Store the full YouTube data
        self.title = data.get('title')
        self.url = data.get('url')  # This is the stream URL
        self.webpage_url = data.get('webpage_url')  # This is the original YouTube URL
        self.duration = data.get('duration', 0)
        self.uploader = data.get('uploader')
        self.time_played = time_played
        self.start_time = time.time()
        self.is_paused = False
    
    def pause(self):
        """Pause and update time_played"""
        if not self.is_paused and self.start_time:
            self.time_played += time.time() - self.start_time
            self.is_paused = True
            self.start_time = None
            print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Yt audio paused at {self.time_played:.1f}s")

    def get_time_played(self):
        """Get current playback time"""
        if self.is_paused or not self.start_time:
            return self.time_played
        return self.time_played + (time.time() - self.start_time)

    async def resume(self, voice_client):
        """Resume playback from current position"""
        current_time = self.get_time_played()
        seek_time = max(0, min(current_time, self.duration-1))

        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Yt audio resuming from {seek_time:.1f}s")
        
        try:
            # Create new source with seek
            seek_options = ffmpeg_options.copy()
            if seek_time > 0:
                seek_options['before_options'] = f'-ss {seek_time} ' + seek_options.get('before_options', '')
            
            # Use the original stream URL from data
            filename = self.data['url']
            
            source = FFmpegPCMAudio(
                filename,
                executable=ffmpeg_executable,
                **seek_options
            )

            await play(voice_client, voice_client.guild.id, YTDLSource(source, data=self.data), start_time=seek_time)

        except Exception as e:
            print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error resuming: {e}")
            return False

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
    
async def play(voice_client, guild_id, source, start_time=0):
    """Play a song in the voice channel"""
    try:            
        # Set volume if specified
        if guild_id in audio_mgr.music_volumes:
            source.volume = audio_mgr.music_volumes[guild_id]

        # Stop whatever is playing
        audio_mgr.stop_audio(voice_client)
        
        # Create YTAudio with proper data
        yt_audio = YTAudio(source, source.data, time_played=start_time)
        audio_mgr.current_youtube_players[guild_id] = yt_audio
        loop = asyncio.get_running_loop()

        def after_playing(error):
            if error:
                print(f'[ERROR - {datetime.now().strftime("%H:%M:%S")}] Player error: {error}')
            # Only proceed if this source is still the current one
            if audio_mgr.current_youtube_players.get(guild_id) == yt_audio:
                audio_mgr.current_youtube_players.pop(guild_id, None)
                print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Launching play_next() after {yt_audio.title}")
                fut = asyncio.run_coroutine_threadsafe(play_next(voice_client, guild_id), loop)
            else:
                print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Skipping callback - {yt_audio.title} is no longer current")

        voice_client.play(source, after=after_playing)
    except Exception as e:
        print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error playing song: {e}")

async def play_instantly(voice_client, guild_id, url):
    """Play a song instantly (stops current music)"""
    try:        
        source = await YTDLSource.from_url(url, stream=True)
        await play(voice_client, guild_id, source)
        return source.title, source.uploader
    except Exception as e:
        print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error playing instantly: {e}")
        return None, None
    
async def play_next(voice_client, guild_id):
    """Play the next song in the queue"""
    try:
        await asyncio.sleep(0.1) 
        if guild_id in audio_mgr.music_queues and audio_mgr.music_queues.get(guild_id):
            print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Songs in queue for guild {guild_id}: {len(audio_mgr.music_queues[guild_id])}")
            if audio_mgr.get_current_audio_type(guild_id) in ['background', None]:
                source = audio_mgr.music_queues[guild_id].pop(0)
                print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Playing next song: {source.title} in {voice_client.channel.name}")
                await play(voice_client, guild_id, source)
                return source.title, source.uploader
            elif audio_mgr.get_current_audio_type(guild_id) != 'youtube':
                loop = asyncio.get_running_loop()
                fut = asyncio.run_coroutine_threadsafe(play_next(voice_client, guild_id), loop)
            else:
                print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Canceling play_next() because youtube is currently playing in {voice_client.channel.name}")
        else:
            print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] No songs in queue for guild {guild_id}")
    except Exception as e:
        print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error playing next song: {e}")
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
        print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error adding to queue: {e}")
        return None, None

def get_queue(guild_id):
    """Get current queue for a guild"""
    return audio_mgr.music_queues.get(guild_id, [])

def clear_queue(guild_id):
    """Clear the queue for a guild"""
    if guild_id in audio_mgr.music_queues:
        audio_mgr.music_queues[guild_id] = []

def get_current_song_info(guild_id):
    """Get currently playing song with timing info"""
    yt_audio = audio_mgr.current_youtube_players.get(guild_id)
    if yt_audio:
        def format_time(seconds):
            """Format seconds to MM:SS"""
            if seconds is None:
                return "??:??"
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"

        current_time = yt_audio.get_time_played()
        return yt_audio.title, yt_audio.uploader, format_time(current_time), format_time(yt_audio.duration)
    return None, None, None, None

def set_volume(guild_id, volume):
    """Set volume for current and future songs"""
    audio_mgr.music_volumes[guild_id] = volume
    if guild_id in audio_mgr.current_youtube_players:
        audio_mgr.current_youtube_players[guild_id].volume = volume

def get_volume(guild_id):
    """Get current volume"""
    return audio_mgr.music_volumes.get(guild_id, 0.5)