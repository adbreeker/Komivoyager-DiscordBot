import discord
from discord.ext import commands, voice_recv
import logging
from dotenv import load_dotenv
import os
import asyncio
import voice_transcriber  # <-- Add this import


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='@@', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server, {member.name}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if 'potwierdzam' in message.content.lower():
        await message.delete()
        await message.channel.send(f'{message.author.mention}, tutaj się nie potwierdza!')

    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)

    if not member.bot:
        if after.channel is not None and not voice_client:
            await asyncio.sleep(0.5)
            if len(after.channel.members) >= 0 and not voice_client:
                vc = await after.channel.connect(cls=voice_recv.VoiceRecvClient)
                await voice_transcriber.start_recording(vc)

        if voice_client and voice_client.channel is not None:
            # Count non-bot members in the channel
            non_bot_members = [m for m in voice_client.channel.members if not m.bot]
            if len(non_bot_members) == 0:
                await asyncio.sleep(0.5)
                non_bot_members = [m for m in voice_client.channel.members if not m.bot]
                if len(non_bot_members) == 0:
                    await voice_client.disconnect()
 

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def echo(ctx, *, message: str):
    await ctx.reply(message)

@bot.command()
async def demokracja(ctx, *, question: str):
    embed = discord.Embed(title="Demokracja!", description=question, color=0x00ff00)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
    else:
        await ctx.reply("You are not connected to a voice channel.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)