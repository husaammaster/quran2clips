from pathlib import Path
from typing import Dict
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3


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

    clip_length_sec = len(clip)/1000.0
    clip_length_ms = int(clip_length_sec*1000)

    if clip_length_sec < fade_seconds*2:
        # for short clips
        if clip_length_sec < fade_seconds:
            return clip.fade_in(int(clip_length_ms))
        else:
           return clip.fade_in(fade_milliseconds)

    else:
        # normal case where clip is longer than fade_seconds*2
        fade_in = clip[:fade_milliseconds].fade_in(fade_milliseconds)

        middle = clip[fade_milliseconds:-fade_milliseconds]
        middle_length_sec = len(middle)/1000.0
        # split middle into 4 parts and fade out the middle half of it
        quarter_ms = int((middle_length_sec*1000)/4)
        mid1 = middle[:quarter_ms].fade_out(quarter_ms)
        mid2 = AudioSegment.silent(duration=quarter_ms)
        mid3 = AudioSegment.silent(duration=quarter_ms)
        mid4 = middle[3*quarter_ms:].fade_in(quarter_ms)
        middle = mid1 + mid2 + mid3 + mid4

        fade_out = clip[-fade_milliseconds:].fade_out(fade_milliseconds)

        clip = fade_in + middle + fade_out
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
    if metadata is not None:
        # Ensure file has an ID3 tag
        mp3 = MP3(str(output_path))
        if mp3.tags is None:
            mp3.add_tags()
            mp3.save()
        audio = EasyID3(str(output_path))
        for key, value in metadata.items():
            audio[key] = value
        audio.save()