import csv
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

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