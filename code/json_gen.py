import os
import shutil
import subprocess
import pandas as pd
import json
from pathlib import Path
from pydub.utils import mediainfo

print("json_gen.py")


def create_folder_dfs(rec_folders):
    for rec_fldr in rec_folders:
        create_folder_df(rec_fldr)

def load_folder_dfs(rec_folders):
    print(rec_folders)

    # Function to load and concatenate DataFrames
    def load_and_concatenate(json_paths):
        dfs = []
        for path in json_paths:
            try:
                dfs.append(pd.read_json(path, lines=True))
            except:
                create_folder_df(path.parent)
                dfs.append(pd.read_json(path, lines=True))

        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"Shape before removing duplicates: {combined_df.shape}")
        print(combined_df)
        return combined_df

    # Function to remove duplicates
    def remove_duplicates(df, subset_columns):
        print(df.columns)
        df_dedup = df.drop_duplicates(subset=subset_columns)
        print(f"Shape after removing duplicates: {df_dedup.shape}")
        print(df_dedup)
        return df_dedup


    json_paths = [folder / "mp3_metadata.json" for folder in rec_folders]
    # Concatenate DataFrames
    combined_df = load_and_concatenate(json_paths)

    # Remove duplicates based on specific columns
    subset_columns = ['sura', 'artist', 'file']
    final_df = remove_duplicates(combined_df, subset_columns)
    print(final_df)

    grouped_df = final_df.groupby('trk_num')['len'].agg(['min', 'mean', 'median', 'max', 'std'])
    print(grouped_df)


    min_max_sura_num = 67
    if min_max_sura_num > 0:
        # Get the row with the min/maximum value in 'len' for a given trk_num
        min_row = final_df[final_df['trk_num'] == min_max_sura_num].loc[final_df[final_df['trk_num'] == min_max_sura_num]['len'].idxmin()]
        max_row = final_df[final_df['trk_num'] == min_max_sura_num].loc[final_df[final_df['trk_num'] == min_max_sura_num]['len'].idxmax()]

        print("min al-mulk")
        print(min_row)
        print("max al-mulk")
        print(max_row)
        
    return final_df

def create_folder_df(input_dir: Path):
    """
    Creates a dataframe which for each mp3 file contains the parent folder name, filename (rel), track length, 3 digit track number (extracted from the filename) and audio encoding.
    """
    data = []

    files = sorted([file for file in input_dir.iterdir() if file.is_file() and file.suffix == ".mp3"])

    def correct_mp3_file(file_path: Path):
        fixed_folder = file_path.parent / "fixed"
        os.makedirs(fixed_folder, exist_ok=True)
        """ Fixes the error where some mp3 files have a header where the length is corrupt. Saves the original files with _old as a suffix. """
        if file_path.name.find("_") == -1:
            fixed_path = file_path.with_suffix('.fixedtmp.mp3')
            subprocess.run(['ffmpeg', '-i', str(file_path), '-c:a', 'copy', '-write_xing', '0', str(fixed_path)])
            shutil.move(fixed_path, fixed_folder / (file_path.stem + "_fixed" + ".mp3"))

    def get_track_length(file):
        correct_mp3_file(file)
        track_info = mediainfo(file)
        track_length = float(track_info['duration'])/60.0
        return track_length

    for file in files:
        if file.is_file() and file.suffix == ".mp3":
            track_info = mediainfo(file)
            #print(json.dumps(track_info, indent=2))
            #track_length = float(track_info['duration'])
            track_length = get_track_length(file)
            track_number = file.stem[:3]
            parent_folder = input_dir.name

            data.append({
                'artist': track_info['TAG']['artist'],
                'sura': track_info['TAG']['title'],
                'len': track_length,
                'file': str(file.relative_to(input_dir)),
                'trk_num': track_number,
                'sample_rate': track_info['sample_rate'],
                'bit_rate': track_info['bit_rate'],
                'genre': track_info['TAG']['genre'],
                'parent_folder': parent_folder,
            })

    df = pd.DataFrame(data)
    print(df)

    # Save the dataframe as a JSON file in the input directory
    json_output_path = input_dir / 'mp3_metadata.json'
    df.to_json(json_output_path, orient='records', lines=True)

    return df
