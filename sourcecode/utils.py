import csv
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
from file_io import save_clips_no_concat

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

def set_mp3_title(file_path: Path, sura_name: str):
    """Set the track title in MP3 metadata using the sura name."""
    try:
        # Ensure file has an ID3 tag
        mp3 = MP3(str(file_path))
        if mp3.tags is None:
            mp3.add_tags()
            mp3.save()
        
        audio = EasyID3(str(file_path))
        audio['title'] = sura_name
        audio.save()
    except Exception as e:
        print(f"Warning: Could not set title for {file_path}: {e}") 

def split_all_median_files_to_clips(
    quran_data_folder: Path,
    clip_length_ms: int,
    overlap_ms: int,
    fade_duration: int,
    metadata: dict
):
    """
    Iterates through all reciter/median folders and splits each median file into overlapping clips.
    Uses the existing save_clips function for the actual splitting.

    Args:
        quran_data_folder (Path): Path to the main data folder containing reciter subfolders.
        clip_length_ms (int): Length of each clip in milliseconds.
        overlap_ms (int): Overlap between consecutive clips in milliseconds.
        fade_duration (int): Fade in/out duration in milliseconds.
        metadata (dict): Metadata to apply to each clip.
    """
    for reciter_folder in quran_data_folder.iterdir():
        if not reciter_folder.is_dir():
            continue
        median_folder = reciter_folder / "median"
        if not median_folder.exists():
            continue
        output_dir = reciter_folder / "clips"
        output_dir.mkdir(exist_ok=True)
        for median_file in sorted(median_folder.glob("*.mp3")):
            audio = AudioSegment.from_mp3(median_file)
            sura_num=int(median_file.stem.split("_")[0])
            sura_start_times = {sura_num: 0}
            save_clips_no_concat(
                audio=audio,
                sura_num=sura_num,
                clip_length_ms=clip_length_ms,
                overlap_ms=overlap_ms,
                output_dir=output_dir,
                sura_start_times=sura_start_times,
                input_dir=median_folder,
                fade_ms=fade_duration,
                metadata=metadata,
                speedup_factor=1.0
            ) 