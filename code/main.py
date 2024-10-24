

import logging
from pathlib import Path
from typing import Dict

from file_io import save_clips
from json_gen import create_folder_dfs, load_folder_dfs
from split_concat import concatenate_audio_files


def main(quran_data_folder: Path, desired_juz_length_minutes, clip_length_minutes, overlap_seconds, fade_seconds: float = 5.0, metadata: Dict[str, str] = None) -> None:
    """
    Main function to concatenate audio files and save clips with overlapping intervals.

    Args:
        quran_data_folder (Path): Directory where for each reciter a folder with the MP3 files is stored.
        output_dir (Path): Directory where the output clips will be saved.
        clip_length_minutes (int, optional): Length of each clip in minutes. Defaults to 5.
        overlap_seconds (int, optional): Overlap between consecutive clips in seconds. Defaults to 5.
        desired_length_minutes (int, optional): Desired total length of the combined audio in minutes. Defaults to 60.
        fade_seconds (int, optional): Duration of the fade in and fade out effect in seconds. Defaults to 2.0.
        metadata (Dict[str, str], optional): Metadata for the output files. Defaults to None.

    Returns:
        None
    """

    rec_folders = sorted([folder for folder in quran_data_folder.iterdir() if folder.is_dir()])
    

    # create_folder_dfs(rec_folders)
    sura_time_analysis_df = load_folder_dfs(rec_folders)

    # create_median_length_tracks() # in own subfolder
    # create_30min/juz versions # in own subfolder 
    # clipper with overlap and fade in/out # in own subfolder

    return


    desired_total_length_minutes = 30 * desired_juz_length_minutes
    clip_length_ms = 1000 * 60 * clip_length_minutes 
    overlap_ms = overlap_seconds * 1000

    files = sorted([file for file in quran_data_folder.iterdir() if file.suffix == '.mp3'])
    logging.info(f"Found {len(files)} MP3 files in {quran_data_folder}.")

    combined_audio, sura_start_times, speedup_factor = concatenate_audio_files(files, desired_total_length_minutes, output_dir)

    combined_audio_path = output_dir / "combined_audio.mp3"
    logging.info(f"Combined audio saved to {combined_audio_path}.")

    save_clips(combined_audio, clip_length_ms, overlap_ms, output_dir, sura_start_times, quran_data_folder, fade_seconds, metadata, speedup_factor)



if __name__ == "__main__":
    quran_data_path = Path('/Users/hm/Downloads/Quran_Recordings/')  # Directory where your MP3 files are located
    # output_directory = input_directory / 'clips'  # Directory where the output clips will be saved
    # output_directory.mkdir(parents=True, exist_ok=True)
    """
    metadata_example = {
        "album": input_directory.stem,
        "composer": input_directory.stem,
        "genre": "Quran",
        "title": "Unnamed Clip"
    }
    """
    main(
        quran_data_path, 
        clip_length_minutes=1, 
        desired_juz_length_minutes=45, 
        overlap_seconds=12.5, 
        fade_seconds=10.0, 
        metadata=None)
