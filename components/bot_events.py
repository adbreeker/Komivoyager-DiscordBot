import discord
import asyncio
import components.voice_transcriber as voice_transcriber
from components.audio_manager import play_background, say_text
import components.utilis as utils
from datetime import datetime

def setup_events(bot):
    @bot.event
    async def on_member_join(member):
        await member.send(f'Welcome to the server, {member.name}!')

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            await message.add_reaction('🗑️')
            return

        if 'potwierdzam' in message.content.lower():
            await message.delete()
            await message.channel.send(f'{message.author.mention}, tutaj się nie potwierdza!')

        await bot.process_commands(message)
    
    @bot.event
    async def on_raw_reaction_add(payload):
        if payload.user_id == bot.user.id:
            return

        # Delete bot message with trash emoji
        if str(payload.emoji) == '🗑️':
            try:
                # Get the channel and message
                channel = bot.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)

                if message.author.id == bot.user.id:
                    user = bot.get_user(payload.user_id)
                    await message.delete()
                    print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Message deleted by {user.name} via reaction in {channel.name}")
                    
            except discord.errors.NotFound:
                print(f"[WARNING - {datetime.now().strftime('%H:%M:%S')}] Message already deleted")
            except discord.errors.Forbidden:
                print(f"[WARNING - {datetime.now().strftime('%H:%M:%S')}] Cannot delete message - missing permissions")
            except Exception as e:
                print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error deleting message via reaction: {e}")

    @bot.event
    async def on_voice_state_update(member, before, after):
        voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
        guild_id = member.guild.id

        # bot state changes
        if member == bot.user:
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
        elif member is not bot.user:
            if voice_client and after.channel is voice_client.channel and after.channel is not None:
                print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] {member.name} joined {after.channel.name}")
                await asyncio.sleep(0.5)
                await say_text(voice_client, utils.get_greeting(member), 'en')
                

        # all state changes
        if voice_client and voice_client.channel is not None:
            non_bot_members = [m for m in voice_client.channel.members if not m.bot]
            if len(non_bot_members) == 0:
                await asyncio.sleep(1)
                non_bot_members = [m for m in voice_client.channel.members if not m.bot]
                if len(non_bot_members) == 0:
                    await voice_client.disconnect()