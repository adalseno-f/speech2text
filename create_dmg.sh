#!/bin/bash
# Create DMG installer for macOS
# Run this script after building the app with build_mac.sh

set -e  # Exit on error

echo "=== Audio Transcription App - DMG Creation Script ==="
echo ""

# Check if app exists
if [ ! -d "dist/AudioTranscription.app" ]; then
    echo "❌ AudioTranscription.app not found in dist/ folder"
    echo "   Please run ./build_mac.sh first to build the app"
    exit 1
fi

echo "✓ Found AudioTranscription.app"

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "📦 Installing create-dmg..."
    brew install create-dmg
fi

# Clean previous DMG
rm -f AudioTranscription-macOS.dmg

echo ""
echo "🔨 Creating DMG installer..."

# Create DMG with nice UI
create-dmg \
    --volname "Audio Transcription" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "AudioTranscription.app" 200 190 \
    --hide-extension "AudioTranscription.app" \
    --app-drop-link 600 185 \
    --no-internet-enable \
    "AudioTranscription-macOS.dmg" \
    "dist/AudioTranscription.app" 2>/dev/null || {

    # Fallback: Create simple DMG if create-dmg fails
    echo "⚠️  Fancy DMG creation failed, creating simple DMG..."
    hdiutil create \
        -volname "Audio Transcription" \
        -srcfolder "dist/AudioTranscription.app" \
        -ov \
        -format UDZO \
        "AudioTranscription-macOS.dmg"
}

# Check if DMG was created
if [ -f "AudioTranscription-macOS.dmg" ]; then
    DMG_SIZE=$(du -h "AudioTranscription-macOS.dmg" | cut -f1)
    echo ""
    echo "✅ DMG installer created successfully!"
    echo ""
    echo "📦 File: AudioTranscription-macOS.dmg"
    echo "📊 Size: $DMG_SIZE"
    echo ""
    echo "To test the DMG:"
    echo "   open AudioTranscription-macOS.dmg"
    echo ""
    echo "To distribute:"
    echo "   1. Upload to GitHub Releases"
    echo "   2. Share the DMG file with users"
    echo "   3. Users can drag the app to Applications"
else
    echo ""
    echo "❌ Failed to create DMG"
    exit 1
fi

# Also create a ZIP as alternative
echo "📦 Creating ZIP archive as alternative..."
cd dist
zip -r -q ../AudioTranscription-macOS.zip AudioTranscription.app
cd ..

ZIP_SIZE=$(du -h "AudioTranscription-macOS.zip" | cut -f1)
echo "✅ ZIP archive created: AudioTranscription-macOS.zip ($ZIP_SIZE)"
echo ""
echo "You now have two distribution formats:"
echo "  • AudioTranscription-macOS.dmg (Recommended - Easy drag-to-install)"
echo "  • AudioTranscription-macOS.zip (Alternative - Direct app bundle)"
