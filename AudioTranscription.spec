# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Audio Transcription App
Build on macOS with: pyinstaller AudioTranscription.spec
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'deepgram',
        'deepgram_utils',
        'clean_audio',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtMultimedia',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AudioTranscription',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window on macOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AudioTranscription',
)

app = BUNDLE(
    coll,
    name='AudioTranscription.app',
    icon=None,  # Add icon path here if you have one (e.g., 'icon.icns')
    bundle_identifier='com.audiotranscription.app',
    info_plist={
        'CFBundleName': 'Audio Transcription',
        'CFBundleDisplayName': 'Audio Transcription',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHighResolutionCapable': True,
        'NSMicrophoneUsageDescription': 'This app needs access to audio files for transcription.',
    },
)
