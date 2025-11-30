import subprocess
from pathlib import Path
import shutil
import os
import sys


def get_ffmpeg_path() -> str | None:
    """
    Find the FFmpeg executable, checking common installation paths.

    Returns:
        str|None: Path to FFmpeg executable, or None if not found
    """
    # First, check if we have a bundled FFmpeg (in the app bundle)
    if getattr(sys, 'frozen', False):
        # Running as a bundled app
        bundle_dir = Path(sys._MEIPASS)
        bundled_ffmpeg = bundle_dir / "ffmpeg"
        if bundled_ffmpeg.exists():
            return str(bundled_ffmpeg)

    # Check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path

    # Check common installation paths on macOS
    if sys.platform == "darwin":
        common_paths = [
            "/usr/local/bin/ffmpeg",           # Homebrew Intel Mac
            "/opt/homebrew/bin/ffmpeg",        # Homebrew Apple Silicon
            "/usr/bin/ffmpeg",                 # System installation
            Path.home() / ".local/bin/ffmpeg", # User local installation
        ]

        for path in common_paths:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_file():
                return str(path_obj)

    # Check common paths on Windows
    elif sys.platform == "win32":
        common_paths = [
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            Path.home() / "ffmpeg/bin/ffmpeg.exe",
        ]

        for path in common_paths:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_file():
                return str(path_obj)

    # Check common paths on Linux
    else:
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            Path.home() / ".local/bin/ffmpeg",
        ]

        for path in common_paths:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_file():
                return str(path_obj)

    return None


def check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed and available.

    Returns:
        bool: True if FFmpeg is installed, False otherwise
    """
    return get_ffmpeg_path() is not None


def clean_audio(input_file: str, output_file: str | None = None, sex: str = "male", remove_keyboard_noise: bool = False, voice_isolation: bool = False, progress_callback=None) -> str:
    """
    Clean an audio file by applying an FFmpeg audio enhancement chain.

    Args:
        input_file (str): Input audio file path
        output_file (str)|None: Output audio file path (default is None)
        sex (str): Sex of speaker, either "male", "female", or "mixed" (default is "male")
        remove_keyboard_noise (bool): Apply aggressive filters to remove keyboard typing noise (default is False)
        voice_isolation (bool): Apply dialogue enhancement to isolate voice and reduce background noise (default is False)
        progress_callback (callable|None): Optional callback function called with progress messages

    Notes:
        - This function applies a high pass filter to remove rumble
        - It optionally removes clicks and keyboard typing noise (if remove_keyboard_noise=True)
        - It optionally applies voice isolation using dialogue enhancement (if voice_isolation=True)
        - It reduces the harsh upper range with a low pass filter
        - It applies a mild dereverb hack to reduce echo
        - It applies compression to even out the audio levels
        - It applies an equalizer to boost speech clarity
        - It normalizes the audio levels to -16 LUFS

    Returns:
        str: Path to the output file
    """


    if progress_callback:
        progress_callback("Initializing audio enhancement...")

    if output_file is None:
        p = Path(input_file)
        output_file = str(p.with_name(p.stem + "_clean" + p.suffix))

    if progress_callback:
        progress_callback(f"Processing audio file: {Path(input_file).name}")

    # Set high-pass filter frequency based on speaker voice
    if sex == "female":
        cut = 110
    elif sex == "mixed":
        cut = 100
    else:  # male
        cut = 90

    # Build FFmpeg audio enhancement chain
    filters = []

    # Stage 1: Remove low-frequency rumble
    filters.append(f"highpass=f={cut}")

    # Stage 2: Keyboard noise removal (optional, aggressive)
    if remove_keyboard_noise:
        filters.extend([
            "afftdn=nf=-20:tn=1:tr=1:om=o",        # FFT denoiser (aggressive, track noise)
            "adeclick=t=5:w=20",                    # remove clicks (aggressive for keyboard)
            "adeclip",                              # remove clipping artifacts
            "agate=threshold=-40dB:ratio=3:attack=5:release=50",  # gate out quiet noise
            "lowpass=f=7000",                       # reduce harsh upper range (more aggressive)
        ])
    else:
        # Standard noise reduction (gentle)
        filters.extend([
            "afftdn=nf=-25",                        # gentle FFT denoiser
            "lowpass=f=8000",                       # reduce harsh upper range
        ])

    # Stage 3: Voice isolation (optional)
    if voice_isolation:
        filters.extend([
            "dialoguenhance=original=0.5:enhance=2:voice=4",  # AI-powered voice isolation
            "speechnorm",                           # normalize speech levels dynamically
        ])

    # Stage 4: Dereverb and enhancement (always applied)
    filters.extend([
        "areverse,highpass=f=200,areverse",         # mild dereverb hack
        "acompressor=threshold=-25dB:ratio=4",      # compression
        "equalizer=f=300:t=h:width=200:g=-2",       # cut muddy area
        "equalizer=f=3000:t=h:width=2000:g=4",      # boost speech clarity
        "loudnorm=I=-16:TP=-1.5"                    # normalize
    ])

    if progress_callback:
        progress_callback("Applying audio filters...")

    # Get the FFmpeg executable path
    ffmpeg_exe = get_ffmpeg_path()
    if not ffmpeg_exe:
        raise RuntimeError("FFmpeg not found. Please install FFmpeg or specify its path.")

    cmd = [
        ffmpeg_exe,
        "-y",  # Overwrite output file without asking
        "-i", input_file,
        "-af", ",".join(filters),
        "-codec:a", "libmp3lame",  # Use MP3 codec
        "-q:a", "0",  # Highest quality MP3 (VBR quality 0, ~245 kbps)
        output_file
    ]

    # Suppress FFmpeg output by redirecting to DEVNULL
    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if progress_callback:
        progress_callback("Audio enhancement completed!")

    return output_file