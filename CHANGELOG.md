# Changelog

All notable changes to the Audio Transcription App will be documented in this file.

## [v0.1.3] - 2025-11-30

### Added
- **Voice Isolation**: Added optional voice isolation/enhancement using FFmpeg's `dialoguenhance` filter
  - New checkbox: "Enhance voice isolation (reduce background noise)"
  - Uses AI-powered dialogue enhancement to isolate voice from background noise
  - Includes dynamic speech normalization (`speechnorm`)
  - Can be used independently or combined with keyboard noise removal

- **Language Selection**: Added language dropdown for transcription
  - Support for Italian (it) and English (en)
  - Default language: Italian
  - Language code is now passed to Deepgram API instead of being hardcoded

- **Optional JSON Export**: Added checkbox to save JSON transcription file
  - New checkbox: "Save JSON (debug)" next to language selection
  - Default: unchecked (only saves TXT file)
  - JSON file useful for debugging and detailed analysis

- **Long Audio Warning & Auto-Split**: Added automatic duration check for audio files
  - Warns users if audio file is longer than 30 minutes
  - **"Split Audio" button** in warning dialog to automatically split the file
  - Cross-platform audio splitter (works on Windows, macOS, Linux)
  - Splits into ~30-minute segments with 30-second overlap
  - Background processing with progress dialog
  - Uses `ffprobe` to get accurate duration
  - Helps prevent Deepgram timeouts on very long recordings
  - New `audio_splitter.py` module for programmatic use
  - New `split_audio.sh` bash script for command-line use (Unix/Linux/macOS)

### Changed
- **Keyboard Noise Removal**: Made keyboard noise removal optional via checkbox
  - New checkbox: "Remove keyboard typing noise (aggressive filtering)"
  - Default: unchecked (uses gentle noise reduction)
  - When enabled, applies more aggressive FFT denoiser, click removal, noise gate, and tighter frequency filters
  - Gives users control over noise reduction intensity

- **Audio Enhancement Pipeline**: Updated filter chain to support conditional processing:
  1. High-pass filter (rumble removal)
  2. Keyboard noise removal (optional, aggressive)
  3. Voice isolation (optional, dialoguenhance + speechnorm)
  4. Dereverb
  5. Compression
  6. EQ
  7. Normalization

### Fixed
- **Deepgram SDK Compatibility**: Fixed import error with Deepgram SDK v5+
  - Removed unused `FileSource` import that was causing ImportError
  - Removed unsupported `timeout` parameter from `transcribe_file()` call

## [v0.1.1] - 2025-11-29

### Added
- **Mixed Speaker Voice Option**: Added "mixed" option to speaker voice dropdown for recordings containing both male and female speakers (uses 100Hz high-pass filter)
- **Click Removal**: Added `adeclick` filter to remove clicking sounds from audio (2ms threshold, 10ms window)
- **Keyboard Noise Removal**: Added FFT denoiser (`afftdn`) to remove background keyboard typing noise
- **Linux AppImage Support**: Full Linux support with AppImage deployment for easy distribution
  - AppImage includes bundled FFmpeg
  - Alternative tarball format also available
  - Automated Linux builds via GitHub Actions

### Changed
- **Audio Enhancement Pipeline**: Reordered filters to apply noise removal before other processing:
  1. Click removal
  2. FFT denoiser (keyboard typing)
  3. High-pass filter (rumble removal)
  4. Low-pass filter
  5. Dereverb
  6. Compression
  7. EQ
  8. Normalization
- Removed `aecho` filter from enhancement chain (was optional and not always needed)

### Developer Notes
- New `build_linux.sh` script for building Linux AppImage
- GitHub Actions now builds for three platforms: macOS, Windows, and Linux
- All platform builds include bundled FFmpeg by default

## [v0.2.0] - 2025-11-28

### Fixed
- **API Key Storage on macOS**: Fixed critical issue where API key was being saved to `/`.env` (root directory) which caused permission errors on macOS. Now uses the proper Application Support directory:
  - macOS: `~/Library/Application Support/AudioTranscription/config.env`
  - Windows: `%APPDATA%/AudioTranscription/config.env`
  - Linux: `~/.config/AudioTranscription/config.env`

- **FFmpeg Detection**: Improved FFmpeg detection to check common installation paths instead of relying solely on PATH:
  - macOS: `/usr/local/bin/ffmpeg`, `/opt/homebrew/bin/ffmpeg` (Apple Silicon), `/usr/bin/ffmpeg`
  - Windows: `C:\Program Files\ffmpeg\bin\ffmpeg.exe`, `C:\ffmpeg\bin\ffmpeg.exe`
  - Linux: `/usr/bin/ffmpeg`, `/usr/local/bin/ffmpeg`
  - Also checks for bundled FFmpeg in the app bundle

- **Timeout Issues**: Increased Deepgram API timeout from default to 600 seconds (10 minutes) to handle long recordings without timing out

### Added
- **FFmpeg Bundling**: Added option to bundle FFmpeg directly with the application, eliminating the need for separate installation
  - New `download_ffmpeg.sh` script to download platform-specific FFmpeg binaries
  - Updated PyInstaller spec file to include FFmpeg when present in `bin/` directory
  - Build script now supports `--with-ffmpeg` flag: `./build_mac.sh --with-ffmpeg`

- **Windows Support**: Added full Windows support via GitHub Actions
  - Windows builds now created automatically alongside macOS builds
  - Windows version includes bundled FFmpeg
  - Cross-platform configuration handling

- **Multi-Platform GitHub Actions**: Updated CI/CD workflow to build for both macOS and Windows
  - Separate build jobs for each platform
  - Both platforms bundle FFmpeg by default
  - Release artifacts now include:
    - `AudioTranscription-macOS-FFmpeg.dmg` (macOS installer with FFmpeg)
    - `AudioTranscription-macOS-FFmpeg.zip` (macOS portable with FFmpeg)
    - `AudioTranscription-Windows-FFmpeg.zip` (Windows portable with FFmpeg)

### Changed
- **Configuration Management**: Completely refactored configuration handling with new `config_utils.py` module
  - Platform-aware configuration directory selection
  - Centralized API key loading and saving
  - Better error handling and user feedback

- **Build Process**: Enhanced build scripts with FFmpeg bundling capability
  - `build_mac.sh` now supports `--with-ffmpeg` option
  - Automatic FFmpeg download and integration
  - Clear build output and status messages

- **Dependencies**: Updated hidden imports in PyInstaller spec to include `config_utils`

### Developer Notes
- All configuration now properly uses platform-specific directories
- FFmpeg binaries are gitignored (stored in `bin/` directory)
- GitHub Actions automatically builds both platforms with bundled FFmpeg
- No manual FFmpeg installation needed for end users when using official releases

## [v0.1.0] - 2025-11-27

### Initial Release
- Audio file playback (MP3, WAV, M4A, OGG, FLAC, MP4)
- Audio enhancement/cleaning for school lessons using FFmpeg
- Speech-to-text transcription using Deepgram AI
- Italian language support
- Export transcriptions as TXT and JSON
- Tab-based interface (Audio Player, Audio Enhancement, Settings)
- macOS support only
