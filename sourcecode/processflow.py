from pathlib import Path
from typing import Dict
from pydub import AudioSegment


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