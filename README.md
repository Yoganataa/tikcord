# 🎬 TikCord - Discord TikTok Live Recorder Bot

A powerful Discord bot that monitors TikTok notifications and automatically records live streams with **graceful stop functionality**.

## ✨ Features

- 🔍 **Smart Monitoring** - Detects TikTok live notifications from other bots
- 📡 **Auto Forwarding** - Routes notifications to specific channels based on user mapping
- 🎬 **Live Recording** - Records TikTok live streams with high quality
- 🛑 **Graceful Stop** - Properly stops recordings without corrupting files
- 🔄 **Auto Conversion** - Converts FLV to MP4 format automatically  
- 📤 **Telegram Upload** - Optional upload to Telegram after recording
- ⚡ **Slash Commands** - Easy-to-use `/live`, `/stop`, `/status` commands
- 🛡️ **Robust Error Handling** - Comprehensive error handling and logging

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg installed on your system
- Discord Bot Token
- TikTok cookies (for bypassing restrictions)

### 1. Installation

```bash
git clone https://github.com/yoganataa/tikcord.git
cd tikcord
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**

```bash
# Using chocolatey
choco install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL:**

```bash
sudo dnf install ffmpeg
# or: sudo yum install ffmpeg
```

### 3. Configuration

1. **Environment Variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **User Mapping:**

   ```bash
   cp config/user_map.example.json config/user_map.json
   # Edit with your TikTok username -> Discord channel mappings
   ```

3. **TikTok Cookies:**

   ```bash
   cp lib/tiktok_recorder/cookies.example.json lib/tiktok_recorder/cookies.json
   # Add your TikTok sessionid_ss cookie
   ```

4. **Telegram (Optional):**

   ```bash
   cp lib/tiktok_recorder/telegram.example.json lib/tiktok_recorder/telegram.json
   # Configure if you want auto-upload to Telegram
   ```

### 4. Getting TikTok Cookies

1. Open TikTok in your browser and log in
2. Press F12 to open Developer Tools
3. Go to Application/Storage → Cookies → <https://www.tiktok.com>
4. Find the `sessionid_ss` cookie and copy its value
5. Paste it in `lib/tiktok_recorder/cookies.json`

### 5. Run the Bot

```bash
python main.py
```

## 📋 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/live <username>` | Start recording & notification | `/live @username` |
| `/stop <username>` | **Gracefully** stop recording | `/stop @username` |
| `/status` | Show active recordings | `/status` |

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
DISCORD_TOKEN=your_bot_token_here
SOURCE_BOT_ID=123456789012345678
FALLBACK_CHANNEL_ID=123456789012345678

# Optional
GUILD_ID=123456789012345678  # For faster command sync
MAIN_SERVER_ID=123456789012345678
MULTI_SERVER_ID=123,456,789  # Comma-separated
RECORDER_ENABLED=true
```

### User Mapping (config/user_map.json)

```json
{
  "tiktok_username1": "123456789012345678",
  "tiktok_username2": "987654321098765432"
}
```

## 🛑 Graceful Stop Feature

The bot implements **graceful stopping** for recordings:

1. **Signal Sent** - Stop command sends graceful stop signal
2. **Segment Finish** - Recorder finishes current segment
3. **File Conversion** - Automatically converts FLV to MP4
4. **Process Exit** - Clean process termination
5. **User Feedback** - Real-time status updates

**Benefits:**

- ✅ No corrupted recordings  
- ✅ Proper MP4 conversion
- ✅ Clean file closure
- ✅ Process cleanup

## 🏗️ Architecture

``` text
tikcord/
├── bot/                    # Discord bot core
│   ├── client.py          # Bot client setup
│   ├── commands.py        # Slash commands
│   └── events.py          # Event handlers
├── config/                # Configuration
│   ├── settings.py        # Settings loader
│   └── user_map.json      # User mappings
├── modules/               # Core modules
│   ├── forwarder.py       # Notification forwarding
│   └── recorder.py        # Recording management
├── lib/tiktok_recorder/   # Vendored recorder library
└── main.py               # Entry point
```

## 🔧 Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure code quality checks pass
6. Submit a pull request

## 🚨 Troubleshooting

### Common Issues

**1. FFmpeg not found:**

```bash
# Make sure FFmpeg is in your PATH
ffmpeg -version
```

**2. Recording fails immediately:**

- Check TikTok cookies are valid
- Verify user is actually live
- Check internet connection

**3. Graceful stop not working:**

- Wait up to 45 seconds for file conversion
- Check logs for error messages
- Restart bot if processes become stuck

**4. Bot can't find channels:**

- Verify channel IDs in .env
- Ensure bot has proper permissions
- Check bot is in the correct servers

### Logs

The bot provides detailed logging:

- ✅ Successful operations
- ⚠️ Warnings and retries  
- ❌ Errors and failures
- 🔧 Configuration details

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Support

- 📖 [Documentation](https://github.com/yoganataa/tikcord/wiki)
- 🐛 [Issues](https://github.com/yoganataa/tikcord/issues)
- 💬 [Discussions](https://github.com/yoganataa/tikcord/discussions)

## 🙏 Acknowledgments

- [TikTok Live Recorder](https://github.com/Michele0303/tiktok-live-recorder) - Core recording functionality
- [discord.py](https://discordpy.readthedocs.io/) - Discord bot framework

---

**⚠️ Disclaimer:** This bot is for educational purposes. Respect TikTok's Terms of Service and content creators' rights. Use responsibly.
