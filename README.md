# Komivoyager-DiscordBot

A feature-rich Discord bot with Polish speech-to-text transcription, moderation, and fun commands.

---

## Features

- 🎤 **Voice Channel Transcription**  
  Automatically transcribes what users say in voice channels using [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

- 🛡️ **Moderation**  
  Customizable message filtering and moderation events.

- 👋 **Welcome Messages**  
  Greets new members with a DM.

- 💬 **Fun Commands**  
  - `@@hello` — Greets you back!
  - `@@echo <message>` — Replies with your message.
  - `@@demokracja <question>` — Creates a quick poll.

---

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/Komivoyager-DiscordBot.git
   cd Komivoyager-DiscordBot
   ```

2. **Install dependencies:**
   ```sh
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Create a `.env` file in the root directory:
     ```
     DISCORD_TOKEN=your_discord_bot_token_here
     ```

4. **Run the bot:**
   ```sh
   python main.py
   ```

---

## Voice Transcription

- The bot will join a voice channel when a user joins and start transcribing speech.
- Transcriptions are printed to the console.
- Audio is processed when a user stops speaking for 1 second (configurable).

---

## Requirements

- Python 3.8+
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [discord.py](https://github.com/Rapptz/discord.py) with voice receive extension
- numpy, scipy, python-dotenv

---

## Disclaimer

> **This bot was created for use on private servers among friends.  
> It may include inside jokes, references, or features that are sometimes sensitive, inappropriate, or not suitable for all audiences.  
> Use at your own discretion.**

---

## License

MIT License

---

## Credits

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [discord.py](https://github.com/Rapptz/discord.py)