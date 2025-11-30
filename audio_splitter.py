"""
Audio Splitter Module
Splits long audio files into segments with optional overlap
Cross-platform (Windows, macOS, Linux)
"""
import subprocess
import os
from pathlib import Path


def get_audio_duration(audio_file):
    """
    Get duration of audio file in seconds using ffprobe

    Args:
        audio_file (str): Path to audio file

    Returns:
        float: Duration in seconds, or None if error
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass

    return None


def split_audio_file(input_file, output_dir=None, segment_length=1800, overlap=30,
                    output_format="mp3", progress_callback=None):
    """
    Split audio file into segments with overlap

    Args:
        input_file (str): Path to input audio file
        output_dir (str): Output directory (default: same as input)
        segment_length (int): Segment length in seconds (default: 1800 = 30 min)
        overlap (int): Overlap between segments in seconds (default: 30)
        output_format (str): Output format (default: "mp3")
        progress_callback (callable): Optional callback for progress updates

    Returns:
        list: List of created segment file paths

    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If ffmpeg/ffprobe not found or splitting fails
    """
    # Validate input file
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Check for ffprobe
    if not _check_ffprobe():
        raise RuntimeError("ffprobe not found. Please install FFmpeg.")

    # Get file info
    input_path = Path(input_file)
    filename = input_path.stem
    input_dir = input_path.parent

    # Set output directory
    if output_dir is None:
        output_dir = input_dir
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    if progress_callback:
        progress_callback("Getting audio duration...")

    # Get duration
    duration = get_audio_duration(input_file)
    if duration is None:
        raise RuntimeError("Could not determine audio duration")

    duration_int = int(duration)
    duration_min = duration / 60

    if progress_callback:
        progress_callback(f"Duration: {duration_min:.1f} minutes")

    # Check if splitting is needed
    if duration_int <= segment_length:
        if progress_callback:
            progress_callback("File is shorter than segment length. No splitting needed.")
        return [input_file]

    # Calculate number of segments
    segment_count = int((duration_int - overlap) / (segment_length - overlap)) + 1

    if progress_callback:
        progress_callback(f"Creating {segment_count} segments...")

    # Split the audio
    output_files = []

    for i in range(segment_count):
        # Calculate start time with overlap
        if i == 0:
            start_time = 0
        else:
            start_time = i * (segment_length - overlap)

        # Calculate duration for this segment
        if i == segment_count - 1:
            # Last segment: take everything remaining
            segment_duration = duration_int - start_time
        else:
            segment_duration = segment_length

        # Output filename
        output_file = output_dir / f"{filename}_part{i+1:02d}.{output_format}"

        if progress_callback:
            start_min = start_time / 60
            end_min = (start_time + segment_duration) / 60
            progress_callback(
                f"Creating segment {i+1}/{segment_count}: "
                f"{start_min:.1f}min - {end_min:.1f}min"
            )

        # Run ffmpeg
        cmd = [
            "ffmpeg",
            "-i", str(input_file),
            "-ss", str(start_time),
            "-t", str(segment_duration),
            "-c:a", "libmp3lame",
            "-q:a", "2",
            "-y",
            str(output_file)
        ]

        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=600  # 10 minutes max per segment
            )
            output_files.append(str(output_file))
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create segment {i+1}: {e}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Timeout while creating segment {i+1}")

    if progress_callback:
        progress_callback(f"Successfully created {len(output_files)} segments")

    return output_files


def _check_ffprobe():
    """Check if ffprobe is available"""
    try:
        subprocess.run(
            ["ffprobe", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


# Command-line interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python audio_splitter.py <input_file> [output_dir]")
        print("\nExample:")
        print("  python audio_splitter.py long_audio.mp3")
        print("  python audio_splitter.py long_audio.mp3 ./segments")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    def print_progress(msg):
        print(f"[*] {msg}")

    try:
        segments = split_audio_file(
            input_file,
            output_dir=output_dir,
            progress_callback=print_progress
        )

        print("\n✓ Splitting complete!")
        print(f"\nCreated {len(segments)} segments:")
        for segment in segments:
            print(f"  - {segment}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
