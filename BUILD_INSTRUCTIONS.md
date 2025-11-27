# Building Audio Transcription App for macOS

This guide explains how to create a standalone macOS application (.app) from the Python source code.

## Prerequisites

### On macOS (Required for Building)

1. **macOS Computer**: You need a Mac to build the macOS application
2. **Python 3.13+**: Install from [python.org](https://www.python.org/downloads/macos/) or use Homebrew:
   ```bash
   brew install python@3.13
   ```

3. **FFmpeg** (Optional but recommended):
   ```bash
   brew install ffmpeg
   ```
   Required for the audio enhancement feature.

## Build Methods

### Method 1: Automated Build Script (Recommended)

1. **Transfer the project to your Mac**
   - Copy the entire project folder to your Mac computer
   - You can use git, USB drive, cloud storage, etc.

2. **Open Terminal** and navigate to the project folder:
   ```bash
   cd /path/to/speech2text
   ```

3. **Make the build script executable**:
   ```bash
   chmod +x build_mac.sh
   ```

4. **Run the build script**:
   ```bash
   ./build_mac.sh
   ```

5. **Wait for the build to complete**
   - The script will install dependencies and build the app
   - The final app will be in `dist/AudioTranscription.app`

### Method 2: Manual Build

1. **Install dependencies**:
   ```bash
   pip install deepgram-sdk pyside6 python-dotenv pyinstaller
   ```

2. **Build the application**:
   ```bash
   pyinstaller AudioTranscription.spec
   ```

3. **Find your app**:
   - The application will be created at `dist/AudioTranscription.app`

## Installing the App

1. **Open Finder** and navigate to the project folder
2. **Drag `AudioTranscription.app`** from the `dist` folder to your **Applications** folder
3. **Launch the app** from Applications or Spotlight

## First Launch

On first launch, macOS may show a security warning because the app is not signed:

1. **Control-click** (or right-click) the app icon
2. Choose **Open** from the menu
3. Click **Open** in the dialog

Alternatively:
1. Go to **System Preferences** > **Security & Privacy**
2. Click **Open Anyway** for AudioTranscription

## Troubleshooting

### "App is damaged" error
```bash
xattr -cr dist/AudioTranscription.app
```

### Missing FFmpeg
- Install FFmpeg: `brew install ffmpeg`
- Or rebuild the app after installing FFmpeg

### Python version issues
- Ensure you're using Python 3.13+
- Check: `python3 --version`

### Build errors
1. Clean previous builds:
   ```bash
   rm -rf build dist
   ```
2. Reinstall dependencies:
   ```bash
   pip install --upgrade -r requirements.txt
   ```
3. Try building again

## Cross-Platform Build (Advanced)

**Note**: Building macOS apps from Linux is not officially supported by PyInstaller. The recommended approach is to:

1. Use GitHub Actions or CI/CD for automated builds
2. Use a Mac (even a VM) for building
3. Use services like [GitHub Actions with macOS runners](https://docs.github.com/en/actions)

## App Size

The final .app bundle will be approximately 150-200 MB due to:
- Python runtime
- Qt/PySide6 frameworks
- Application dependencies

## Distribution

To distribute the app to others:

1. **Compress the app**:
   ```bash
   cd dist
   zip -r AudioTranscription.zip AudioTranscription.app
   ```

2. **Share the ZIP file** with users

3. **Important**: Users will need to:
   - Install FFmpeg for audio enhancement: `brew install ffmpeg`
   - Configure their Deepgram API key in the Settings tab
   - Allow the app in Security & Privacy settings (first launch)

## Code Signing (Optional)

For wider distribution without security warnings, you can sign the app with an Apple Developer certificate:

1. Join the [Apple Developer Program](https://developer.apple.com/programs/) ($99/year)
2. Create a Developer ID certificate
3. Sign the app:
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: YOUR NAME" dist/AudioTranscription.app
   ```

4. Notarize the app (required for macOS 10.15+):
   ```bash
   xcrun notarytool submit dist/AudioTranscription.zip --apple-id YOUR_APPLE_ID --team-id YOUR_TEAM_ID --password APP_SPECIFIC_PASSWORD
   ```

## Support

For issues or questions:
- Check the console output for error messages
- Verify all dependencies are installed
- Ensure FFmpeg is in your PATH
- Try running the Python script directly: `python3 main.py`
