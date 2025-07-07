from pathlib import Path
import random
from tqdm import tqdm

def shuffle_audio_files(audio_folder_path: Path, unshuffle: bool = False):
    """
    adds a random 4 digit number prefix RND1234_ to the audio files to shuffle them for primitive devices/players.

    Args:
        audio_folder_path: Path to the audio folder
        unshuffle: If True, the files will be unshuffled, which removes the RND prefix and renames the files to the original name.
    Returns:
        None
    """
    if unshuffle:
        print("Unshuffling audio files, by removing the RND prefix...")
        for file in tqdm(audio_folder_path.glob('*.mp3')):
            file_name = file.stem
            if file_name.startswith("RND") and len(file_name) >= 8 and file_name[3:7].isdigit() and file_name[7] == "_":
                base_name = file_name[8:]
                if not base_name:  # Skip if base name is empty
                    print(f"Skipping {file.name}: empty base name after removing prefix")
                    continue
                new_file_name = f"{base_name}{file.suffix}"
                new_file_path = file.with_name(new_file_name)
                if new_file_path.exists():
                    print(f"Skipping {file.name}: would overwrite existing file {new_file_name}")
                    continue
                file.rename(new_file_path)
            else:
                continue
    else:
        print("Shuffling audio files, by adding or refreshing a RND prefix...")
        for file in tqdm(audio_folder_path.glob('*.mp3')):
            file_name = file.stem
            # Check if the file already has a RND prefix
            if file_name.startswith("RND") and len(file_name) >= 8 and file_name[3:7].isdigit() and file_name[7] == "_":
                # Remove the existing RND prefix
                base_name = file_name[8:]
            else:
                base_name = file_name
            # Add a new random 4 digit number prefix
            new_file_name = f"RND{random.randint(0, 9999):04d}_{base_name}{file.suffix}"
            new_file_path = file.with_name(new_file_name)
            if new_file_path.exists():
                print(f"Skipping {file.name}: would overwrite existing file {new_file_name}")
                continue
            file.rename(new_file_path)

if __name__ == "__main__":
    AUDIO_FOLDER_PATH = Path('./output/')
    shuffle_audio_files(AUDIO_FOLDER_PATH, unshuffle=True)