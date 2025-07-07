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
import gc
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import csv
from utils import load_quran_numbers, set_mp3_title


# read the json file for sura names
script_dir = Path(__file__).parent  # Get the directory of the current script
csv_path = script_dir / "quran_numbers.csv"
NUM_TO_SURA = load_quran_numbers(csv_path)


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

                median_file_name = curr_sura_ID + "_median.mp3"
                sura_median_filep = median_folder / median_file_name
                if not sura_median_filep.exists():
                    speedup_audio_ffmpeg(
                        input_filep=fixed_filep, 
                        output_filep=sura_median_filep, 
                        speed_change=speed_change
                        )
                else: # median already exists but may have a different old median
                    # Check if the existing median file has the correct length
                    existing_median_len = float(mediainfo(sura_median_filep)['duration'])/60.0
                    input_file_len = float(mediainfo(fixed_filep)['duration'])/60.0
                    expected_median_len = input_file_len / speed_change

                    if not math.isclose(existing_median_len, expected_median_len, abs_tol=1e-5):
                        print(f" - Regenerating {sura_median_filep.name} (existing length: {existing_median_len:.2f}, expected: {expected_median_len:.2f})")
                        speedup_audio_ffmpeg(
                            input_filep=fixed_filep, 
                            output_filep=sura_median_filep, 
                            speed_change=speed_change
                            )
                    else: 
                        print(f" - Skipping {sura_median_filep.name} (already correct length: {existing_median_len:.2f})")
            else:
                raise ValueError(F"Unexpected filename: {fixed_filep} does not end with '_fixed'.")
        
        # Memory optimization after processing each reciter
        gc.collect()



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
            
            # Get original duration for metadata verification
            original_info = mediainfo(input_filep)
            original_duration = float(original_info['duration'])
            expected_duration = original_duration / speed_change
            
            # Handle extreme speed changes by chaining atempo filters
            if speed_change < 0.5:
                # For slowing down (speed_change < 0.5), chain multiple atempo filters
                # Each atempo can handle 0.5-1.0, so we need multiple steps
                remaining_factor = speed_change
                atempo_filters = []
                
                while remaining_factor < 0.5:
                    # Use the minimum supported value (0.5) for each step
                    atempo_filters.append("atempo=0.5")
                    remaining_factor /= 0.5
                
                # Add the final step
                if remaining_factor != 1.0:
                    atempo_filters.append(f"atempo={remaining_factor}")
                
                filter_chain = ",".join(atempo_filters)
            elif speed_change > 2.0:
                # For speeding up (speed_change > 2.0), chain multiple atempo filters
                # Each atempo can handle 1.0-2.0, so we need multiple steps
                remaining_factor = speed_change
                atempo_filters = []
                
                while remaining_factor > 2.0:
                    # Use the maximum supported value (2.0) for each step
                    atempo_filters.append("atempo=2.0")
                    remaining_factor /= 2.0
                
                # Add the final step
                if remaining_factor != 1.0:
                    atempo_filters.append(f"atempo={remaining_factor}")
                
                filter_chain = ",".join(atempo_filters)
            else:
                # Normal case: speed_change is within 0.5-2.0 range
                filter_chain = f"atempo={speed_change}"
            
            # Process the audio with speed change
            subprocess.run([
                'ffmpeg', '-y', '-i', str(input_filep), '-filter:a', filter_chain, '-c:a', 'mp3', '-b:a', '128k', str(output_filep)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Verify and fix metadata if needed
            actual_info = mediainfo(output_filep)
            actual_duration = float(actual_info['duration'])
            final_info = None
            
            # Check if duration metadata is correct (within 1 second tolerance)
            if not math.isclose(actual_duration, expected_duration, abs_tol=1.0):
                print(f"   Metadata duration mismatch: expected {expected_duration:.1f}s, got {actual_duration:.1f}s")
                print(f"   Fixing metadata...")
                
                # Re-encode with explicit duration metadata
                temp_output = output_filep.with_suffix('.temp.mp3')
                shutil.move(output_filep, temp_output)
                
                subprocess.run([
                    'ffmpeg', '-y', '-i', str(temp_output), '-c:a', 'mp3', '-b:a', '128k',
                    '-metadata', f'duration={expected_duration}', str(output_filep)
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                temp_output.unlink()
                
                # Verify the fix worked
                final_info = mediainfo(output_filep)
                final_duration = float(final_info['duration'])
                if math.isclose(final_duration, expected_duration, abs_tol=1.0):
                    print(f"   Metadata fixed: duration now correct at {final_duration:.1f}s")
                else:
                    print(f"   Metadata fix failed: duration still {final_duration:.1f}s")
            else:
                print(f"   Metadata correct: duration {actual_duration:.1f}s")
            
            # Set the track title using sura name from CSV
            sura_id = int(output_filep.stem[:3])
            sura_name = NUM_TO_SURA.get(sura_id, f"Sura {sura_id:03d}")
            set_mp3_title(output_filep, sura_name)
            
            # Memory optimization - free large variables (only delete if they exist)
            del original_info, actual_info
            if final_info is not None:
                del final_info
            gc.collect()
            
        else:
            # print(F"\n - Copying {input_filep.parent.stem}/{input_filep.name} to {output_filep.parent.stem}/{output_filep.name}, because speedup factor is 1.0.")
            shutil.copy(input_filep, output_filep)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error speeding up {input_filep.parent.stem}/{input_filep.stem} with ffmpeg:\n{e}")