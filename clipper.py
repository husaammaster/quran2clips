from pydub import AudioSegment
import os

def concatenate_audio_files(file_list):
    combined = AudioSegment.empty()
    sura_start_times = {}
    current_time = 0

    for file in file_list:
        sura_number = os.path.basename(file).split('.')[0]
        sura_audio = AudioSegment.from_mp3(file)
        combined += sura_audio
        sura_start_times[sura_number] = current_time
        current_time += len(sura_audio)
        print(F"Added sura {sura_number}.")
        print(F"Total length {current_time / 3600000} h")
    
    return combined, sura_start_times

def get_sura_length(sura_number, input_dir):
    sura_file = os.path.join(input_dir, f"{sura_number}.mp3")
    sura_audio = AudioSegment.from_mp3(sura_file)
    return len(sura_audio)

def get_sura_range(start, end, sura_start_times, input_dir):
    suras = []
    for sura, start_time in sura_start_times.items():
        sura_length = get_sura_length(sura, input_dir)
        sura_end_time = start_time + sura_length
        
        # Check if the clip overlaps with the sura
        # Case 1: Clip starts in the sura (start_time < end)
        # Case 2: Clip ends in the sura (sura_end_time > start)
        # Case 3: Clip overlaps the entire sura (both conditions true)
        # Case 4: Clip is entirely within the sura (both conditions true)
        if (start_time < end and sura_end_time > start):
            suras.append(sura)
    
    return suras

def save_clips(audio, clip_length_ms, overlap_ms, output_dir, sura_start_times, input_dir):
    start = 0
    clip_num = 1
    
    while start < len(audio):
        end = start + clip_length_ms
        clip = audio[start:end]
        sura_range = get_sura_range(start, end, sura_start_times, input_dir)
        sura_range_str = "_to_".join(sura_range) if len(sura_range) > 1 else sura_range[0]
        filename = f"clip_{sura_range_str}_n{clip_num}.mp3"
        clip.export(os.path.join(output_dir, filename), format="mp3")
        start = end - overlap_ms
        clip_num += 1

def main(input_dir, output_dir, clip_length_minutes=10, overlap_seconds=5):
    clip_length_ms = clip_length_minutes * 60 * 1000
    overlap_ms = overlap_seconds * 1000

    files = sorted([os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.mp3')])
    print(files[:5])
    combined_audio, sura_start_times = concatenate_audio_files(files)
    save_clips(combined_audio, clip_length_ms, overlap_ms, output_dir, sura_start_times, input_dir)

if __name__ == "__main__":
    input_directory = '/Users/hm/Downloads/Quran_Recordings/Islam_Subhi_(MP3_Quran)'  # Directory where your MP3 files are located
    output_directory = '/Users/hm/Downloads/Quran_Recordings/Islam_Subhi_(MP3_Quran)/clips'  # Directory where the output clips will be saved
    os.makedirs(output_directory, exist_ok=True)
    main(input_directory, output_directory)
