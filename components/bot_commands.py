import discord
from discord import app_commands
import components.voice_transcriber as voice_transcriber
from discord.ext import voice_recv
import components.youtube_player as yt_player
import components.audio_manager as audio_mgr
import components.utilis as utils
from datetime import datetime
import components.opgg_api as opgg_api

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
                "`/kv_say <text> <pl/en>` - Make the bot speak text in voice channel\n"
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
                "• Bot disconnects when no users are in voice channel\n"
                "• React with 🗑️ to any bot message to instantly delete it"
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
        await interaction.response.send_message("✓", ephemeral=True, delete_after=0)
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

#say command ----------------------------------------------------------------------------------------------------- say command
    @bot.tree.command(name="kv_say", description="Make the bot speak text in voice channel")
    @app_commands.describe(text="Text to speak", language="Language (pl/en)")
    async def say(interaction: discord.Interaction, text: str, language: str):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_say' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with text: '{text[:50]}{'...' if len(text) > 50 else ''}' language: '{language}'")
        
        # Validate language
        if language.lower() not in ['pl', 'en']:
            await interaction.response.send_message("❌ Invalid language! Use 'pl' for Polish or 'en' for English.", ephemeral=True, delete_after=10)
            return
        
        # Check if bot is connected to voice
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            await interaction.response.send_message("❌ I'm not connected to a voice channel! Use `/kv_join` first.", ephemeral=True, delete_after=10)
            return
        
        # Validate text length
        if len(text) > 500:
            await interaction.response.send_message("❌ Text is too long! Maximum 500 characters allowed.", ephemeral=True, delete_after=10)
            return
        
        await audio_mgr.say_text(voice_client, text, language.lower())
        await interaction.response.send_message("✓", ephemeral=True, delete_after=0)

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
        current_title, current_uploader, current_time, duration = yt_player.get_current_song_info(guild_id)
        queue_list = yt_player.get_queue(guild_id)
        
        embed = discord.Embed(title="🎵 Music Queue", color=0x00ff00)
        
        if current_title:
            now_playing = f"**{current_title}**"
            if current_time is not None and duration:
                time_display = f"{current_time}/{duration}"
                now_playing += f"\n`{time_display}`"

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
        current_title, current_uploader, current_time, duration = yt_player.get_current_song_info(guild_id)
        
        if current_title:
            embed = discord.Embed(
                title="🎶 Now Playing",
                description=f"**{current_title}**",
                color=0x00ff00
            )

            if current_time is not None and duration:
                time_display = f"{current_time} / {duration}"
                embed.add_field(name="⏱️ Progress", value=f"`{time_display}`", inline=False)

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

