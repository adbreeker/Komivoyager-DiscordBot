import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# Import the component modules
from components.bot_commands import setup_commands
from components.bot_events import setup_events


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="@@", intents=intents)

@bot.event
async def on_ready():
    print(f'\nLogged in as {bot.user.name} - {bot.user.id}')
    print(f'Connected to {len(bot.guilds)} server(s):')
    for guild in bot.guilds:
        print(f'  - {guild.name} (ID: {guild.id}) | Members: {guild.member_count}')
    
    print('-----------')
    activity = discord.Game("Ready to solve your np-hard problems | /help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    #bot app status
    import torch
    print("cuda available:", torch.cuda.is_available())
    print("cuDNN available:", torch.backends.cudnn.is_available())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print("-----------\nLogs:\n")

# Set up commands and events
setup_commands(bot)
setup_events(bot)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)