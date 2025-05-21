import asyncio
import re

BINGO_WORDS = {"ward", "wards", "wardy", "warda", "pinka"}
bot = None
guild_id_to_channel_id = {}

# Thread-safe queue for incoming texts
bingo_queue = asyncio.Queue()

def set_bot(bot_instance):
    global bot
    bot = bot_instance

def set_guild_channel(guild_id, channel_id):
    guild_id_to_channel_id[guild_id] = channel_id

def queue_bingo_check(text, author, guild_id):
    # This can be called from any thread
    loop = None
    if bot and hasattr(bot, "loop"):
        loop = bot.loop
    else:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
    if loop and loop.is_running():
        loop.call_soon_threadsafe(bingo_queue.put_nowait, (text, author, guild_id))

async def bingo_worker():
    while True:
        text, author, guild_id = await bingo_queue.get()
        pattern = r"\b(" + "|".join(BINGO_WORDS) + r")\b"
        if re.search(pattern, text, re.IGNORECASE):
            await send_bingo_message(guild_id)
        bingo_queue.task_done()

async def send_bingo_message(guild_id):
    if bot is None:
        return
    channel = None
    if guild_id in guild_id_to_channel_id:
        channel = bot.get_channel(guild_id_to_channel_id[guild_id])
    else:
        guild = bot.get_guild(guild_id)
        if guild:
            channel = guild.system_channel
    if channel:
        await channel.send("bingo")

def start_bingo_worker():
    if bot and hasattr(bot, "loop"):
        bot.loop.create_task(bingo_worker())