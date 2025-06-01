import discord
import asyncio
import components.voice_transcriber as voice_transcriber
from components.audio_manager import play_background, say_text
from datetime import datetime

def setup_events(bot):
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
        guild_id = member.guild.id

        # bot state changes
        if member.bot:
            if after.channel is not None:
                print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] {member.name} joined {voice_client.channel.name}")
                # Wait until the bot is fully connected to voice
                while not voice_client.is_connected():
                    await asyncio.sleep(0.1)
                await say_text(voice_client, "Hello there", 'en')
                bot.loop.create_task(play_background(voice_client))

            if after.channel is None and voice_client:
                print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] {member.name} left from {voice_client.channel.name}")
                await voice_transcriber.stop_recording(voice_client, guild_id)

        # user state changes
        if voice_client and voice_client.channel is not None:
            non_bot_members = [m for m in voice_client.channel.members if not m.bot]
            if len(non_bot_members) == 0:
                await asyncio.sleep(1)
                non_bot_members = [m for m in voice_client.channel.members if not m.bot]
                if len(non_bot_members) == 0:
                    await voice_client.disconnect()