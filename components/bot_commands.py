import discord
from discord import app_commands
import components.voice_transcriber as voice_transcriber
from discord.ext import voice_recv
import components.youtube_player as yt_player
import components.audio_manager as audio_mgr
import components.utilis as utils
from datetime import datetime

def setup_commands(bot):
#help command ----------------------------------------------------------------------------------------------------- help command
    @bot.tree.command(name="kv_help", description="Shows all available commands and their usage")
    async def help(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_help' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        embed = discord.Embed(
            title="🤖 Komivoyager Help Page",
            description="Here are all available commands and important informations:",
            color=0x00ff00
        )

        # General Commands
        embed.add_field(
            name="🌟 General Commands",
            value=(
                "`/kv_hello` - Greets you back!\n"
                "`/kv_echo <message>` - Replies with your message\n"
                "`/kv_demokracja <question>` - Creates a quick poll with 👍/👎 reactions\n"
                "`/kv_help` - Shows this help message"
            ),
            inline=False
        )

        # Admin Commands
        embed.add_field(
            name="🛡️ Admin Commands",
            value=(
                "`/kv_clearchat <1-100>` - Delete messages from chat (Admin/Owner only)\n"
            ),
            inline=False
        )
        
        # Voice Commands
        embed.add_field(
            name="🎵 Voice Commands",
            value=(
                "`/kv_join` - Joins your current voice channel\n"
                "`/kv_leave` - Leaves his current voice channel\n"
            ),
            inline=False
        )
        
        # Transcription Commands
        embed.add_field(
            name="📝 Transcription Commands",
            value=(
                "`/kv_transcript on` - Enable voice transcription\n"
                "`/kv_transcript off` - Disable voice transcription\n"
                "`/kv_transcript status` - Check transcription status\n"
                "`/kv_transcript get` - Choose one of saved transcripts and get it as attachment\n"
            ),
            inline=False
        )
        
        # Music Commands
        embed.add_field(
            name="🎵 Music Commands",
            value=(
                "`/kv_play` - Starts playing from queue if queue is not empty\n"
                "`/kv_play <query>` - Play song instantly (stops current music)\n"
                "`/kv_enqueue <query>` - Add song to queue\n"
                "`/kv_clearqueue` - Clear the music queue\n"
                "`/kv_queue` - Show current queue\n"
                "`/kv_nowplaying` - Show current song\n"
                "`/kv_skip` - Skip current sound/music\n"
                "`/kv_stop` - Stop current sound/music and clear queue\n"
                "`/kv_volume <0-100>` - Set music volume\n"
                "`/kv_background <0-100>` - Set background music volume\n"
            ),
            inline=False
        )
        
        # Additional Info
        embed.add_field(
            name="ℹ️ Additional Info",
            value=(
                "• Background music starts and loops automatically\n"
                "• Transcription supports Polish language\n"
                "• Bot disconnects when no users are in voice channel"
            ),
            inline=False
        )
        
        # Disclaimer
        embed.add_field(
            name="⚠️ Disclaimer",
            value=(
                "This bot is made for fun and intended for use on private servers\n"
                "with close friends. May contain inappropriate humor and is\n"
                "**NOT family-friendly**. Use at your own discretion."
            ),
            inline=False
        )
        
        embed.set_footer(text="Komivoyager Bot | Ready to solve your np-hard problems")
        await interaction.response.send_message(embed=embed, ephemeral=True)

