# Audio Transcription App

A cross-platform desktop application that enhances audio quality and transcribes speech to text using AI.

![macOS](https://img.shields.io/badge/macOS-10.15+-blue)
![Windows](https://img.shields.io/badge/Windows-10+-blue)
![Linux](https://img.shields.io/badge/Linux-AppImage-blue)
![Python](https://img.shields.io/badge/python-3.13+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- **Audio Playback**: Support for MP3, WAV, M4A, OGG, FLAC, and MP4 files
- **Audio Enhancement**: Clean and improve audio quality with noise removal
  - Click and keyboard noise removal
  - Multiple speaker voice profiles (male, female, mixed)
  - FFmpeg bundled with the app
- **AI Transcription**: Speech-to-text using Deepgram AI (supports Italian)
- **Audio Controls**: Play, pause, and seek through audio files
- **Export**: Save transcriptions as TXT and JSON files
- **Secure**: API keys stored locally in platform-specific config directory
- **Cross-Platform**: Available for macOS, Windows, and Linux

## Download

**[Download Latest Release](https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest)**

### Installation

**macOS:**
1. Download `AudioTranscription-macOS-FFmpeg.dmg` from the [Releases page](https://github.com/YOUR_USERNAME/YOUR_REPO/releases)
2. Open the DMG file
3. Drag **Audio Transcription** to your **Applications** folder
4. Launch from Applications
5. **First Launch**: macOS may show a security warning. Right-click the app and select "Open", then confirm.

**Windows:**
1. Download `AudioTranscription-Windows-FFmpeg.zip`
2. Extract the ZIP file
3. Run `AudioTranscription.exe`
4. **First Launch**: Windows Defender may show a warning. Click "More info" and then "Run anyway".

**Linux:**
1. Download `AudioTranscription-Linux-FFmpeg-x86_64.AppImage`
2. Make it executable: `chmod +x AudioTranscription-Linux-FFmpeg-x86_64.AppImage`
3. Run: `./AudioTranscription-Linux-FFmpeg-x86_64.AppImage`
4. **Note**: If the AppImage doesn't run, install FUSE: `sudo apt install fuse libfuse2`

## Requirements

- **macOS**: 10.15 (Catalina) or later
- **Windows**: Windows 10 or later
- **Linux**: Most modern distributions (Ubuntu 20.04+, Fedora 34+, etc.)
- **FFmpeg**: Now bundled with the app! No separate installation needed.
- **Deepgram API Key**: Required for transcription ([Get one free](https://console.deepgram.com/))

## Quick Start

1. **Launch the app**
2. **Go to Settings** and enter your Deepgram API key
   - API key is stored securely in:
     - macOS: `~/Library/Application Support/AudioTranscription/config.env`
     - Windows: `%APPDATA%/AudioTranscription/config.env`
     - Linux: `~/.config/AudioTranscription/config.env`
3. **Select an audio file** on the Audio Player tab
4. **Optional**: Click "Improve Audio Quality" to enhance the audio
5. **Click "Transcribe Audio"** to convert speech to text
6. **Save the transcription** to your desired location

## User Guide

### Audio Enhancement

The audio enhancement feature is perfect for cleaning up school lessons or recordings:

1. Select an audio file
2. Click "Improve Audio Quality"
3. Choose speaker voice type:
   - **Male**: Optimized for male voices
   - **Female**: Optimized for female voices
   - **Mixed**: For recordings with both male and female speakers
4. Customize output location (optional)
5. Click "Start Audio Enhancement"
6. Preview the enhanced audio
7. Click "Accept Enhancement" to use the cleaned audio

**Enhancement Features**:
- Click and pop removal
- Keyboard typing noise reduction (FFT denoiser)
- Rumble and low-frequency noise removal
- Echo reduction
- Speech clarity enhancement
- Audio level normalization

**Output**: High-quality MP3 files with professional audio enhancement.

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

#### Quick Build

**macOS:**
```bash
# Build without FFmpeg
./build_mac.sh

# Build with bundled FFmpeg (recommended)
./build_mac.sh --with-ffmpeg
```

**Linux:**
```bash
# Build without FFmpeg
./build_linux.sh

# Build with bundled FFmpeg (recommended)
./build_linux.sh --with-ffmpeg
```

**Windows:**
Use GitHub Actions for Windows builds (requires Windows environment)

## Creating Releases

The project uses GitHub Actions for automated multi-platform releases.

### Automatic Release

```bash
# Update version in pyproject.toml and AudioTranscription.spec
# Commit and create a tag
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will automatically:
# - Build for macOS (DMG + ZIP with FFmpeg)
# - Build for Windows (ZIP with FFmpeg)
# - Build for Linux (AppImage + tarball with FFmpeg)
# - Publish release with all assets
```

See [RELEASE_GUIDE.md](RELEASE_GUIDE.md) for complete release instructions.

## Project Structure

```
speech2text/
├── main.py                 # Main Qt application
├── clean_audio.py          # Audio enhancement module
├── deepgram_utils.py       # Transcription utilities
├── config_utils.py         # Configuration management
├── AudioTranscription.spec # PyInstaller configuration
├── build_mac.sh           # macOS build script
├── build_linux.sh         # Linux build script
├── download_ffmpeg.sh     # FFmpeg download script
└── .github/
    └── workflows/
        └── build-release.yml  # Multi-platform automated builds
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
- Icon: "speech-to-text" from [Google Material Symbols](https://fonts.google.com/icons) (material-symbols-light)
- Built with assistance from [Claude Code](https://claude.ai/claude-code) by Anthropic

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/YOUR_REPO/discussions)

## Roadmap

- [x] Windows support
- [x] Linux support
- [x] Click and keyboard noise removal
- [x] Multiple speaker voice profiles
- [ ] Additional language support
- [ ] Batch processing
- [ ] Real-time transcription
- [ ] Speaker diarization
- [ ] Custom audio enhancement profiles

---

Made with ❤️ for better audio transcription
