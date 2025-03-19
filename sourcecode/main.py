

import logging
from pathlib import Path
from typing import Dict
import pandas as pd

from speedster import create_median_length_tracks
from file_io import save_clips
from json_gen import load_folder_dfs
from split_concat import concatenate_audio_files


def analyze_n_generate_medians(
        quran_data_folder: Path) -> None:
    """
    A function to generate median length tracks for all reciters in the given folder.

    Args:
        quran_data_folder (Path): Directory where for each reciter a folder with the MP3 files is stored.

    Does:
        - Loads/generates metadata dataframes for all reciters.
        - Concatenates the dataframes of all reciters.
        - Saves the concatenated dataframe and an analysis of track lenghts.
        - Creates median length tracks for all reciters.
        
    Returns:
        None
    """


    print("\n"*2, " Fixing files and analyzing them ".center(80, "="), "\n"*2)
    rec_folders = sorted([folder for folder in quran_data_folder.iterdir() if folder.is_dir()])
    

    # create_folder_dfs(rec_folders)
    sura_stat_df, rec_sura_df = load_folder_dfs(quran_data_folder, rec_folders)


    def get_min_max_sura(sura_num: int, rec_sura_df: pd.DataFrame):
        """Get the min and max len reciter for the sura with number sura_num."""
        print(F"\nGet min and max len reciter for the sura with number {sura_num}")
        # Get the row with the min/maximum value in 'len' for a given trk_num
        min_row = rec_sura_df[rec_sura_df['trk_num'] == sura_num].loc[rec_sura_df[rec_sura_df['trk_num'] == sura_num]['len'].idxmin()]
        max_row = rec_sura_df[rec_sura_df['trk_num'] == sura_num].loc[rec_sura_df[rec_sura_df['trk_num'] == sura_num]['len'].idxmax()]

        print(F" - min len for sura {sura_num}:")
        print(min_row)
        print(F" - max len for sura {sura_num}:")
        print(max_row)

        return min_row, max_row
    
    # get_min_max_sura(1, rec_sura_df)
    # get_min_max_sura(2, rec_sura_df)
    # get_min_max_sura(3, rec_sura_df)

    create_median_length_tracks(rec_folders, sura_stat_df) # in own subfolder


    print("\n"*2, " Done: Generating median files for all reciters ".center(80, "="), "\n"*2)
    return

"""
def speedup_medians_n_clip(
        quran_data_folder: Path, 
        desired_juz_length_minutes, 
        clip_length_minutes, 
        overlap_seconds, 
        fade_seconds: float = 5.0, 
        metadata: Dict[str, str] = None) -> None:
    "
    Args:
        
    Does:
        - Creates 30 minute and Juz versions of the median length tracks.
        - Clips the median length tracks with overlapping intervals and fade in/out.
        - Saves the clips to the output
        - Saves the metadata for the clips to the output

    Returns:
        None
    "

    # create_30min/juz versions # in own subfolder
    # clipper with overlap and fade in/out # in own subfolder

    desired_total_length_minutes = 30 * desired_juz_length_minutes
    clip_length_ms = 1000 * 60 * clip_length_minutes 
    overlap_ms = overlap_seconds * 1000

    files = sorted([file for file in quran_data_folder.iterdir() if file.suffix == '.mp3'])
    logging.info(f"Found {len(files)} MP3 files in {quran_data_folder}.")

    combined_audio, sura_start_times, speedup_factor = concatenate_audio_files(files, desired_total_length_minutes, output_dir)

    combined_audio_path = output_dir / "combined_audio.mp3"
    logging.info(f"Combined audio saved to {combined_audio_path}.")

    save_clips(combined_audio, clip_length_ms, overlap_ms, output_dir, sura_start_times, quran_data_folder, fade_seconds, metadata, speedup_factor)
"""


if __name__ == "__main__":
    quran_data_path = Path('/Users/hm/Downloads/Quran Recordings/')
    # Directory where your MP3 files are located
    # output_directory = quran_data_path / 'clips'  # Directory where the output clips will be saved
    # output_directory.mkdir(parents=True, exist_ok=True)

    desired_juz_length_minutes = 45
    metadata = {
        "album": quran_data_path.stem,
        "composer": F"{desired_juz_length_minutes} minutes Juz",
        "genre": "Quran",
        "title": "Unnamed Clip"
    }

    analyze_n_generate_medians(
        quran_data_path,
        )
    

