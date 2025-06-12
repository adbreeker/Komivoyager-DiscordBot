# Komivoyager Discord Bot

A comprehensive, feature-rich Discord bot with AI-powered voice transcription, League of Legends statistics, music playback, and advanced moderation capabilities.

---

## 🚀 Features

### 🎤 **AI Voice Transcription**
- Real-time speech-to-text using **faster-whisper** with CUDA acceleration
- Automatic voice channel joining and transcription
- Configurable silence detection (0.5s timeout)
- Polish language optimization with multilingual support
- Transcript logging with daily rotation (`transcripts/Guild_ID/YYYY-MM-DD.txt`)
- Smart background noise filtering and audio enhancement

### 🎮 **League of Legends Integration**
- **Champion Analysis** (`/kv_lolchampion`) - Complete champion statistics and builds
- **Matchup Analysis** (`/kv_lolmatchup`) - Detailed counter-pick information
- Real-time data from OP.GG API with patch-specific statistics
- Comprehensive build guides: items, runes, skill orders, summoner spells
- Win rates, pick rates, and performance analytics by game length

### 🎵 **Advanced Music System**
- **YouTube Integration** - Play music directly from YouTube links or search
- **Queue Management** - Add, skip, clear, and view music queue
- **Volume Control** - Separate volume controls for music and background audio
- **Background Music** - Continuous ambient audio with smart mixing
- **Text-to-Speech** - Multi-language TTS with `pyttsx3`
- **Smart Audio Management** - Automatic switching between transcription and playback

### 🛡️ **Moderation & Utilities**
- **Message Filtering** - Automatic deletion of specific phrases (e.g., "potwierdzam")
- **Bulk Message Deletion** - Admin-only chat clearing (1-100 messages)
- **Welcome System** - Automatic DM greetings for new members
- **Interactive Polls** - Quick democracy polls with emoji reactions
- **Quick Bot Message Removal** - React with 🗑️ to any bot message to instantly delete it

### 🔧 **Technical Features**
- **Slash Commands** - Modern Discord interactions with autocomplete
- **Multi-Guild Support** - Independent settings per Discord server
- **CUDA Acceleration** - GPU-accelerated AI processing
- **Async Architecture** - Non-blocking operations for optimal performance
- **Comprehensive Logging** - Detailed console and file logging

---

## 📋 Commands

### General Commands
- `/kv_help` - Display all available commands
- `/kv_hello` - Friendly greeting
- `/kv_echo <message>` - Echo your message
- `/kv_demokracja <question>` - Create a poll with 👍/👎 reactions

### Voice & Transcription
- `/kv_join` - Join your current voice channel
- `/kv_leave` - Leave the voice channel
- `/kv_transcript <action>` - Control transcription (on/off/status/get)

### Music Commands
- `/kv_play <query>` - Play music instantly (stops current track)
- `/kv_enqueue <query>` - Add song to queue
- `/kv_queue` - Show current music queue
- `/kv_nowplaying` - Display currently playing track
- `/kv_skip` - Skip current track
- `/kv_stop` - Stop music and clear queue
- `/kv_clearqueue` - Clear the music queue
- `/kv_volume <0-100>` - Set music volume
- `/kv_background <0-100>` - Set background music volume

### League of Legends
- `/kv_lolchampion <champion> <lane>` - Complete champion analysis
- `/kv_lolmatchup <champion> <lane>` - Matchup and counter information
  - **Lanes:** top, jungle, mid, adc, support
  - **Special:** Taric users get a special message 😉

### Moderation (Admin Only)
- `/kv_clearchat <amount>` - Delete 1-100 messages from current channel

