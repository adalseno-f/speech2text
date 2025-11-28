#!/bin/bash
# Build script for macOS
# This script should be run on a Mac computer
#
# Usage:
#   ./build_mac.sh              # Build without bundled FFmpeg
#   ./build_mac.sh --with-ffmpeg # Build with bundled FFmpeg

set -e  # Exit on error

echo "=== Audio Transcription App - macOS Build Script ==="
echo ""

# Parse command line arguments
BUNDLE_FFMPEG=false
if [[ "$1" == "--with-ffmpeg" ]]; then
    BUNDLE_FFMPEG=true
    echo "🎬 FFmpeg bundling enabled"
    echo ""
fi

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Warning: This script is designed for macOS."
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
        echo "   Install it with: brew install ffmpeg"
        echo "   Or rebuild with: ./build_mac.sh --with-ffmpeg"
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
echo "🔨 Building macOS application..."
pyinstaller AudioTranscription.spec

# Check if build was successful
if [ -d "dist/AudioTranscription.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📱 Your app is located at: dist/AudioTranscription.app"
    echo ""
    echo "To run the app:"
    echo "   open dist/AudioTranscription.app"
    echo ""
    echo "To install the app:"
    echo "   1. Open Finder and navigate to this folder"
    echo "   2. Drag 'AudioTranscription.app' from the 'dist' folder to your Applications folder"
    echo ""
    echo "Note: On first launch, macOS may show a security warning."
    echo "      Go to System Preferences > Security & Privacy to allow the app."
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
