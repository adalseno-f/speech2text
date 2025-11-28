#!/bin/bash
# Build script for Linux
# Creates an AppImage for easy distribution
#
# Usage:
#   ./build_linux.sh              # Build without bundled FFmpeg
#   ./build_linux.sh --with-ffmpeg # Build with bundled FFmpeg

set -e  # Exit on error

echo "=== Audio Transcription App - Linux Build Script ==="
echo ""

# Parse command line arguments
BUNDLE_FFMPEG=false
if [[ "$1" == "--with-ffmpeg" ]]; then
    BUNDLE_FFMPEG=true
    echo "🎬 FFmpeg bundling enabled"
    echo ""
fi

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: This script is designed for Linux."
    echo "   You are running on: $OSTYPE"
    echo "   The build may not work correctly."
    echo ""
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.13 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Handle FFmpeg bundling
if [ "$BUNDLE_FFMPEG" = true ]; then
    echo ""
    echo "📥 Downloading FFmpeg for bundling..."
    ./download_ffmpeg.sh

    if [ -f "bin/ffmpeg" ]; then
        echo "✓ FFmpeg downloaded and ready for bundling"
    else
        echo "❌ Failed to download FFmpeg"
        exit 1
    fi
else
    # Check if FFmpeg is installed on system
    if ! command -v ffmpeg &> /dev/null; then
        echo "⚠️  FFmpeg is not installed and not being bundled."
        echo "   Install it with: sudo apt install ffmpeg"
        echo "   Or rebuild with: ./build_linux.sh --with-ffmpeg"
        echo "   The app will work but audio enhancement will be disabled."
        echo ""
    else
        echo "✓ System FFmpeg found: $(ffmpeg -version | head -n1)"
    fi
fi

# Install/update dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r <(python3 -c "import tomllib; f=open('pyproject.toml','rb'); data=tomllib.load(f); print('\n'.join(data['project']['dependencies']))")

# Clean previous builds
echo ""
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build the app
echo ""
echo "🔨 Building Linux application..."
pyinstaller AudioTranscription.spec

# Check if build was successful
if [ -d "dist/AudioTranscription" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📱 Your app is located at: dist/AudioTranscription/"
    echo ""

    # Create AppImage if appimagetool is available
    if command -v appimagetool &> /dev/null; then
        echo "🎁 Creating AppImage..."

        # Create AppDir structure
        APP_DIR="dist/AudioTranscription.AppDir"
        mkdir -p "$APP_DIR/usr/bin"
        mkdir -p "$APP_DIR/usr/lib"
        mkdir -p "$APP_DIR/usr/share/applications"
        mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

        # Copy application files
        cp -r dist/AudioTranscription/* "$APP_DIR/usr/bin/"

        # Create desktop file
        cat > "$APP_DIR/usr/share/applications/audiotranscription.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Audio Transcription
Comment=Audio transcription and enhancement tool
Exec=AudioTranscription
Icon=audiotranscription
Categories=AudioVideo;Audio;
Terminal=false
EOF

        # Create AppRun script
        cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/AudioTranscription" "$@"
EOF
        chmod +x "$APP_DIR/AppRun"

        # Create symbolic links
        ln -sf usr/share/applications/audiotranscription.desktop "$APP_DIR/audiotranscription.desktop"

        # Build AppImage
        appimagetool "$APP_DIR" "AudioTranscription-Linux-x86_64.AppImage"

        if [ -f "AudioTranscription-Linux-x86_64.AppImage" ]; then
            echo "✅ AppImage created: AudioTranscription-Linux-x86_64.AppImage"
            chmod +x AudioTranscription-Linux-x86_64.AppImage
        fi
    else
        echo "ℹ️  appimagetool not found. Skipping AppImage creation."
        echo "   Install with: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        echo "   Then: chmod +x appimagetool-x86_64.AppImage && sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
        echo ""
        echo "   Alternatively, create a tarball:"
        cd dist
        tar -czf ../AudioTranscription-Linux-x86_64.tar.gz AudioTranscription
        cd ..
        echo "✅ Tarball created: AudioTranscription-Linux-x86_64.tar.gz"
    fi

    echo ""
    echo "To run the app:"
    if [ -f "AudioTranscription-Linux-x86_64.AppImage" ]; then
        echo "   ./AudioTranscription-Linux-x86_64.AppImage"
    else
        echo "   ./dist/AudioTranscription/AudioTranscription"
    fi
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