---

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.11+** (recommended for PyTorch compatibility)
- **NVIDIA GPU** with CUDA support (optional but recommended for transcription)
- **Discord Bot Token** ([Create one here](https://discord.com/developers/applications))
- **FFmpeg** (automatically handled by imageio-ffmpeg)

### Installation Steps

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/yourusername/Komivoyager-DiscordBot.git
   cd Komivoyager-DiscordBot
   ```

2. **Create and activate virtual environment:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

5. **Run the bot:**
   ```powershell
   python main.py
   ```

### GPU Setup (Optional)
The bot automatically detects CUDA availability and will use GPU acceleration for faster transcription. No additional configuration needed if you have NVIDIA drivers and CUDA toolkit installed.

---

## 📁 Project Structure

```
Komivoyager-DiscordBot/
├── main.py                     # Bot entry point and initialization
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (create this)
├── discord.log                # Bot activity logs
├── scrapped.json              # LoL API data cache
├── components/                # Core bot modules
│   ├── bot_commands.py        # All slash commands
│   ├── bot_events.py          # Event handlers (joins, messages, etc.)
│   ├── voice_transcriber.py   # AI transcription engine
│   ├── audio_manager.py       # Audio playback coordination
│   ├── youtube_player.py      # YouTube integration
│   ├── opgg_api.py           # League of Legends statistics
│   └── utilis.py             # Utility functions
├── assets/sounds/             # Audio files for background music
└── transcripts/               # Voice transcription logs
    └── Guild_{ID}/           # Per-server transcript storage
        ├── 2025-06-01.txt   # Daily transcript files
        └── ...
```

---

## ⚙️ Configuration

### Voice Transcription Settings
Located in `components/voice_transcriber.py`:
- **Model Size:** `turbo` (default), `tiny`, `base`, `small`, `medium`, `large`
- **Silence Timeout:** `0.5` seconds (configurable)
- **Device:** Auto-detects CUDA or falls back to CPU
- **Language:** Optimized for Polish, supports multilingual detection

### Audio Quality Settings
Located in `components/audio_manager.py`:
- **Background Music Volume:** Default 0%
- **Music Volume:** Default 50%
- **Audio Processing:** Wiener filtering for noise reduction

---

## 🔍 Advanced Features

### AI-Powered Transcription
- **Real-time Processing:** Transcribes speech as users talk
- **Smart Buffering:** Accumulates audio until silence is detected
- **Quality Enhancement:** Noise reduction and audio filtering
- **Multi-user Support:** Simultaneous transcription for all voice participants
- **Automatic Logging:** Saves daily transcripts with timestamps

### League of Legends Integration
- **Live Data:** Real-time statistics from OP.GG
- **Comprehensive Analysis:** Win rates, builds, matchups, trends
- **Multiple Formats:** Both quick overview and detailed analysis
- **Patch Support:** Historical data across different game versions
- **Smart Formatting:** Discord embed optimization for readability

### Music System Architecture
- **Multi-source Audio:** YouTube, local files, TTS, background music
- **Smart Mixing:** Automatic volume balancing during transcription
- **Queue Management:** Advanced playlist functionality
- **Format Support:** MP3, MP4, WebM, and most audio formats via FFmpeg

---

## 🚨 Requirements & Dependencies

### Core Dependencies
- **discord.py** - Discord API wrapper with voice support
- **faster-whisper** - AI transcription engine (SYSTRAN)
- **torch + torchaudio** - PyTorch with CUDA support
- **yt-dlp** - YouTube media extraction
- **scipy + numpy** - Audio processing and filtering

### System Requirements
- **RAM:** 4GB+ (8GB+ recommended for AI transcription)
- **Storage:** 2GB+ (for AI models and transcripts)
- **Network:** Stable internet for Discord and YouTube streaming
- **GPU:** NVIDIA GPU with 4GB+ VRAM (optional but recommended)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🐛 Troubleshooting

### Common Issues

**CUDA Not Detected:**
```
- Ensure NVIDIA drivers are installed
- Install CUDA Toolkit 12.4
- Restart the application
```

**Voice Transcription Not Working:**
```
- Check microphone permissions
- Verify bot has "Use Voice Activity" permission
- Ensure sufficient RAM/VRAM available
```

**YouTube Playback Issues:**
```
- Update yt-dlp: pip install --upgrade yt-dlp
- Check internet connection
- Verify FFmpeg installation
```

**Permission Errors:**
```
- Ensure bot has Administrator permissions
- Check channel-specific permissions
- Verify bot role hierarchy
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

> **This bot was created for use on private servers among friends.**  
> It may include inside jokes, references, or features that are sometimes sensitive, inappropriate, or not suitable for all audiences.  
> **Use at your own discretion.**

The bot processes voice data for transcription purposes. Ensure compliance with your local privacy laws and Discord's Terms of Service when using voice transcription features.

---

## 🙏 Credits & Acknowledgments

### Core Technologies
- **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)** - SYSTRAN's optimized Whisper implementation
- **[discord.py](https://github.com/Rapptz/discord.py)** - Discord API wrapper by Rapptz
- **[discord-ext-voice-recv](https://github.com/imayhaveborkedit/discord-ext-voice-recv)** - Voice receive extension
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - YouTube media downloader
- **[PyTorch](https://pytorch.org/)** - Machine learning framework

### Special Thanks
- **OpenAI** - Original Whisper model
- **SYSTRAN** - Faster Whisper optimization
- **OP.GG** - League of Legends statistics API
- **Discord Community** - Various libraries and extensions

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/Komivoyager-DiscordBot/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/Komivoyager-DiscordBot/discussions)

---

**Made with ❤️ for the Discord community**