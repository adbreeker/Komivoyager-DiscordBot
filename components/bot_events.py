import discord
import asyncio
from discord.ext import voice_recv
import components.voice_transcriber as voice_transcriber

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
                    await asyncio.sleep(1)
                    non_bot_members = [m for m in voice_client.channel.members if not m.bot]
                    if len(non_bot_members) == 0:
                        await voice_client.disconnect()