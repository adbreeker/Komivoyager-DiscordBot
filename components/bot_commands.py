import discord
from discord import app_commands
import components.voice_transcriber as voice_transcriber
from discord.ext import voice_recv
from components.voice_utils import set_background_volume

def setup_commands(bot):
    @bot.tree.command(name="kv_hello", description="Greets you back dupa!")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")

    @bot.tree.command(name="kv_echo", description="Replies with your message.")
    @app_commands.describe(message="The message to echo")
    async def echo(interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

    @bot.tree.command(name="kv_demokracja", description="Creates a quick poll.")
    @app_commands.describe(question="The poll question")
    async def demokracja(interaction: discord.Interaction, question: str):
        embed = discord.Embed(title="Demokracja!", description=question, color=0x00ff00)
        poll_message = await interaction.channel.send(embed=embed)
        await poll_message.add_reaction('👍')
        await poll_message.add_reaction('👎')
        await interaction.response.send_message("Poll created!", ephemeral=True)

    @bot.tree.command(name="kv_join", description="Joins a voice channel.")
    async def join(interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            voice_client = interaction.guild.voice_client
            guild_id = interaction.guild.id

            if voice_client is None:
                if voice_transcriber.is_transcribing(guild_id):
                    vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
                else:
                    vc = await channel.connect()
                await interaction.response.send_message(f"Joined {channel.name}!", ephemeral=True)
            else:
                await voice_client.disconnect()
                if voice_transcriber.is_transcribing(guild_id):
                    vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
                else:
                    vc = await channel.connect()
                await interaction.response.send_message(f"Moved to {channel.name}!", ephemeral=True)
        else:
            await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)

    @bot.tree.command(name="kv_transcript", description="Enable or disable voice transcription.")
    @app_commands.describe(action="on,off or status")
    async def transcript(interaction: discord.Interaction, action: str):
        guild_id = interaction.guild.id
        if action.lower() == "status":
            
            if voice_transcriber.is_transcribing(guild_id):
                await interaction.response.send_message("Transcription is currently enabled.", ephemeral=True)
            else:
                await interaction.response.send_message("Transcription is currently disabled.", ephemeral=True)
            return

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("You must be in a voice channel.", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client
        if action.lower() == "on":
            voice_transcriber.set_transcribing(guild_id, True)
            if voice_client:
                await voice_client.disconnect() 
            voice_client = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
            await voice_transcriber.start_recording(voice_client)
            await interaction.response.send_message("Transcription enabled.", ephemeral=True)
        elif action.lower() == "off":
            voice_transcriber.set_transcribing(guild_id, False)
            if voice_client:
                await voice_client.disconnect() 
                voice_client = await interaction.user.voice.channel.connect()
            await voice_transcriber.stop_recording(guild_id)
            await interaction.response.send_message("Transcription disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Wrong command!\nUsage: /kv_transcript {on/off/status}", ephemeral=True)

    @bot.tree.command(name="kv_background", description="Set background music volume (0.0 - 2.0)")
    async def background(interaction: discord.Interaction, volume: float):
        if not 0.0 <= volume <= 2.0:
            await interaction.response.send_message("Volume must be between 0.0 and 2.0", ephemeral=True)
            return
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message("Bot is not in a voice channel.", ephemeral=True)
            return
        set_background_volume(interaction.guild.id, volume, voice_client)
        await interaction.response.send_message(f"Background music volume set to {volume}", ephemeral=True)