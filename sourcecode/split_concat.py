from pydub import AudioSegment
from pathlib import Path
from typing import List, Dict, Tuple
import logging

from audio import preprocess_audio_files

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def postprocess_combined_audio(combined_audio: AudioSegment, combined_path: Path, sura_start_times: Dict[str, int], desired_length_minutes: int) -> Tuple[AudioSegment, Dict[str, int]]:
    from speedster import speedup_audio_ffmpeg  # moved import here to break circular dependency
    """
    Postprocess the combined audio file and sura_start_times after concatenation.
    
    Args:
        combined_audio (AudioSegment): The combined audio file to postprocess.
        sura_start_times (Dict[str, int]): Dictionary of sura start times in milliseconds.
        desired_length_minutes (int): The desired total length of the combined audio in minutes.
        
    Returns:
        Tuple[AudioSegment, Dict[str, int]]: The postprocessed combined audio file and updated sura start times.
    """
    desired_length_ms = desired_length_minutes * 60 * 1000
    current_length_ms = len(combined_audio)
    speed_change = desired_length_ms / current_length_ms
    speed_change = 1.0 / speed_change

    # Export the combined audio to a temporary file
    temp_combined_audio_path = combined_path / "combined_audio.mp3"
    combined_audio.export(temp_combined_audio_path, format="mp3")
    
    # Speed up the audio using ffmpeg
    temp_output_audio_path = combined_path / "combined_audio_speed.mp3"
    speedup_audio_ffmpeg(temp_combined_audio_path, temp_output_audio_path, speed_change)
    
    # Load the sped-up audio back into an AudioSegment
    combined_audio = AudioSegment.from_mp3(temp_output_audio_path)

    # Adjust sura start times according to the speed change
    adjusted_sura_start_times = {sura: int(start_time / speed_change) for sura, start_time in sura_start_times.items()}
    
    # Clean up temporary file
    # temp_combined_audio_path.unlink()

    return combined_audio, adjusted_sura_start_times, speed_change

def concatenate_audio_files(file_list: List[Path], desired_length_minutes: int, ouput_path:Path) -> Tuple[AudioSegment, Dict[str, int]]:
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
            sura_audio = preprocess_audio_files(sura_audio)
        except Exception as e:
            logging.error(f"Error loading {file}: {e}")
            continue

        combined += sura_audio
        sura_start_times[sura_number] = current_time
        current_time += len(sura_audio)
        logging.info(f"Added sura {sura_number}. Total length {current_time / 3600000:.2f} h")
    
    combined, sura_start_times, speedup_factor = postprocess_combined_audio(combined, ouput_path, sura_start_times, desired_length_minutes=desired_length_minutes)
    return combined, sura_start_times, speedup_factor

def get_sura_length_ms(sura_number: str, input_dir: Path, speedup_factor:float) -> int:
    """
    Gets the length of a sura audio file in milliseconds.
    
    Args:
        sura_number (str): The number of the sura as a string.
        input_dir (Path): Directory where the sura MP3 files are located.
        
    Returns:
        int: Length of the sura audio file in milliseconds.
    """
    sura_file = input_dir / f"{sura_number:03d}_median.mp3"
    try:
        sura_audio = AudioSegment.from_mp3(sura_file)
        return len(sura_audio) / speedup_factor
    except Exception as e:
        logging.error(f"Error loading {sura_file}: {e}")
        return 0

def get_sura_range(start_sec: int, end_sec: int, sura_start_times: Dict[str, int], input_dir: Path, speedup_factor) -> List[str]:
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
        sura_length_sec = get_sura_length_ms(sura, input_dir, speedup_factor)/1000
        sura_end_time = start_time + sura_length_sec
        
        if start_time < end_sec and sura_end_time > start_sec:
            suras.append(F"{sura:03d}")
    
    return suras