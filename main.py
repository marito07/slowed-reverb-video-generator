from pedalboard import Pedalboard, Reverb, Gain, Compressor
from pedalboard.io import AudioFile
from pydub import AudioSegment
import moviepy.editor as mpe
import librosa
import os, glob
import subprocess

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

files = os.listdir('input')
print(files)

for filenamed in files:

    sound = AudioSegment.from_wav(f'input/{filenamed}')

    speed_multiplier = 0.8  # Slowdown audio, 1.0 means original speed, 0.5 half speed etc

    def speed_change(sound, speed=1.0):
        sound_with_altered_frame_rate = sound._spawn(
            sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed)}
        )
        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

    slow = speed_change(sound, speed_multiplier)

    with open("salida.wav", "wb") as out_f:
        slow.export(out_f, format="wav")

    with AudioFile('salida.wav', 'r') as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    board = Pedalboard([
        Reverb(room_size=0.6, width=0.001, dry_level=0.6),
        Gain(gain_db=-1.5),
    ])

    # Run the audio through this pedalboard!
    effected = board(audio, samplerate)

    with AudioFile('processed-output.wav', 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)

    dur = librosa.get_duration(filename='processed-output.wav')

    # ffmpeg_extract_subclip("full.mp4", start_seconds, end_seconds, targetname="cut.mp4")
    ffmpeg_extract_subclip("full.mp4", 0, int(dur), targetname="cut.mp4")


    subprocess.call(['ffmpeg', '-i' ,'cut.mp4', '-i', 'processed-output.wav', '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', f'output/{filenamed[:len(filenamed)-4]}.mp4'])
