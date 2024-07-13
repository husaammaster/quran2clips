# generating clippings
I have the following file structure:

hm@MacBook-Air-von-H ~ % cd Downloads 
hm@MacBook-Air-von-H Downloads % cd Islam_Subhi 
hm@MacBook-Air-von-H Islam_Subhi % ls
001.mp3	019.mp3	031.mp3	047.mp3	057.mp3	068.mp3	079.mp3	089.mp3	099.mp3	110.mp3
002.mp3	020.mp3	032.mp3	048.mp3	058.mp3	070.mp3	080.mp3	090.mp3	100.mp3	111.mp3
005.mp3	021.mp3	034.mp3	049.mp3	059.mp3	071.mp3	081.mp3	091.mp3	101.mp3	114.mp3
011.mp3	023.mp3	035.mp3	050.mp3	060.mp3	072.mp3	082.mp3	092.mp3	102.mp3
012.mp3	024.mp3	036.mp3	051.mp3	061.mp3	073.mp3	083.mp3	093.mp3	103.mp3
013.mp3	025.mp3	038.mp3	052.mp3	062.mp3	074.mp3	084.mp3	094.mp3	104.mp3
014.mp3	026.mp3	041.mp3	053.mp3	063.mp3	075.mp3	085.mp3	095.mp3	106.mp3
015.mp3	027.mp3	042.mp3	054.mp3	064.mp3	076.mp3	086.mp3	096.mp3	107.mp3
017.mp3	029.mp3	044.mp3	055.mp3	066.mp3	077.mp3	087.mp3	097.mp3	108.mp3
018.mp3	030.mp3	046.mp3	056.mp3	067.mp3	078.mp3	088.mp3	098.mp3	109.mp3
hm@MacBook-Air-von-H Islam_Subhi % 


I am new to working with audio files, so please give me a useful python library and teach me the basics.
Its a downlod of the quran, or at least a large section of its 114 suras

I want to write a code, which concatenates all tracks in order of their number. Then cuts that concatenated full track into sections of 10 minutes each, but with 5 seconds overlap between each two. Then saves those tracks based on the numbers of the suras from which they were created initially. So a track, which is from sura 088 only should be named clip_088_n1, clip_088_n2, clip_088_n3 etc. if 088 results in multiple clips. And if a clip contains multiple suras, then the clip should be named clip_088_to_092