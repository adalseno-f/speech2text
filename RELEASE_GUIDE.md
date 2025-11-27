# GitHub Release Guide

This guide explains how to create and publish releases with downloadable installers on GitHub.

## Table of Contents
- [Automatic Releases (Recommended)](#automatic-releases-recommended)
- [Manual Releases](#manual-releases)
- [Release Best Practices](#release-best-practices)

---

## Automatic Releases (Recommended)

The project includes a GitHub Actions workflow that automatically builds and publishes releases.

### Setup (One-time)

1. **Push your code to GitHub**:
   ```bash
   git init  # If not already a git repo
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin master
   ```

2. **Ensure Actions are enabled**:
   - Go to your GitHub repository
   - Click **Settings** > **Actions** > **General**
   - Enable **Allow all actions and reusable workflows**

### Creating a Release

When you're ready to release a new version:

1. **Update version in `pyproject.toml`**:
   ```toml
   version = "0.2.0"  # Increment version
   ```

2. **Commit changes**:
   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.2.0"
   git push
   ```

3. **Create and push a version tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

4. **Wait for automatic build**:
   - Go to **Actions** tab on GitHub
   - Watch the build progress
   - Build takes ~10-15 minutes

5. **Check your release**:
   - Go to **Releases** tab
   - Your new release will be published with DMG and ZIP files

### What Gets Created

The workflow automatically:
- ✅ Builds the macOS app
- ✅ Creates a DMG installer
- ✅ Creates a ZIP archive
- ✅ Uploads both as release assets
- ✅ Generates release notes
- ✅ Publishes the release

---

## Manual Releases

If you prefer to build and upload manually (requires a Mac):

### 1. Build the App

```bash
# Build the application
./build_mac.sh

# Create DMG installer
./create_dmg.sh
```

You'll get:
- `AudioTranscription-macOS.dmg` (~150-200 MB)
- `AudioTranscription-macOS.zip` (~150-200 MB)

### 2. Create Release on GitHub

1. **Go to your repository** on GitHub

2. **Click "Releases"** in the right sidebar

3. **Click "Draft a new release"**

4. **Fill in the details**:
   - **Tag**: `v0.2.0` (create new tag)
   - **Target**: `master` (or your main branch)
   - **Title**: `Audio Transcription v0.2.0`
   - **Description**: See template below

5. **Upload files**:
   - Drag and drop `AudioTranscription-macOS.dmg`
   - Drag and drop `AudioTranscription-macOS.zip`

6. **Click "Publish release"**

### Release Description Template

```markdown
# Audio Transcription App v0.2.0

## Download

**For macOS users:**
- Download `AudioTranscription-macOS.dmg` (Recommended)
- Or download `AudioTranscription-macOS.zip` (Alternative)

## What's New

- ✨ Audio enhancement feature
- ✨ Support for MP4 video files
- ✨ High-quality MP3 output
- 🐛 Bug fixes and improvements

## Installation

### DMG Method (Recommended):
1. Download and open `AudioTranscription-macOS.dmg`
2. Drag **AudioTranscription.app** to your **Applications** folder
3. Eject the DMG
4. Launch from Applications

### ZIP Method:
1. Download and extract `AudioTranscription-macOS.zip`
2. Move **AudioTranscription.app** to your **Applications** folder
3. Launch from Applications

## First Launch

On first launch, macOS may show a security warning:
1. **Right-click** the app and select **Open**
2. Click **Open** in the confirmation dialog

Or go to **System Preferences > Security & Privacy** and click **Open Anyway**

## Requirements

- macOS 10.15 (Catalina) or later
- **FFmpeg** (for audio enhancement): `brew install ffmpeg`
- **Deepgram API key** (configure in Settings tab)

## Features

- 🎵 Audio file playback (MP3, WAV, M4A, OGG, FLAC, MP4)
- 🎙️ Audio enhancement/cleaning for school lessons
- 📝 Speech-to-text transcription using Deepgram AI
- 🇮🇹 Italian language support
- 💾 Export transcriptions as TXT and JSON

## Support

For issues or questions, please [open an issue](https://github.com/YOUR_USERNAME/YOUR_REPO/issues).
```

---

## Release Best Practices

### Version Numbering

Use [Semantic Versioning](https://semver.org/):
- `v1.0.0` - Major release (breaking changes)
- `v0.2.0` - Minor release (new features)
- `v0.1.1` - Patch release (bug fixes)

### Release Checklist

Before creating a release:

- [ ] Update version in `pyproject.toml`
- [ ] Test the app thoroughly
- [ ] Update documentation if needed
- [ ] Write clear release notes
- [ ] Create changelog entry
- [ ] Build and test installers
- [ ] Tag the release
- [ ] Upload assets
- [ ] Announce the release

### Testing Releases

Before publishing:

1. **Test the DMG**:
   ```bash
   open AudioTranscription-macOS.dmg
   # Drag to Applications
   # Launch and test
   ```

2. **Test the ZIP**:
   ```bash
   unzip AudioTranscription-macOS.zip
   open AudioTranscription.app
   ```

3. **Verify features**:
   - File selection works
   - Audio playback works
   - Audio enhancement works (with FFmpeg)
   - Transcription works (with API key)

### Release Frequency

- **Major releases**: When ready for production
- **Minor releases**: Every few features
- **Patch releases**: Critical bug fixes

---

## GitHub Release Assets Example

Your release page will look like this:

```
Audio Transcription v0.2.0

[Release notes appear here]

Assets:
📦 AudioTranscription-macOS.dmg        185 MB
📦 AudioTranscription-macOS.zip        178 MB
📄 Source code (zip)
📄 Source code (tar.gz)
```

Users can click on the DMG or ZIP to download directly.

---

## Troubleshooting

### Build fails on GitHub Actions

1. Check the **Actions** tab for error details
2. Common issues:
   - Python version mismatch
   - Missing dependencies
   - FFmpeg not found

### DMG creation fails

1. Use the ZIP alternative
2. Or create a simple DMG:
   ```bash
   hdiutil create -srcfolder dist/AudioTranscription.app -volname "Audio Transcription" AudioTranscription-macOS.dmg
   ```

### Release not appearing

1. Check you pushed the tag: `git push origin v0.2.0`
2. Check Actions completed successfully
3. Check repository permissions

---

## Next Steps

1. **Set up GitHub repository**
2. **Push your code**
3. **Create your first release**: `git tag v0.1.0 && git push origin v0.1.0`
4. **Share the download link** with users

Your release URL will be:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/releases
```

Users can click **Download** on the latest release to get the installer!