#lolchampion command ----------------------------------------------------------------------------------------------------- lolchampion command
    @bot.tree.command(name="kv_lolchampion", description="Get full champion analysis from OP.GG")
    @app_commands.describe(champion="Champion name", lane="Lane (top/jungle/mid/adc/support)")
    async def lolchampion(interaction: discord.Interaction, champion: str, lane: str):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_lolchampion' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with champion: '{champion}' lane: '{lane}'")
        
        # Parse and validate inputs
        champion_formatted = champion.upper().replace(' ', '_')
        lane_formatted = lane.upper()
        
        valid_lanes = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
        if lane_formatted not in valid_lanes:
            await interaction.response.send_message(f"❌ Invalid lane! Use: {', '.join(valid_lanes).lower()}", ephemeral=True, delete_after=10)
            return
        
        await interaction.response.defer()
        
        try:
            async with opgg_api.OpGGAPI() as api:
                data = await api.get_champion_analysis(champion_formatted, lane_formatted)
                
                if 'error' in data:
                    await interaction.followup.send(f"❌ Error fetching data: {data['error']}")
                    return
                
                if 'data' not in data or 'data' not in data['data']:
                    await interaction.followup.send(f"❌ No data found for {champion} in {lane} lane")
                    return
                
                analyzer = opgg_api.ChampionAnalyzer(data)
                
                # Get all data
                basic_stats = analyzer.get_basic_stats()
                position_stats = analyzer.get_position_stats()
                game_performance = analyzer.get_game_length_performance()
                trends = analyzer.get_trends()
                summoner_spells = analyzer.get_summoner_spells()
                detailed_runes = analyzer.get_runes()
                skill_orders = analyzer.get_skill_orders()
                skill_masteries = analyzer.get_skill_masteries()
                starter_items = analyzer.get_starter_items()
                boots = analyzer.get_boots()
                core_items = analyzer.get_core_items()
                final_items = analyzer.get_final_items()
                weak_counters = analyzer.get_weak_counters()
                strong_counters = analyzer.get_strong_counters()
                
                # Create main embed
                embed = discord.Embed(
                    title=f"🏆 {basic_stats['champion']} {basic_stats['position']} Analysis",
                    color=0x00ff00
                )
                
                # 1. Header Stats
                embed.add_field(
                    name="📊 **STATISTICS**",
                    value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    inline=False
                )
                
                # 2 & 3. Core stats + Position performance (first column)
                stats_combined = (
                    f"🎯 **Win Rate:** {basic_stats['win_rate']*100:.1f}%\n"
                    f"📈 **Pick Rate:** {basic_stats['pick_rate']*100:.1f}%\n"
                    f"🚫 **Ban Rate:** {basic_stats['ban_rate']*100:.1f}%\n"
                    f"⚔️ **Average KDA:** {basic_stats['kda']:.2f}\n"
                    f"🏅 **Tier:** {basic_stats['tier']} (Rank #{basic_stats['rank']})\n"
                    f"🎮 **Games Played:** {basic_stats['games_played']:,}"
                )
                
                if position_stats:
                    stats_combined += "\n\n**Position Performance:**\n"
                    for pos in position_stats:
                        stats_combined += f"`{pos['role_rate']*100:.1f}%` **{pos['lane']}:** {pos['win_rate']*100:.1f}% WR\n"

                embed.add_field(name="📊 **Overall Champion Statistics**", value=stats_combined.strip(), inline=True)

                # 4 & 5. Game length + Trends (second column)
                analytics_text = ""
                if game_performance:
                    for perf in game_performance[:5]:
                        analytics_text += f"`{perf['game_length']}min:` {perf['win_rate']*100:.1f}% WR\n"
                
                
                if trends and trends['win_history']:
                    if analytics_text:
                        analytics_text += "\n"
                    analytics_text += f"**Recent Trends:**\n"
                    analytics_text += f"Overall: #{trends['overall_rank']} • Position: #{trends['position_rank']}\n"
                    for patch in trends['win_history'][:4]:
                        analytics_text += f"`{patch['patch']}:` {patch['win_rate']*100:.1f}% WR\n"
                
                if analytics_text:
                    embed.add_field(name="**Game Length Performance:**", value=analytics_text.strip(), inline=True)
                

                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(
                    name="🛠️ **BUILD GUIDE**",
                    value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    inline=False
                )
                
                # 6. Summoner spells + Runes (keep as they were)
                if summoner_spells:
                    spells_text = ""
                    for i, spell in enumerate(summoner_spells[:3], 1):
                        spells_text += f"`{i}.` ({spell['pick_rate']*100:.0f}%) {' + '.join(spell['spells'])} **{spell['win_rate']*100:.1f}% WR**\n"
                    embed.add_field(name="✨ Summoner Spells", value=spells_text.strip(), inline=False)
                    embed.add_field(name="\u200b", value="", inline=False)

                if detailed_runes:
                    runes_text = ""
                    for i, rune in enumerate(detailed_runes[:3], 1):
                        runes_text += f"`{i}.` ({rune['pick_rate']*100:.0f}%) **{rune['primary_page']} + {rune['secondary_page']}** **{rune['win_rate']*100:.1f}% WR**\n"
                        runes_text += f"Primary: {' → '.join(rune['primary_runes'])}\n"
                        runes_text += f"Secondary: {' + '.join(rune['secondary_runes'])}\n"
                    embed.add_field(name="🔮 Detailed Runes", value=runes_text.strip(), inline=False)
                    embed.add_field(name="\u200b", value="", inline=False)
                
                # 7. Skills (keep as they were)
                skills_combined = ""
                if skill_masteries:
                    skills_combined += "**Skill Priority:**\n"
                    for i, mastery in enumerate(skill_masteries[:2], 1):
                        skills_combined += f"`{i}.` ({mastery['pick_rate']*100:.0f}%) {' > '.join(mastery['skill_priority'])} **{mastery['win_rate']*100:.1f}% WR**\n"

                if skill_orders:
                    skills_combined += "**Skill Order:**\n"
                    for i, skill in enumerate(skill_orders[:3], 1):
                        skills_combined += f"`{i}.` ({skill['pick_rate']*100:.0f}%) {' → '.join(skill['order'])} **{skill['win_rate']*100:.1f}% WR**\n"
                
                if skills_combined:
                    embed.add_field(name="📚 Skills", value=skills_combined.strip(), inline=False)
                
                
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(
                    name="🛒 **ITEMIZATION**",
                    value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    inline=False
                )
                
                # Starting items (full width)
                if starter_items:
                    items_text = ""
                    for i, starter in enumerate(starter_items[:3], 1):
                        items = ' + '.join(starter['items'][:2])
                        items_text += f"`{i}.` ({starter['pick_rate']*100:.0f}%) {items} **{starter['win_rate']*100:.1f}% WR**\n"
                    embed.add_field(name="👶 Starting Items", value=items_text.strip(), inline=False)
                
                # Boots (full width)
                if boots:
                    boots_text = ""
                    for i, boot in enumerate(boots[:3], 1):
                        boots_text += f"`{i}.` ({boot['pick_rate']*100:.0f}%) {boot['boot']} **{boot['win_rate']*100:.1f}% WR**\n"
                    embed.add_field(name="👟 Boots", value=boots_text.strip(), inline=False)
                
                # Core items (full width)
                if core_items:
                    items_text = ""
                    for i, item in enumerate(core_items[:4], 1):
                        items_list = ' + '.join(item['items'][:3])
                        items_text += f"`{i}.` ({item['pick_rate']*100:.0f}%) {items_list} **{item['win_rate']*100:.1f}% WR**\n"
                    embed.add_field(name="⚔️ Core Items", value=items_text.strip(), inline=False)
                
                # Late items (full width)
                if final_items:
                    final_text = ""
                    for i, item in enumerate(final_items[:4], 1):
                        final_text += f"`{i}.` ({item['pick_rate']*100:.0f}%) {item['item']} **{item['win_rate']*100:.1f}% WR**\n"
                    embed.add_field(name="⏳ Late Game Items", value=final_text.strip(), inline=False)

                # 11. Matchups header
                embed.add_field(name="\u200b", value="\u200b", inline=False)
                embed.add_field(
                    name="⚔️ **MATCHUPS**",
                    value="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    inline=False
                )
                
                # 12. Counters in two columns
                if weak_counters:
                    counter_text = ""
                    for i, counter in enumerate(weak_counters[:5], 1):
                        counter_text += f"`{i}.` **{counter['champion']}** - {counter['win_rate']*100:.1f}% WR\n"
                    embed.add_field(name=f"❌ Hard Matchups", value=counter_text.strip(), inline=True)
                
                if strong_counters:
                    counter_text = ""
                    for i, counter in enumerate(strong_counters[:5], 1):
                        counter_text += f"`{i}.` **{counter['champion']}** - {counter['win_rate']*100:.1f}% WR\n"
                    embed.add_field(name=f"✅ Easy Matchups", value=counter_text.strip(), inline=True)
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error in lolchampion command: {str(e)}")
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")

