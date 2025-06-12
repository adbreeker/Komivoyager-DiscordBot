import random
import discord
from discord import app_commands
from discord.ext import voice_recv
import components.voice_transcriber as voice_transcriber
from datetime import datetime
from pathlib import Path
import io

async def connect_to_channel(channel: discord.VoiceChannel, guild_id: int) -> discord.VoiceClient:
    
    if voice_transcriber.is_transcribing(guild_id):
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        await voice_transcriber.start_recording(vc, guild_id)
    else:
        vc = await channel.connect()
    return vc

def get_file_as_discord_file(file_path):
    """Get a file as a discord.File object from a given file path."""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read()
                        
         # Create a temporary file-like object
        file_name = Path(file_path).name
                            
        discord_file = discord.File(
            io.BytesIO(content.encode('utf-8')),
            filename=file_name
        )

        return discord_file
    except Exception as e:
        print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error reading transcript file '{file_path}': {e}")
        return None

def get_greeting(user: discord.User) -> str:
    """Generate a greeting message for a user."""
    name = user.name

    if user.bot:
        return f"Hello bot {name}."

    if name == 'adbreeker':
        random_greetings = [
            f"Hello {name}! You look amazing today!",
            f"Greetings, master {name}!",
            f"Welcome {name}, lovely to have you here!",
            f"All praise the great {name}! Your presence is a gift!",
        ]
        return random.choice(random_greetings)
    else:
        random_greetings = [
            f"Do you smell it? Uh it must be {name}, what a stink!",
            f"Oh hell no, it's {name} again!",
            f"Look who it is, {name}, the destroyer of fun and children's smiles!",
            f"Hi {name}, I am afraid there is no place for you and your belly here at the same time.",
            f"Welcome {name}, could you check if you are not somewhere else?",
            f"Fuck... it's {name}. Another day ruined!",
            f"They say that every newcomer is a gift... They clearly haven't met {name}."
        ]
        return random.choice(random_greetings)
