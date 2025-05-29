import discord
from discord import app_commands
from discord.ext import voice_recv
from components.voice_transcriber import is_transcribing

async def connect_to_channel(channel: discord.VoiceChannel, guild_id: int) -> discord.VoiceClient:
    
    if is_transcribing(guild_id):
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
    else:
        vc = await channel.connect()
    return vc