from pydub import AudioSegment, effects
import os, subprocess
import ffmpeg
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def speedup_audio_ffmpeg(input_path: Path, file_output_path: Path, speed_change: float) -> None:
    """
    Speed up the audio file using ffmpeg.
    
    Args:
        input_path (Path): Path to the input audio file.
        file_output_path (Path): Path to the output audio file.
        speed_change (float): The factor by which to change the playback speed.
        
    Returns:
        None
    """
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', str(input_path), '-filter:a', f"atempo={speed_change}", str(file_output_path)
        ], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error speeding up audio with ffmpeg: {e}")

def preprocess_audio_files(sura_audio: AudioSegment) -> AudioSegment:
    """
    Preprocess an individual sura audio file before concatenation.
    
    Args:
        sura_audio (AudioSegment): The sura audio file to preprocess.
        
    Returns:
        AudioSegment: The preprocessed sura audio file with normalized audio level.
    """
    sura_audio = effects.normalize(sura_audio)
    return sura_audio

def postprocess_combined_audio(combined_audio: AudioSegment, combined_path: Path, sura_start_times: Dict[str, int], desired_length_minutes: int) -> Tuple[AudioSegment, Dict[str, int]]:
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

def postprocess_clip(clip: AudioSegment, fade_seconds: float) -> AudioSegment:
    """
    Postprocess an individual audio clip after it is cut from the combined audio.
    
    Args:
        clip (AudioSegment): The audio clip to postprocess.
        fade_seconds (float): The duration of the fade in and fade out effect in seconds.
        
    Returns:
        AudioSegment: The postprocessed audio clip with fade in and fade out effects.
    """
    fade_milliseconds = int(fade_seconds*1000)
    clip = clip.fade_in(fade_milliseconds).fade_out(fade_milliseconds)
    return clip

def postprocess_file(output_path: Path, metadata: Dict[str, str]) -> None:
    """
    Edit the resulting clip file to add metadata such as album art, album name, composer, genre, and title.
    
    Args:
        output_path (Path): The path to the output clip file to edit.
        metadata (Dict[str, str]): A dictionary containing metadata parameters.
        
    Returns:
        None
    """
    audio = ffmpeg.input(str(output_path))
    metadata_params = []
    for key, value in metadata.items():
        metadata_params.extend(['-metadata', f'{key}={value}'])
    ffmpeg.output(audio, str(output_path), **{k: v for i, (k, v) in enumerate(zip(metadata_params[0::2], metadata_params[1::2]))}).run(overwrite_output=True)

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

def get_sura_length(sura_number: str, input_dir: Path, speedup_factor:float) -> int:
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
        return len(sura_audio) / speedup_factor
    except Exception as e:
        logging.error(f"Error loading {sura_file}: {e}")
        return 0

def get_sura_range(start: int, end: int, sura_start_times: Dict[str, int], input_dir: Path, speedup_factor) -> List[str]:
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
        sura_length = get_sura_length(sura, input_dir, speedup_factor)
        sura_end_time = start_time + sura_length
        
        if start_time < end and sura_end_time > start:
            suras.append(sura)
    
    return suras

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
        clip = postprocess_clip(clip, fade_duration)
        sura_range = get_sura_range(start, end, sura_start_times, input_dir, speedup_factor)
        sura_range_str = "_".join(sura_range) if len(sura_range) > 1 else sura_range[0]
        filename = f"sura_{sura_range_str}_c{clip_num}.m4a"
        temp_path = output_dir / f"temp_{filename}"

        try:
            clip.export(temp_path, format="mp3")
            output_path = output_dir / filename
            ffmpeg.input(str(temp_path)).output(str(output_path), codec='aac').run(overwrite_output=True)
            os.remove(temp_path)
            postprocess_file(output_path, metadata)
        except Exception as e:
            logging.error(f"Error exporting clip {filename}: {e}")
        
        start = end - overlap_ms
        clip_num += 1

def main(input_dir: Path, output_dir: Path, desired_length_minutes, clip_length_minutes, overlap_seconds, fade_seconds: float = 5.0, metadata: Dict[str, str] = None) -> None:
    """
    Main function to concatenate audio files and save clips with overlapping intervals.
    
    Args:
        input_dir (Path): Directory where the MP3 files are located.
        output_dir (Path): Directory where the output clips will be saved.
        clip_length_minutes (int, optional): Length of each clip in minutes. Defaults to 5.
        overlap_seconds (int, optional): Overlap between consecutive clips in seconds. Defaults to 5.
        desired_length_minutes (int, optional): Desired total length of the combined audio in minutes. Defaults to 60.
        fade_seconds (int, optional): Duration of the fade in and fade out effect in seconds. Defaults to 2.0.
        metadata (Dict[str, str], optional): Metadata for the output files. Defaults to None.
        
    Returns:
        None
    """
    clip_length_ms = clip_length_minutes * 60 * 1000
    overlap_ms = overlap_seconds * 1000

    files = sorted([file for file in input_dir.iterdir() if file.suffix == '.mp3'])
    logging.info(f"Found {len(files)} MP3 files in {input_dir}.")
    
    combined_audio, sura_start_times, speedup_factor = concatenate_audio_files(files, desired_length_minutes, output_dir)
    
    combined_audio_path = output_dir / "combined_audio.mp3"
    logging.info(f"Combined audio saved to {combined_audio_path}.")
    
    save_clips(combined_audio, clip_length_ms, overlap_ms, output_dir, sura_start_times, input_dir, fade_seconds, metadata, speedup_factor)

if __name__ == "__main__":
    input_directory = Path('/Users/hm/Downloads/Quran_Recordings/Short_Saud_Al-Shuraim_(Updated2)(MP3_Quran)')  # Directory where your MP3 files are located
    output_directory = input_directory / 'clips'  # Directory where the output clips will be saved
    output_directory.mkdir(parents=True, exist_ok=True)
    metadata_example = {
        "album": "Quran Recordings",
        "composer": "Various",
        "genre": "Religious",
        "title": "Sample Clip"
    }
    main(input_directory, output_directory, clip_length_minutes=1, desired_length_minutes=3, overlap_seconds=15, fade_seconds=10.0, metadata=metadata_example)
