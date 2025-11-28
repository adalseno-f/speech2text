#!/bin/bash

# Script to download FFmpeg static binary for bundling with the app
# This script downloads platform-specific FFmpeg binaries

set -e

echo "Downloading FFmpeg for bundling..."

# Detect platform
PLATFORM=$(uname -s)
ARCH=$(uname -m)

# Create bin directory if it doesn't exist
mkdir -p bin

if [[ "$PLATFORM" == "Darwin" ]]; then
    # macOS
    echo "Detected macOS ($ARCH)"

    if [[ "$ARCH" == "arm64" ]]; then
        # Apple Silicon
        echo "Downloading FFmpeg for Apple Silicon..."
        DOWNLOAD_URL="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
    else
        # Intel Mac
        echo "Downloading FFmpeg for Intel Mac..."
        DOWNLOAD_URL="https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
    fi

    # Download and extract
    curl -L "$DOWNLOAD_URL" -o bin/ffmpeg.zip
    unzip -o bin/ffmpeg.zip -d bin/
    rm bin/ffmpeg.zip
    chmod +x bin/ffmpeg

    echo "FFmpeg downloaded to bin/ffmpeg"
    ./bin/ffmpeg -version

elif [[ "$PLATFORM" == "Linux" ]]; then
    # Linux
    echo "Detected Linux ($ARCH)"

    if [[ "$ARCH" == "x86_64" ]]; then
        echo "Downloading FFmpeg static build..."
        DOWNLOAD_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"

        curl -L "$DOWNLOAD_URL" -o bin/ffmpeg.tar.xz
        tar -xf bin/ffmpeg.tar.xz -C bin/ --strip-components=1
        rm bin/ffmpeg.tar.xz
        chmod +x bin/ffmpeg

        echo "FFmpeg downloaded to bin/ffmpeg"
        ./bin/ffmpeg -version
    else
        echo "Architecture $ARCH not supported for automatic download"
        exit 1
    fi

elif [[ "$PLATFORM" == MINGW* ]] || [[ "$PLATFORM" == MSYS* ]] || [[ "$PLATFORM" == CYGWIN* ]]; then
    # Windows (Git Bash/MSYS2/Cygwin)
    echo "Detected Windows"
    echo "Please download FFmpeg manually from https://www.gyan.dev/ffmpeg/builds/"
    echo "Extract ffmpeg.exe to the bin/ directory"
    exit 1

else
    echo "Unsupported platform: $PLATFORM"
    exit 1
fi

echo "FFmpeg download complete!"
