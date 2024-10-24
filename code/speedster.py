import logging
import subprocess
from pathlib import Path


def speedup_audio_ffmpeg(input_path: Path, file_output_path: Path, speed_change: float) -> None:
    """
    Speed up the audio file using ffmpeg.

    Args:
        input_path (Path): Path to the input audio file.
        file_output_path (Path): Path to the output audio file.
        speed_change (float): The factor by which to change the playback speed.

    Returns:
        None
    """
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', str(input_path), '-filter:a', f"atempo={speed_change}", str(file_output_path)
        ], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error speeding up audio with ffmpeg: {e}")