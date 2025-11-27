# Audio Transcription App

A desktop application for macOS that enhances audio quality and transcribes speech to text using AI.

![macOS](https://img.shields.io/badge/macOS-10.15+-blue)
![Python](https://img.shields.io/badge/python-3.13+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- **Audio Playback**: Support for MP3, WAV, M4A, OGG, FLAC, and MP4 files
- **Audio Enhancement**: Clean and improve audio quality for school lessons and recordings
- **AI Transcription**: Speech-to-text using Deepgram AI (supports Italian)
- **Audio Controls**: Play, pause, and seek through audio files
- **Export**: Save transcriptions as TXT and JSON files
- **Secure**: API keys stored locally in .env file

## Download

**[Download Latest Release](https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest)**

### Installation

1. Download `AudioTranscription-macOS.dmg` from the [Releases page](https://github.com/YOUR_USERNAME/YOUR_REPO/releases)
2. Open the DMG file
3. Drag **Audio Transcription** to your **Applications** folder
4. Launch from Applications

**First Launch**: macOS may show a security warning. Right-click the app and select "Open", then confirm.

## Requirements

- **macOS**: 10.15 (Catalina) or later
- **FFmpeg**: Required for audio enhancement
  ```bash
  brew install ffmpeg
  ```
- **Deepgram API Key**: Required for transcription ([Get one free](https://console.deepgram.com/))

## Quick Start

1. **Launch the app**
2. **Go to Settings** and enter your Deepgram API key
3. **Select an audio file** on the Audio Player tab
4. **Optional**: Click "Improve Audio Quality" to enhance the audio
5. **Click "Transcribe Audio"** to convert speech to text
6. **Save the transcription** to your desired location

## User Guide

### Audio Enhancement

The audio enhancement feature is perfect for cleaning up school lessons or recordings:

1. Select an audio file
2. Click "Improve Audio Quality"
3. Choose speaker voice type (male/female)
4. Customize output location (optional)
5. Click "Start Audio Enhancement"
6. Preview the enhanced audio
7. Click "Accept Enhancement" to use the cleaned audio

**Output**: High-quality MP3 files with noise reduction and speech clarity improvements.

### Transcription

1. Ensure you have a Deepgram API key configured
2. Select an audio file (or use an enhanced version)
3. Choose transcription model:
   - `nova-3` - Latest, most accurate (recommended)
   - `nova-2` - Fast and accurate
   - `whisper-large` - Alternative model
4. Click "Transcribe Audio"
5. Choose destination folder
6. Wait for transcription to complete

**Output**:
- `.txt` file with plain text transcription
- `.json` file with detailed metadata

## Development

### Prerequisites

- Python 3.13+
- FFmpeg

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies (using uv)
uv sync

# Or using pip
pip install deepgram-sdk pyside6 python-dotenv

# Run the app
python main.py
```

### Building from Source

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build instructions.

#### Quick Build (macOS)

```bash
# Build the app
./build_mac.sh

# Create DMG installer
./create_dmg.sh
```

## Creating Releases

The project uses GitHub Actions for automated releases.

### Automatic Release

```bash
# Update version in pyproject.toml
# Commit and create a tag
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will automatically:
# - Build the macOS app
# - Create DMG installer
# - Publish release with assets
```

See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for complete release instructions.

## Project Structure

```
speech2text/
├── main.py                 # Main application
├── clean_audio.py          # Audio enhancement module
├── deepgram_utils.py       # Transcription utilities
├── AudioTranscription.spec # PyInstaller configuration
├── build_mac.sh           # Build script
├── create_dmg.sh          # DMG creation script
└── .github/
    └── workflows/
        └── build-release.yml  # Automated builds
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Deepgram](https://deepgram.com/) - AI speech-to-text API
- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python framework
- [FFmpeg](https://ffmpeg.org/) - Multimedia framework
- [PyInstaller](https://pyinstaller.org/) - Python application bundler
- Built with assistance from [Claude Code](https://claude.ai/claude-code) by Anthropic

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/YOUR_REPO/discussions)

## Roadmap

- [ ] Windows support
- [ ] Linux support
- [ ] Multiple language support
- [ ] Batch processing
- [ ] Real-time transcription
- [ ] Speaker diarization
- [ ] Custom audio profiles

---

Made with ❤️ for better audio transcription
