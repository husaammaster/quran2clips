from pydub import AudioSegment
import os
import ffmpeg
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def concatenate_audio_files(file_list: List[Path]) -> Tuple[AudioSegment, Dict[str, int]]:
    """
    Concatenates a list of MP3 audio files into a single AudioSegment object.
    
    Args:
        file_list (List[Path]): List of file paths to the MP3 files to be concatenated.
        
    Returns:
        Tuple[AudioSegment, Dict[str, int]]: A tuple containing the concatenated AudioSegment
                                             and a dictionary with sura start times in milliseconds.
    """
    combined = AudioSegment.empty()
    sura_start_times = {}
    current_time = 0

    for file in file_list:
        sura_number = file.stem
        try:
            sura_audio = AudioSegment.from_mp3(file)
        except Exception as e:
            logging.error(f"Error loading {file}: {e}")
            continue

        combined += sura_audio
        sura_start_times[sura_number] = current_time
        current_time += len(sura_audio)
        logging.info(f"Added sura {sura_number}. Total length {current_time / 3600000:.2f} h")
    
    return combined, sura_start_times

def get_sura_length(sura_number: str, input_dir: Path) -> int:
    """
    Gets the length of a sura audio file in milliseconds.
    
    Args:
        sura_number (str): The number of the sura as a string.
        input_dir (Path): Directory where the sura MP3 files are located.
        
    Returns:
        int: Length of the sura audio file in milliseconds.
    """
    sura_file = input_dir / f"{sura_number}.mp3"
    try:
        sura_audio = AudioSegment.from_mp3(sura_file)
        return len(sura_audio)
    except Exception as e:
        logging.error(f"Error loading {sura_file}: {e}")
        return 0

def get_sura_range(start: int, end: int, sura_start_times: Dict[str, int], input_dir: Path) -> List[str]:
    """
    Determines the range of suras that overlap with a given time range.
    
    Args:
        start (int): Start time of the range in milliseconds.
        end (int): End time of the range in milliseconds.
        sura_start_times (Dict[str, int]): Dictionary of sura start times in milliseconds.
        input_dir (Path): Directory where the sura MP3 files are located.
        
    Returns:
        List[str]: List of sura numbers that overlap with the given time range.
    """
    suras = []
    for sura, start_time in sura_start_times.items():
        sura_length = get_sura_length(sura, input_dir)
        sura_end_time = start_time + sura_length
        
        if start_time < end and sura_end_time > start:
            suras.append(sura)
    
    return suras

def save_clips(audio: AudioSegment, clip_length_ms: int, overlap_ms: int, output_dir: Path, sura_start_times: Dict[str, int], input_dir: Path) -> None:
    """
    Saves audio clips of a specified length with overlapping intervals from a combined audio segment.
    
    Args:
        audio (AudioSegment): The combined audio segment.
        clip_length_ms (int): Length of each clip in milliseconds.
        overlap_ms (int): Overlap between consecutive clips in milliseconds.
        output_dir (Path): Directory where the output clips will be saved.
        sura_start_times (Dict[str, int]): Dictionary of sura start times in milliseconds.
        input_dir (Path): Directory where the sura MP3 files are located.
        
    Returns:
        None
    """
    start = 0
    clip_num = 1
    
    while start < len(audio):
        end = start + clip_length_ms
        clip = audio[start:end]
        sura_range = get_sura_range(start, end, sura_start_times, input_dir)
        sura_range_str = "_".join(sura_range) if len(sura_range) > 1 else sura_range[0]
        filename = f"sura_{sura_range_str}_c{clip_num}.m4a"
        temp_path = output_dir / f"temp_{filename}"

        try:
            clip.export(temp_path, format="mp3")
            output_path = output_dir / filename
            ffmpeg.input(str(temp_path)).output(str(output_path), codec='aac').run(overwrite_output=True)
            os.remove(temp_path)
        except Exception as e:
            logging.error(f"Error exporting clip {filename}: {e}")
        
        start = end - overlap_ms
        clip_num += 1

def main(input_dir: Path, output_dir: Path, clip_length_minutes: int = 5, overlap_seconds: int = 5) -> None:
    """
    Main function to concatenate audio files and save clips with overlapping intervals.
    
    Args:
        input_dir (Path): Directory where the MP3 files are located.
        output_dir (Path): Directory where the output clips will be saved.
        clip_length_minutes (int, optional): Length of each clip in minutes. Defaults to 5.
        overlap_seconds (int, optional): Overlap between consecutive clips in seconds. Defaults to 5.
        
    Returns:
        None
    """
    clip_length_ms = clip_length_minutes * 60 * 1000
    overlap_ms = overlap_seconds * 1000

    files = sorted([file for file in input_dir.iterdir() if file.suffix == '.mp3'])
    logging.info(f"Found {len(files)} MP3 files in {input_dir}.")
    
    combined_audio, sura_start_times = concatenate_audio_files(files)
    
    combined_audio_path = output_dir / "combined_audio.mp3"
    combined_audio.export(combined_audio_path, format="mp3")
    logging.info(f"Combined audio saved to {combined_audio_path}.")
    
    save_clips(combined_audio, clip_length_ms, overlap_ms, output_dir, sura_start_times, input_dir)

if __name__ == "__main__":
    input_directory = Path('/Users/hm/Downloads/Quran_Recordings/Short_Saud_Al-Shuraim_(Updated2)(MP3_Quran)')  # Directory where your MP3 files are located
    output_directory = input_directory / 'clips'  # Directory where the output clips will be saved
    output_directory.mkdir(parents=True, exist_ok=True)
    main(input_directory, output_directory, clip_length_minutes=1)
