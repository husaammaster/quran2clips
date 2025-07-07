
from gtts import gTTS
from pathlib import Path
from mutagen.easyid3 import EasyID3  # Import at the top of the function scope, not inside try
from mutagen.mp3 import MP3


def generate_tts_numbers(dest: Path, max_int: int, w_subdirectories: bool = False):
    """
    Generates TTS audio files (mp3) for numbers up to max_int.

    Args:
        dest (Path): The destination path for audio files.
        max_int (int): The highest number to generate.
        w_subdirectories (bool): Whether to group files into subdirectories and set album metadata.

    Returns:
        None
    """
    print("Generating test audio")
    tts = gTTS(text="Hello, this is a tts test audio file.", lang='en')

    dest.mkdir(parents=True, exist_ok=True)
    tts.save(dest / "test.mp3")


    print(F"Generating Numbered audio up to {max_int}")
    for i in range(1, max_int + 1):
        p = dest
        if w_subdirectories:
            p = dest / f"{i // 10 * 10:03d}"
            p.mkdir(parents=True, exist_ok=True)
        out_file = p / f"{i:03d}.mp3"
        if out_file.exists():
            continue  # Skip if file already exists
        tts = gTTS(text=str(i), lang='de')
        tts.save(out_file)
        try:
            # Ensure file has an ID3 tag
            mp3 = MP3(str(out_file))
            if mp3.tags is None:
                mp3.add_tags()
                mp3.save()
            audio = EasyID3(str(out_file))
            audio['title'] = f"Number {i:03d}"
            if w_subdirectories:
                audio['album'] = "Album " + str(p.name)
            audio.save()
        except Exception as e:
            print(f"Warning: Could not set metadata for {out_file}: {e}")


if __name__ == "__main__":
    OUTPUT_DIR = Path("./output")
    MAX_NUM = 100
    W_SUBDIR = False

    generate_tts_numbers(OUTPUT_DIR, MAX_NUM, W_SUBDIR)