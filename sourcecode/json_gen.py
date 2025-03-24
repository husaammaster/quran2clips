import os
import shutil
import subprocess
import csv
from typing import List
from tqdm import tqdm
import pandas as pd
import json
from pathlib import Path
from pydub.utils import mediainfo

print("json_gen.py")

ORIG_JSON_NAME = "original_mp3_metadata.json"

def load_quran_numbers(csv_path):
    """Reads quran_numbers.csv and returns a dictionary mapping numbers to Surah names."""
    quran_dict = {}
    
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 2:  # Ensure at least two elements (number, name)
                number = int(row[0].strip())  # Convert number to integer
                sura_name = row[1].strip()  # Clean up name
                quran_dict[number] = sura_name

    return quran_dict

# read the json file for sura names
script_dir = Path(__file__).parent  # Get the directory of the current script
csv_path = script_dir / "quran_numbers.csv"
NUM_TO_SURA = load_quran_numbers(csv_path)

def load_folder_dfs(quran_data_folder: Path, rec_folders: List[Path]):
    """
    Loads the ORIG_JSON_NAME dataframes for all reciters. It also creates missing json files.
    Returns sura_stat_df, rec_sura_df
    """
    print(F"\nStarting load folder dfs")
    print([rf.stem for rf in rec_folders], "\n")

    
    def load_and_concatenate(json_paths: List[Path]):
        """Loads and concatenates the ORIG_JSON_NAME jsons for all reciters. If a ORIG_JSON_NAME is missing it gets generated."""
        fixed_dfs = []
        for orig_metadata_json_path in json_paths:
            print(F"Loading and appending {ORIG_JSON_NAME} for {orig_metadata_json_path.parent.stem}:")
            try:
                fixed_dfs.append(pd.read_json(orig_metadata_json_path, lines=True))
                print(f" - {ORIG_JSON_NAME} found")
            except:
                print(f" - {ORIG_JSON_NAME} was not found")
                rec_folder = orig_metadata_json_path.parent
                create_folder_df(rec_folder)
                fixed_dfs.append(pd.read_json(orig_metadata_json_path, lines=True))

        combined_df = pd.concat(fixed_dfs, ignore_index=True)
        print(F"\nConcatenated the dataframes for all reciters in the quran data folder.")
        return combined_df

    # Function to remove duplicates
    def remove_duplicates(df: pd.DataFrame, subset_columns: List[str]):
        """Removes all duplicate lines according to the given subset of columns."""
        df_dedup = df.drop_duplicates(subset=subset_columns)
        print(f"Shape after removing duplicates: {df_dedup.shape}")
        return df_dedup


    json_paths = [rec_folder / ORIG_JSON_NAME for rec_folder in rec_folders]
    # Concatenate DataFrames
    combined_df = load_and_concatenate(json_paths)

    # Remove duplicates based on specific columns
    print(combined_df.columns)
    print(f"\nShape before removing duplicates: {combined_df.shape}")
    subset_columns = ['sura', 'artist', 'file']
    rec_sura_df = remove_duplicates(combined_df, subset_columns)
    print(F"\nShape after removing duplicates: {rec_sura_df.shape}")

    rec_sura_df.to_json(quran_data_folder / "rec_sura_df.json", orient='records', lines=True)

    # Filter to only keep suras where all reciters have an entry
    sura_counts = rec_sura_df['trk_num'].value_counts()
    common_suras = sura_counts[sura_counts == len(rec_folders)].index
    rec_sura_df = rec_sura_df[rec_sura_df['trk_num'].isin(common_suras)]
    print(F"\nFiltered dataset to only include suras present for all reciters. Remaining suras: {len(common_suras)}")
    print(F" - those suras are: {common_suras}")

    print(F"\nCalculating sum of sura lengths per reciter for common suras.")
    reciter_sums = rec_sura_df.groupby('artist')['len'].sum().to_dict()
    print(F"Sum of sura lengths per reciter for the common suras: {reciter_sums}")
    
    rec_sura_df.to_json(quran_data_folder / "filtered_rec_sura_df.json", orient='records', lines=True)
    with open(quran_data_folder / "reciter_sura_sums.json", "w") as f:
        json.dump(reciter_sums, f, indent=2)

    sura_stat_df = "not calculated because of logical issues"
    print(common_suras)
    # Out overall medial reciter is the one with the median sum of sura lengths (measured on common suras)
    # Each reciter is a factor of that median reciter that factor is the speedup factor for all suras of that reciter
    #     there is no telling how long the complete quran would take for the median reciter, because the recordings are not complete
    # Each sura is then speeded up by that factor
    #     there is no telling how long each resultigng complete quran will take.

    # after we spepedup all suras to be of median speedfactor, we can calculate the average length of each sura
    # this will result in the average length of the quran for the median reciter
    # we can then calculate the speedup factor for the median reciter to get to the desired minutes per juz
    # this factor gets applied to all spedup factors of each reciter
        
    return reciter_sums