#hello command ----------------------------------------------------------------------------------------------------- hello command
    @bot.tree.command(name="kv_hello", description="Greets you back!")
    async def hello(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_hello' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")

#echo command ----------------------------------------------------------------------------------------------------- echo command
    @bot.tree.command(name="kv_echo", description="Replies with your message.")
    @app_commands.describe(message="The message to echo")
    async def echo(interaction: discord.Interaction, message: str):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_echo' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with message: '{message}'")
        await interaction.response.send_message("✓", ephemeral=True, delete_after=0.1)
        await interaction.channel.send(message)

#demokracja command ----------------------------------------------------------------------------------------------------- demokracja command
    @bot.tree.command(name="kv_demokracja", description="Creates a quick poll.")
    @app_commands.describe(question="The poll question")
    async def demokracja(interaction: discord.Interaction, question: str):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_demokracja' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with question: '{question}'")
        embed = discord.Embed(title="Demokracja!", description=question, color=0x00ff00)
        poll_message = await interaction.channel.send(embed=embed)
        await poll_message.add_reaction('👍')
        await poll_message.add_reaction('👎')
        await interaction.response.send_message("Poll created!", ephemeral=True, delete_after=5)

#join command ----------------------------------------------------------------------------------------------------- join command
    @bot.tree.command(name="kv_join", description="Joins a voice channel.")
    async def join(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_join' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            voice_client = interaction.guild.voice_client
            guild_id = interaction.guild.id

            if voice_client is None:
                voice_client = await utils.connect_to_channel(channel, guild_id)
                await interaction.response.send_message(f"Joined {channel.name}!", ephemeral=True, delete_after=5)
            else:
                await voice_client.disconnect()
                voice_client = await utils.connect_to_channel(channel, guild_id)
                await interaction.response.send_message(f"Moved to {channel.name}!", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True, delete_after=5)

#leave command ----------------------------------------------------------------------------------------------------- leave command
    @bot.tree.command(name="kv_leave", description="Leaves the voice channel.")
    async def leave(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_leave' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("Disconnected from the voice channel.", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message("I am not connected to any voice channel.", ephemeral=True, delete_after=5)

#transcript command ----------------------------------------------------------------------------------------------------- transcript command
    @bot.tree.command(name="kv_transcript", description="Enable or disable voice transcription.")
    @app_commands.describe(action="on, off, status, or get")
    async def transcript(interaction: discord.Interaction, action: str):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_transcript' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with action: '{action}'")
        
        guild_id = interaction.guild.id
        
        if action.lower() == "status":            
            if voice_transcriber.is_transcribing(guild_id):
                await interaction.response.send_message("Transcription is currently enabled.", ephemeral=True, delete_after=5)
            else:
                await interaction.response.send_message("Transcription is currently disabled.", ephemeral=True, delete_after=5)
            return
        
        if action.lower() == "get":
            await interaction.response.defer(ephemeral=True)
            
            transcript_files = voice_transcriber.get_transcripts(guild_id)
            
            if not transcript_files:
                await interaction.followup.send("❌ No transcript files found for this guild.", ephemeral=True)
                return
            
            options = voice_transcriber.get_transcripts(guild_id)
            
            # Create dropdown view
            class TranscriptSelect(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)
                
                @discord.ui.select(
                    placeholder="Choose a transcript file...",
                    options=options,
                    min_values=1,
                    max_values=1
                )
                async def select_transcript(self, select_interaction: discord.Interaction, select: discord.ui.Select):
                    selected_file = select.values[0]
                    
                    discord_file = utils.get_file_as_discord_file(selected_file)
                    if discord_file is None:
                        await select_interaction.response.send_message(
                            "❌ Error reading transcript file. It may be too large or corrupted.",
                            ephemeral=True,
                            delete_after=5
                        )
                    else:
                        file_name = discord_file.filename
                        await select_interaction.response.send_message(
                            f"📄 **Transcript: {file_name}**",
                            file=discord_file,
                            ephemeral=True
                        )
                            
                        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Transcript file '{file_name}' sent to {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
                
                async def on_timeout(self):
                    # Disable all components when timeout occurs
                    for item in self.children:
                        item.disabled = True
            
            view = TranscriptSelect()
            embed = discord.Embed(
                title="📄 Available Transcripts",
                description=f"Found **{len(transcript_files)}** transcript files for this guild.\nSelect one to view:",
                color=0x00ff00
            )
            embed.set_footer(text="Selection expires in 60 seconds")
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            return

        # transcribe on/off actions
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("You must be in a voice channel.", ephemeral=True, delete_after=5)
            return
        
        voice_client = interaction.guild.voice_client
        if action.lower() == "on":
            await interaction.response.defer(ephemeral=True)
            await voice_transcriber.set_transcribing(guild_id, True)
            if voice_client:
                await voice_client.disconnect() 
            voice_client = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
            await voice_transcriber.start_recording(voice_client, guild_id)
            await interaction.followup.send("Transcription enabled.", ephemeral=True)
        elif action.lower() == "off":
            await interaction.response.defer(ephemeral=True)
            await voice_transcriber.set_transcribing(guild_id, False)
            await voice_transcriber.stop_recording(voice_client, guild_id)
            if voice_client:
                await voice_client.disconnect() 
                voice_client = await interaction.user.voice.channel.connect()
            await interaction.followup.send("Transcription disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Wrong command!\nUsage: /kv_transcript {on/off/status/get}", ephemeral=True, delete_after=15)

#play command (instant play) ----------------------------------------------------------------------------------------------------- play command
    @bot.tree.command(name="kv_play", description="Play a song instantly (stops current music)")
    @app_commands.describe(query="YouTube URL or search query (optional - leave empty to play from queue)")
    async def play(interaction: discord.Interaction, query: str = ""):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_play' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with query: '{query if query else 'empty (play from queue)'}'")
        
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True, delete_after=5)
            return
        
        voice_client = interaction.guild.voice_client
        if not voice_client:
            voice_client = await utils.connect_to_channel(interaction.user.voice.channel, interaction.guild.id)
        
        await interaction.response.defer(ephemeral=True)

        if query is None or query.strip() == "":
            title, uploader = await yt_player.play_next(voice_client, interaction.guild.id)
            if not title:
                await interaction.followup.send(f"❌ There is nothing to play.", ephemeral=True)
                return
        
        else:
            # Play instantly
            title, uploader = await yt_player.play_instantly(voice_client, interaction.guild.id, query)
            if not title:
                await interaction.followup.send(f"❌ Failed to load the '{query}'! Please check the URL or search term.")
                return
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{title}**",
            color=0x00ff00
        )
        if uploader:
            embed.add_field(name="Uploader", value=uploader, inline=True)
        await interaction.followup.send(embed=embed)

#enqueue command (add to queue) ----------------------------------------------------------------------------------------------------- enqueue command
    @bot.tree.command(name="kv_enqueue", description="Add a song to the queue")
    @app_commands.describe(query="YouTube URL or search query")
    async def enqueue(interaction: discord.Interaction, query: str):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_enqueue' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with query: '{query}'")
        
        await interaction.response.defer(ephemeral=True)
        
        # Add to queue
        title, uploader = await yt_player.add_to_queue(interaction.guild.id, query)
        if not title:
            await interaction.followup.send(f"❌ Failed to load the '{query}'! Please check the URL or search term.")
            return
        
        queue_pos = len(yt_player.get_queue(interaction.guild.id))
        embed = discord.Embed(
            title="📋 Added to Queue",
            description=f"**{title}**",
            color=0x00ff00
        )
        if uploader:
            embed.add_field(name="Uploader", value=uploader, inline=True)
        embed.add_field(name="Position", value=f"#{queue_pos}", inline=True)
        await interaction.followup.send(embed=embed)

#clearqueue command ----------------------------------------------------------------------------------------------------- clearqueue command
    @bot.tree.command(name="kv_clearqueue", description="Clear the music queue")
    async def clearqueue(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_clearqueue' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        guild_id = interaction.guild.id
        queue_list = yt_player.get_queue(guild_id)
        
        if queue_list:
            queue_length = len(queue_list)
            yt_player.clear_queue(guild_id)
            embed = discord.Embed(
                title="🗑️ Queue Cleared",
                description=f"Removed **{queue_length}** songs from the queue",
                color=0xff9900
            )
            await interaction.response.send_message(embed=embed, delete_after=5)
        else:
            await interaction.response.send_message("❌ Queue is already empty!", ephemeral=True, delete_after=5)

#queue command ----------------------------------------------------------------------------------------------------- queue command
    @bot.tree.command(name="kv_queue", description="Show the current music queue")
    async def queue(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_queue' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        guild_id = interaction.guild.id
        current_title, current_uploader = yt_player.get_current_song_info(guild_id)
        queue_list = yt_player.get_queue(guild_id)
        
        embed = discord.Embed(title="🎵 Music Queue", color=0x00ff00)
        
        if current_title:
            now_playing = f"**{current_title}**"
            if current_uploader:
                now_playing += f"\nby {current_uploader}"
            embed.add_field(name="🎶 Now Playing", value=now_playing, inline=False)
        
        if queue_list:
            queue_text = ""
            for i, source in enumerate(queue_list[:10]):
                queue_text += f"{i+1}. **{source.title}**"
                if source.uploader:
                    queue_text += f" - {source.uploader}"
                queue_text += "\n"
            
            if len(queue_list) > 10:
                queue_text += f"... and {len(queue_list) - 10} more songs"
            
            embed.add_field(name="📋 Up Next", value=queue_text, inline=False)
        else:
            embed.add_field(name="📋 Queue", value="Empty", inline=False)
        
        current_volume = int(yt_player.get_volume(guild_id) * 100)
        embed.set_footer(text=f"Volume: {current_volume}% | Use /kv_volume to change")
        
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=min(30, max(5, len(queue_list) * 3)))

#nowplaying command ----------------------------------------------------------------------------------------------------- nowplaying command
    @bot.tree.command(name="kv_nowplaying", description="Show what's currently playing")
    async def nowplaying(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_nowplaying' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        guild_id = interaction.guild.id
        current_title, current_uploader = yt_player.get_current_song_info(guild_id)
        
        if current_title:
            embed = discord.Embed(
                title="🎶 Now Playing",
                description=f"**{current_title}**",
                color=0x00ff00
            )
            if current_uploader:
                embed.add_field(name="Uploader", value=current_uploader, inline=True)
            
            volume = int(yt_player.get_volume(guild_id) * 100)
            embed.add_field(name="Volume", value=f"{volume}%", inline=True)
            
            queue_length = len(yt_player.get_queue(guild_id))
            embed.add_field(name="Queue", value=f"{queue_length} songs", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=15)
        else:
            await interaction.response.send_message("❌ Nothing is currently playing!", ephemeral=True, delete_after=5)

#skip command ----------------------------------------------------------------------------------------------------- skip command
    @bot.tree.command(name="kv_skip", description="Skip the current sound/music")
    async def skip(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_skip' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            audio_mgr.stop_audio(voice_client)
            await interaction.response.send_message("⏭️ Skipped current sound!", delete_after=5)
        else:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True, delete_after=5)

#stop command ----------------------------------------------------------------------------------------------------- stop command
    @bot.tree.command(name="kv_stop", description="Stop music and clear queue")
    async def stop_music(interaction: discord.Interaction):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_stop' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id})")
        
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            yt_player.clear_queue(interaction.guild.id)
            audio_mgr.stop_audio(voice_client)
            await interaction.response.send_message("⏹️ Stopped current sound and cleared queue!", delete_after=5)
        else:
            yt_player.clear_queue(interaction.guild.id)
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True, delete_after=5)

#volume command ----------------------------------------------------------------------------------------------------- volume command
    @bot.tree.command(name="kv_volume", description="Set music volume (0-100)")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(interaction: discord.Interaction, volume: int):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_volume' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with volume: {volume}")
        
        if not 0 <= volume <= 100:
            await interaction.response.send_message("❌ Volume must be between 0-100!", ephemeral=True, delete_after=15)
            return
        
        voice_client = interaction.guild.voice_client
        if voice_client:
            yt_player.set_volume(interaction.guild.id, volume / 100)
            await interaction.response.send_message(f"🔊 Music volume set to {volume}%", delete_after=5)
        else:
            await interaction.response.send_message("❌ Not connected to voice channel!", ephemeral=True, delete_after=15)

#background command ----------------------------------------------------------------------------------------------------- background command
    @bot.tree.command(name="kv_background", description="Set background music volume (0-100)")
    @app_commands.describe(volume="Volume level (0-100)")
    async def background(interaction: discord.Interaction, volume: int):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_background' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with volume: {volume}")
        
        if not 0 <= volume <= 100:
            await interaction.response.send_message("Volume must be between 0-100", ephemeral=True, delete_after=15)
            return
        
        scaled_volume = (volume / 100) * 2.0
        
        audio_mgr.set_background_volume(interaction.guild.id, scaled_volume)
        await interaction.response.send_message(f"Background music volume set to {volume}%", delete_after=5)

#clearchat command ----------------------------------------------------------------------------------------------------- clearchat command
    @bot.tree.command(name="kv_clearchat", description="Delete messages from chat (Admin only)")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    async def clearchat(interaction: discord.Interaction, amount: int):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_clearchat' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with amount: {amount}")
        
        # Check permissions
        if not (interaction.user.guild_permissions.administrator or 
                interaction.user.name == "adbreeker" or
                interaction.user.id == interaction.guild.owner_id):
            print(f"[WARNING - {datetime.now().strftime('%H:%M:%S')}] User {interaction.user.name} ({interaction.user.id}) tried to use kv_clearchat without permission")
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True, delete_after=5)
            return
        
        # Validate amount
        if not 1 <= amount <= 100:
            await interaction.response.send_message("❌ Amount must be between 1-100!", ephemeral=True, delete_after=15)
            return
        
        # Check bot permissions
        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.response.send_message("❌ I don't have permission to delete messages in this channel!", ephemeral=True, delete_after=5)
            return
        
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Delete messages
            deleted = await interaction.channel.purge(limit=amount)
            
            print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Successfully deleted {len(deleted)} messages in channel {interaction.channel.name} ({interaction.channel.id})")
            
            # Send confirmation
            embed = discord.Embed(
                title="🗑️ Messages Deleted",
                description=f"Successfully deleted **{len(deleted)}** messages",
                color=0xff4444
            )
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Failed to delete messages - Forbidden permission")
            await interaction.followup.send("❌ I don't have permission to delete messages!", ephemeral=True)
        except discord.HTTPException as e:
            print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] HTTP error during message deletion: {str(e)}")
            await interaction.followup.send(f"❌ Failed to delete messages: {str(e)}", ephemeral=True)
        except Exception as e:
            print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Unexpected error during message deletion: {str(e)}")
            await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)