import discord
from discord import app_commands

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

            if voice_client is None:
                await channel.connect()
                await interaction.response.send_message(f"Joined {channel.name}!", ephemeral=True)
            else:
                await voice_client.disconnect()
                await channel.connect()
                await interaction.response.send_message(f"Moved to {channel.name}!", ephemeral=True)
        else:
            await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)