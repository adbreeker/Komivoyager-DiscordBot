import asyncio
import re

# Set of bingo keywords (case-insensitive)
BINGO_WORDS = {"ward", "wards", "wardy", "warda", "pinka"}

# This should be set by your bot setup code
bot = None
guild_id_to_channel_id = {}  # Optionally map guild_id to a text channel for bingo messages

def set_bot(bot_instance):
    global bot
    bot = bot_instance

def set_guild_channel(guild_id, channel_id):
    guild_id_to_channel_id[guild_id] = channel_id

async def bingo_check(texts_and_authors, guild_id):
    """
    texts_and_authors: list of (text, author) tuples
    guild_id: int
    """
    # Flatten all texts to one string for search
    pattern = r"\b(" + "|".join(BINGO_WORDS) + r")\b"
    for text, author in texts_and_authors:
        if re.search(pattern, text, re.IGNORECASE):
            # Send bingo message to the configured channel or the system channel
            await send_bingo_message(guild_id)
            break

async def send_bingo_message(guild_id):
    if bot is None:
        return
    channel = None
    # Try to use mapped channel, else use system_channel
    if guild_id in guild_id_to_channel_id:
        channel = bot.get_channel(guild_id_to_channel_id[guild_id])
    else:
        guild = bot.get_guild(guild_id)
        if guild:
            channel = guild.system_channel
    if channel:
        await channel.send("bingo")