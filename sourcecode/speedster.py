import logging
import math
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List
from pandas import DataFrame
from pydub.utils import mediainfo
from tqdm import tqdm


def create_median_length_tracks(rec_folders: List[Path], rec_med_speedup: Dict[str, float]):
    """
    Iterates through each recitor in the rec_folders and turns the fixed tracks into median-len tracks based on the reciters speedup factor.
    Stores the generated audio files with _median suffix in own folder.
    """

    for rec_folder in rec_folders:
        median_folder = rec_folder / "median"
        fixed_folder = rec_folder / "fixed"
        os.makedirs(median_folder, exist_ok=True)

        speed_change = rec_med_speedup[rec_folder.stem]
        for fixed_filep in tqdm(sorted(fixed_folder.iterdir()), desc="Creating median suras", unit="sura"):
            if fixed_filep.stem.endswith("_fixed"):
                fixed_file_name = fixed_filep.stem # number plus "_fixed" suffix
                curr_sura_ID = str(fixed_file_name.split("_")[0])

                median_file_name = curr_sura_ID + "_median.aac"
                sura_median_filep = median_folder / median_file_name
                if not sura_median_filep.exists():
                    speedup_audio_ffmpeg(
                        input_filep=fixed_filep, 
                        output_filep=sura_median_filep, 
                        speed_change=speed_change
                        )
                else: # medial already exists but is may have a different old median
                    old_median_sura_len = float(mediainfo(fixed_filep)['duration'])/60.0
                    sura_median_len = old_median_sura_len / speed_change

                    if not math.isclose(old_median_sura_len, sura_median_len, abs_tol=1e-5):
                        
                        speed_change = rec_med_speedup[rec_folder.stem]
                        speedup_audio_ffmpeg(
                            input_filep=fixed_filep, 
                            output_filep=sura_median_filep, 
                            speed_change=speed_change
                            )
                    else: 
                        pass # because the median already exists and is correct
            else:
                raise ValueError(F"Unexpected filename: {fixed_filep} does not end with '_fixed'.")



def speedup_audio_ffmpeg(input_filep: Path, output_filep: Path, speed_change: float) -> None:
    """
    Speed up the audio file using ffmpeg.

    Args:
        input_path (Path): Path to the input audio file.
        file_output_path (Path): Path to the output audio file.
        speed_change (float): The factor by which to change the playback speed. Range 0.5 (slow down) to 100.0 (speed up).

    Returns:
        None
    """
    try:
        if not math.isclose(speed_change, 1.0, abs_tol=1e-5):
            print(F"\n - Speeding up {input_filep.parent.parent.stem}/{input_filep.parent.stem}/{input_filep.stem} with factor {speed_change:.2f}.")
            
            subprocess.run([
                'ffmpeg', '-y', '-i', str(input_filep), '-filter:a', f"atempo={speed_change}", str(output_filep)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # print(F"\n - Copying {input_filep.parent.stem}/{input_filep.name} to {output_filep.parent.stem}/{output_filep.name}, because speedup factor is 1.0.")
            shutil.copy(input_filep, output_filep)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error speeding up {input_filep.parent.stem}/{input_filep.stem} with ffmpeg:\n{e}")