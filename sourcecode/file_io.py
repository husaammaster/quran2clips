import ffmpeg
from pydub import AudioSegment
import logging
import os
from pathlib import Path
from typing import Dict

from processflow import postprocess_clip, postprocess_file
from split_concat import get_sura_range
from utils import load_quran_numbers


# read the json file for sura names
script_dir = Path(__file__).parent  # Get the directory of the current script
csv_path = script_dir / "quran_numbers.csv"
NUM_TO_SURA = load_quran_numbers(csv_path)

def save_clips_no_concat(audio: AudioSegment, 
    reciter_name: str, 
    sura_num: int, 
    clip_length_ms: int, 
    overlap_ms: int, 
    output_dir: Path,
    fade_ms: int, 
    metadata: Dict[str, str], 
    speedup_factor:float,
    clip_folder_prefix: str) -> None:
    """
    Saves audio clips of a specified length with overlapping intervals from a combined audio segment.

    Args:
        audio (AudioSegment): The combined audio segment.
        clip_length_ms (int): Length of each clip in milliseconds.
        overlap_ms (int): Overlap between consecutive clips in milliseconds.
        output_dir (Path): Directory where the output clips will be saved.
        sura_start_times (Dict[str, int]): Dictionary of sura start times in milliseconds.
        input_dir (Path): Directory where the sura MP3 files are located.
        fade_ms (int): The duration of the fade in and fade out effect in milliseconds.
        metadata (Dict[str, str]): A dictionary containing metadata parameters.

    Returns:
        None
    """
    start = 0
    clip_num = 1

    while start < len(audio):
        end = start + clip_length_ms
        audio_clip = audio[start:end]
        audio_clip = postprocess_clip(audio_clip, fade_ms / 1000.0)

        reciter_str = "REC-" + reciter_name.replace(' ', '-')
        sura_str = f"SUR{sura_num:03d}"
        speedup_factor_str = f"SPD{speedup_factor:.2f}"
        clip_str = f"CLP{clip_num:03d}-{clip_folder_prefix.replace('_', '')}"

        filename = "_".join([reciter_str, sura_str, speedup_factor_str, clip_str]) + ".mp3"
        # results in REC-Abdel-Fattah_SUR001_SPD1.00_CLP001.mp3

        temp_path = output_dir / f"temp_{filename}"

        audio_clip.export(temp_path, format="mp3")
        output_path = output_dir / filename
        ffmpeg.input(str(temp_path)).output(str(output_path), codec='mp3', audio_bitrate='128k').run(overwrite_output=True)
        os.remove(temp_path)

        if metadata is None:
            metadata = {}
        metadata["album"] = f"Speed {speedup_factor:.2f}x"
        metadata["artist"] = reciter_name
        metadata["genre"] = "Quran" + " " + clip_folder_prefix.replace('_', '')
        sura_name = NUM_TO_SURA[sura_num]
        metadata["title"] = f"{sura_name} - C{clip_num:03d} S{speedup_factor:.2f}"
        postprocess_file(output_path, metadata)

        start = end - overlap_ms
        clip_num += 1


def save_clips(audio: AudioSegment, clip_length_ms: int, overlap_ms: int, output_dir: Path, sura_start_times: Dict[str, int], input_dir: Path, fade_duration: int, metadata: Dict[str, str], speedup_factor:float) -> None:
    """
    Saves audio clips of a specified length with overlapping intervals from a combined audio segment.

    Args:
        audio (AudioSegment): The combined audio segment.
        clip_length_ms (int): Length of each clip in milliseconds.
        overlap_ms (int): Overlap between consecutive clips in milliseconds.
        output_dir (Path): Directory where the output clips will be saved.
        sura_start_times (Dict[str, int]): Dictionary of sura start times in milliseconds.
        input_dir (Path): Directory where the sura MP3 files are located.
        fade_duration (int): The duration of the fade in and fade out effect in milliseconds.
        metadata (Dict[str, str]): A dictionary containing metadata parameters.

    Returns:
        None
    """
    start = 0
    clip_num = 1

    while start < len(audio):
        end = start + clip_length_ms
        clip = audio[start:end]
        clip = postprocess_clip(clip, fade_duration / 1000.0)
        sura_range = get_sura_range(start, end, sura_start_times, input_dir, speedup_factor)
        sura_range_str = "_".join(sura_range) if len(sura_range) > 1 else sura_range[0]
        filename = f"sura_{sura_range_str}_c{clip_num:03d}.mp3"
        temp_path = output_dir / f"temp_{filename}"

        try:
            clip.export(temp_path, format="mp3")
            output_path = output_dir / filename
            ffmpeg.input(str(temp_path)).output(str(output_path), codec='mp3', audio_bitrate='128k').run(overwrite_output=True)
            os.remove(temp_path)
            postprocess_file(output_path, metadata)
        except Exception as e:
            logging.error(f"Error exporting clip {filename}: {e}")

        start = end - overlap_ms
        clip_num += 1