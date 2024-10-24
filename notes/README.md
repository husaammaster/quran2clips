# quran2clips
A tool for turning quran recordings into shorter overlapping clips for easier memorization and looping.

# Motivation: 
There is no good tool or app for selecting a range you want to learn, selecting your personal reading speed which you normally read in and just listening to that range at that speed (with or without looping):
- Most youtube videos are either only full sura videos or full juz' videos. Not page specific and not aya specific.
- Most apps which can loop over multiple surats, but opening the app and selecting the starting sura and aya and ending sura and aya is a hastle. Especially for quick plug and play memorization in everyday life, for example starting the playback with a voice command while you are driving your car or doing sports or busy cooking and dont have your hands free. 
- Most apps get automatically closed when you dont use them, which means you always restart your reading at the beginning of the page range. Therefore you memorize the beginning pages too well and the last pages very weakly.
- Also for each reader you have to memorize the correct playback speed setting or alternatively you just stick to one or two readers and your reading becomes very aligned to those specific readers. 

# Planned Goal:
This tool helps you by creating all relevant clips (of the page and ayat range you want to memorize) as mp3 files with useful song titles, album titles and playlists. This allows you to put them onto your device and use the voice assistant on your device by saying:
 - "Play the song 'Pages 234 to 250'."
 - "Shuffle the songs in the playlist 'My Weekly Repetitions'."
 - "Continue playback." to just quickly return to whatever playback you had last active.

---

# Specific Features
Some of the main planned features are:
1. **Speed normaization**:
    - Adjusting Speed to a common speed, independently of the specific reader.
    - Takes the reader-specific playback time for a sura and the number of pages of that sura and scales the audio file to a user-specified preferred speed, for example 20 pages per hour. This allows you to hear every reader automatically scaled to your favorite reading speed.
2. **Page range clips**:
    - Export speed-normalized clips from a specific start to ending page range.
    - Uses the true page playback times of the sura if available. If not available then it uses normalized page playback times to cut the clips. Same for ayat of a sura.
3. **Assistant Compatibility**:
    - Hands free starting and changing of playback ranges by using mp3 files instead of apps with GUIs. Useful for during driving, cooking, doing chores or doing sports.
    - When exporting, the sura range and page range are automatically stored as the song title for easy assistant access (starting and changing playback)
    - The title of the mp3 file gets displayed on your phone display or car display, depending on your music players capabilities, as most players display the music titles.
4. **Learning from multiple readers/citation styles**:
    - Option to not only export a single track for a given page range, but instead export an album of your favorite readers, all speed-normalized.
    - For playing a single reader you would say to your assistant "Play 'Pages 515 to 535'." which would play that mp3 file which has a single reader.
    - For playing multiple readers you would say: "Play ***the album*** 'Pages 515 to 535'." or "Shuffle ***the album*** 'Pages 515 to 535'."  where the album would have multiple files of that page range for each of your added readers. And the assistant would play those files in order or in shuffle mode depending on your voice commad.
5. **Overlapping short clips**:
    - Given a page range, it exports multiple overlapping short clips of varying sizes. These are all exported into a single playlist with that range name. This allows you to shuffle between different pages of that range and skip the easy ones (easily accessible via voice assistant as the "next track" voice command).
    - For example the "Playlist Pages 1 to 10" would include the files (see image which will be uploaded later):
      - (Full range) Page 1 to 10
      - (Half range) Page 1 to 5, Page 6 to 10
      - (Half range with offset) Page 3.5 to 8.5
      - (Third range) Page 1 to 3, Page 4 to 6, Page 7 to 10
      - (Third range with offset) Page 2,5 to 5,5, Page 6,5 to 8,5
      - (Singel pages) Page 1, 2, ..., 9, 10
      - (Single pages with offset) Page 1.5 to 2.5, Page 2.5 to 3.5, ..., Page 8.5 to 9.5
    - All clip borders are rounded to the closest half page and duplicate clips are removed.
    - For shuffling, after each clip there is a short 1.5 second pause, so that the meaning of the previous ayat does not connect to the next ayat.
6. **Short quiz pages**:
    - For a given Page range a quiz playlist of short overlapping clips of size of half a page and smaller are created, each half page repeats twice. The first time the 
audio level slowly but linearly turn quieter and quieter, so that you have to continue the ayat yourself. And after the playback finished the page will repeat with normal audio levels for you to check if your memorization was correct.
    - Then you can say to your assistant "Shuffle/Play the playlist 'Quiz Page 1 to 10'." to get one short clip after the other.


# Downloads
From mp3quran.net through the torrent links