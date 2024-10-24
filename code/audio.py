from pydub import AudioSegment, effects


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