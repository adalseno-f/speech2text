import subprocess
from pathlib import Path
import shutil
import os


def check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed and available in PATH.

    Returns:
        bool: True if FFmpeg is installed, False otherwise
    """
    return shutil.which("ffmpeg") is not None


def clean_audio(input_file: str, output_file: str | None = None, sex: str = "male", progress_callback=None) -> str:
    """
    Clean an audio file by applying an FFmpeg audio enhancement chain.

    Args:
        input_file (str): Input audio file path
        output_file (str)|None: Output audio file path (default is None)
        sex (str): Sex of speaker, either "male" or "female" (default is "male")
        progress_callback (callable|None): Optional callback function called with progress messages

    Notes:
        - This function applies a high pass filter to remove rumble
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

    if sex == "female":
        cut = 110
    else:
        cut = 90
    # FFmpeg audio enhancement chain
    filters = [
        f"highpass=f={cut}",                        # remove rumble
        "lowpass=f=8000",                           # reduce harsh upper range
        "areverse, highpass=f=200, areverse",       # mild dereverb hack
        "acompressor=threshold=-25dB:ratio=4",      # compression
        "aecho=0.8:0.9:10:0.3",                     # optional: REMOVE if not needed
        "equalizer=f=300:t=h:width=200:g=-2",       # cut muddy area
        "equalizer=f=3000:t=h:width=2000:g=4",      # boost speech clarity
        "loudnorm=I=-16:TP=-1.5"                    # normalize
    ]

    if progress_callback:
        progress_callback("Applying audio filters...")

    cmd = [
        "ffmpeg",
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