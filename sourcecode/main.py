from pathlib import Path
import statistics

from speedster import create_median_length_tracks
from json_gen import load_folder_dfs


def analyze_n_generate_medians(
        quran_data_folder: Path):
    """
    A function to generate median length tracks for all reciters in the given folder.

    Args:
        quran_data_folder (Path): Directory where for each reciter a folder with the MP3 files is stored.

    Does:
        - Loads/generates metadata dataframes for all reciters.
        - Concatenates the dataframes of all reciters.
        - Saves the concatenated dataframe and an analysis of track lenghts.
        - Creates median length tracks for all reciters.
    """


    print("\n"*2, " Fixing files and analyzing them ".center(80, "="), "\n"*2)
    rec_folders = sorted([folder for folder in quran_data_folder.iterdir() if folder.is_dir()])
    

    # create_folder_dfs(rec_folders)
    reciter_sums_dict = load_folder_dfs(quran_data_folder, rec_folders)

    median_reciter_sum = reciter_sums_dict.values()
    median_reciter = statistics.median(median_reciter_sum)
    print("")
    print(F"Median of all reciters: {median_reciter}")
    rec_med_speedup = {}
    for reciter, reciter_sum in reciter_sums_dict.items():
        rec_med_speedup[reciter] = reciter_sum/median_reciter
        print(F"Speedup factor for {reciter} to reach median: {rec_med_speedup[reciter]}")
    
    create_median_length_tracks(rec_folders, rec_med_speedup) # in own subfolder

    print("\n"*2, " Done: Generating median files for all reciters ".center(80, "="), "\n"*2)
    
    # Memory optimization
    return rec_folders, reciter_sums_dict, median_reciter_sum, rec_med_speedup

"""
def speedup_medians_to_spedfull(
        quran_data_folder: Path, 
        desired_juz_length_minutes, 
        clip_length_minutes, 
        overlap_seconds, 
        fade_seconds: float = 5.0, 
        metadata: Dict[str, str] = None) -> None:
    "
    Args:
        
    Does:
        - creates subfolder for the reader for the specified min per juz
        - MISTAKE!!get the sum of median lengths for all suras
        - MISTAKE!!the desired total length is 30 times desired_juz_length_minutes
        - get the speedup factor so that the sum of median lengths is equal to the desired total length
        - for each sura:
            - speed up the median length track
            - save it to the new subfolder with the specified min per juz (full len tracks) as mp3 instead of aac
                - filename being sura number plus "_spedfull_{desired_juz_length_minutes}min.mp3"
            - save the metadata for the new track with 
                - title being sura str name with "F" suffix
                - genre being quran 
                - artist being the speed
                - album being the reciter plus suffix "F"

    Returns:
        None
    "

    

def spedfull_to_clips(
        quran_data_folder: Path, 
        desired_juz_length_minutes, 
        clip_length_minutes, 
        overlap_seconds, 
        fade_seconds: float = 5.0, 
        metadata: Dict[str, str] = None) -> None:
    "
    Does:
        - creates clips subfolder for the specified min per juz
        - for each sura:
            - calculates how many percents of the full length the clip length is
            - calculates how many percents of the full length the overlap length is
            - Clips the spedfulls with overlapping intervals by using percentages
            - add fade in/out
            - Saves the clips to the clip folder
                - filename being sura number with infix "C" and "Xp - Yp" suffix
            - save the metadata for the new track with
                - title being sura str name with infix "C" and "Xp - Yp" suffix
                - genre being quran-clip 
                - artist being the speed
                - album being the reciter plus suffix "C"
    "
    

    desired_total_length_minutes = 30 * desired_juz_length_minutes
    clip_length_ms = 1000 * 60 * clip_length_minutes 
    overlap_ms = overlap_seconds * 1000



"""


if __name__ == "__main__":
    quran_data_path = Path('/Users/hm/Documents/Quran_Recordings/')
    # Directory where your MP3 files are located
    # output_directory = quran_data_path / 'clips'  # Directory where the output clips will be saved
    # output_directory.mkdir(parents=True, exist_ok=True)

    desired_juz_length_minutes = 45
    metadata = {
        "album": quran_data_path.stem,
        "composer": F"{desired_juz_length_minutes} minutes Juz",
        "genre": "Quran",
        "title": "Unnamed Clip"
    }

    analyze_n_generate_medians(
        quran_data_path,
        )

    # now generate the clips for each file inside the reciter/median/reciter folder

    