#lolmatchup command ----------------------------------------------------------------------------------------------------- lolmatchup command  
    @bot.tree.command(name="kv_lolmatchup", description="Get champion matchup information (counters)")
    @app_commands.describe(champion="Champion name", lane="Lane (top/jungle/mid/adc/support)")
    async def lolmatchup(interaction: discord.Interaction, champion: str, lane: str):
        print(f"[INFO - {datetime.now().strftime('%H:%M:%S')}] Command 'kv_lolmatchup' used by {interaction.user.name} ({interaction.user.id}) in guild {interaction.guild.name} ({interaction.guild.id}) with champion: '{champion}' lane: '{lane}'")
        
        # Parse and validate inputs
        champion_formatted = champion.upper().replace(' ', '_')
        lane_formatted = lane.upper()
        
        valid_lanes = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
        if lane_formatted not in valid_lanes:
            await interaction.response.send_message(f"❌ Invalid lane! Use: {', '.join(valid_lanes).lower()}", ephemeral=True, delete_after=10)
            return
        
        await interaction.response.defer()
        
        try:
            async with opgg_api.OpGGAPI() as api:
                data = await api.get_champion_analysis(champion_formatted, lane_formatted)
                
                if 'error' in data:
                    await interaction.followup.send(f"❌ Error fetching data: {data['error']}")
                    return
                
                if 'data' not in data or 'data' not in data['data']:
                    await interaction.followup.send(f"❌ No data found for {champion} in {lane} lane")
                    return
                
                analyzer = opgg_api.ChampionAnalyzer(data)
                basic_stats = analyzer.get_basic_stats()
                
                # Get all counters
                weak_counters = analyzer.get_weak_counters()
                strong_counters = analyzer.get_strong_counters()
                
                # Create matchup embed with two columns
                embed = discord.Embed(
                    title=f"⚔️ {basic_stats['champion']} {basic_stats['position']} Matchups",
                    color=0x9932cc
                )
                
                # Special note for Taric
                if champion_formatted == 'TARIC':
                    embed.description = f"Why bother? {champion_formatted} is good in every situation 📈"
                
                if weak_counters:
                    counter_text = ""
                    for i, counter in enumerate(weak_counters, 1):
                        counter_text += f"{i:2d}. **{counter['champion']}** - {counter['win_rate']*100:.1f}% WR ({counter['games_played']:,})\n"
                        # Add extra line space after top 5
                        if i == 5 and len(weak_counters) > 5:
                            counter_text += "\n"
                    embed.add_field(name=f"❌ {basic_stats['champion']} is bad against", value=counter_text, inline=True)
                
                # Add empty field for spacing between columns
                if weak_counters and strong_counters:
                    embed.add_field(name="\u200b", value="\u200b", inline=True)
                
                if strong_counters:
                    counter_text = ""
                    for i, counter in enumerate(strong_counters, 1):
                        counter_text += f"{i:2d}. **{counter['champion']}** - {counter['win_rate']*100:.1f}% WR ({counter['games_played']:,})\n"
                        # Add extra line space after top 5
                        if i == 5 and len(strong_counters) > 5:
                            counter_text += "\n"
                    embed.add_field(name=f"✅ {basic_stats['champion']} is good against", value=counter_text, inline=True)
                
                if not weak_counters and not strong_counters:
                    embed.description = f"❌ No counter data found for {champion} in {lane} lane"
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            print(f"[ERROR - {datetime.now().strftime('%H:%M:%S')}] Error in lolmatchup command: {str(e)}")
            await interaction.followup.send(f"❌ An error occurred: {str(e)}")