def create_folder_df(rec_folder: Path):
    """
    Creates a dataframe which for each fixed original mp3 file contains ['artist', 'sura', 'len', 'file', 'trk_num', 'sample_rate', 'bit_rate',
       'genre', 'parent_folder'].
    """
    tracks_metadata = []

    sura_fileps = sorted([sura_filep for sura_filep in rec_folder.iterdir() if sura_filep.is_file() and sura_filep.suffix == ".mp3"])

    def correct_mp3_file(sura_filep: Path):
        """ Fixes the file-error where some mp3 files have a header where the length is corrupt. Saves the fixed files with _fixed as a suffix in separate folder. """

        fixed_folder = sura_filep.parent / "fixed"
        if sura_filep.name.find("_") == -1: # if the file does not contain "_" which signifies any suffix, so it is the original file
            tmp_fixed_path = sura_filep.with_suffix('.fixedtmp.aac')
            fixed_sura_filep = fixed_folder / (sura_filep.stem + "_fixed" + ".aac")
            
            if tmp_fixed_path.exists(): # Remove tmp_fixed_path if it exists
                os.remove(tmp_fixed_path)
    
            if not fixed_sura_filep.exists():
                print(f"\n - Fixing {sura_filep.name} from {sura_filep.parent.stem}.")
                subprocess.run(['ffmpeg', '-i', str(sura_filep), '-ar', '44100', '-c:a', 'aac', '-b:a', '128k', str(tmp_fixed_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                shutil.move(tmp_fixed_path, fixed_sura_filep)
            else:
                pass
            return fixed_sura_filep

        else:
            raise ValueError(F"File {sura_filep.name} was given as input to be fixed, but it is not an original mp3 file.")

    def get_track_length(sura_filep: Path):
        """Gets the corrected file length."""
        fixed_sura_filep = correct_mp3_file(sura_filep)
        track_info = mediainfo(fixed_sura_filep)
        track_length = float(track_info['duration'])/60.0
        return track_length

    print(F" - reading the metadata for all mp3s")
    fixed_folder = rec_folder / "fixed"
    os.makedirs(fixed_folder, exist_ok=True)
    for sura_filep in tqdm(sura_fileps, desc="Reading metadata and fixing mp3s", unit="sura"):
        if sura_filep.is_file() and sura_filep.suffix == ".mp3":
            track_info = mediainfo(sura_filep)
            track_length = get_track_length(sura_filep)
            track_number = sura_filep.stem[:3]
            parent_folder = rec_folder.name
            sura_ID = sura_filep.stem[:3]

            track_md = {
                'artist': rec_folder.name,
                'sura': NUM_TO_SURA[int(sura_ID)],
                'len': track_length,
                'file': str(sura_filep.relative_to(rec_folder)),
                'trk_num': track_number,
                'sample_rate': track_info['sample_rate'],
                'bit_rate': track_info['bit_rate'],
                'genre': "Quran",
                'parent_folder': parent_folder,
            }
            tracks_metadata.append(track_md)

    rec_metadata_df = pd.DataFrame(tracks_metadata)
    print(rec_metadata_df)

    # Save the dataframe as a JSON file in the input directory
    json_output_path = rec_folder / ORIG_JSON_NAME
    rec_metadata_df.to_json(json_output_path, orient='records', lines=True)
    print(F" - dataframe for {rec_folder.name} generated and {ORIG_JSON_NAME} stored")
