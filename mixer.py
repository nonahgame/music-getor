# mixer.py ; new 24 11 25
import os
from pydub import AudioSegment
import numpy as np
import subprocess
import uuid

def ensure_mono_16k(path_in, path_out):
    # optional resample helper using ffmpeg to standardize sample rate / channels
    cmd = f'ffmpeg -y -i "{path_in}" -ar 22050 -ac 1 "{path_out}"'
    subprocess.run(cmd, shell=True, check=True)
    return path_out

def mix_vocals_and_beat(beat_path, vocals_path, out_path, vocals_gain_dB=0.0):
    """
    Mix vocals onto beat. Aligns from start. Simple mixing: overlay vocals at start.
    For production-quality alignment you would need vocal timing / beat detection.
    """
    print(f"[mixer] Loading beat: {beat_path}")
    beat = AudioSegment.from_file(beat_path)
    vocals = AudioSegment.from_file(vocals_path)

    # Normalize lengths: loop beat if shorter than vocals or extend with silence
    if len(beat) < len(vocals):
        # Loop beat to match vocals duration
        times = int(len(vocals) / len(beat)) + 1
        beat = beat * times
    # Trim beat to vocals length (optional: mix to beat duration)
    target_len = min(len(beat), len(vocals))
    beat = beat[:target_len]
    vocals = vocals[:target_len]

    # Apply gain
    vocals = vocals + vocals_gain_dB

    print(f"[mixer] overlaying vocals (len {len(vocals)}ms) onto beat (len {len(beat)}ms)")
    mixed = beat.overlay(vocals)

    # Export as MP3 at 192k
    mixed.export(out_path, format="mp3", bitrate="192k")
    return out_path

def create_final_mp4(mixed_mp3_path, out_mp4_path, title=None, lyrics_text_file=None):
    """Creates a simple MP4 with black background + title + lyrics (textfile) using ffmpeg."""
    # we create a color video then burn title and (optionally) lyrics via textfile
    lyrics_file_arg = ""
    if lyrics_text_file and os.path.exists(lyrics_text_file):
        lyrics_file_arg = f",drawtext=textfile='{lyrics_text_file}':fontcolor=yellow:fontsize=30:x=(w-text_w)/2:y=h-th-100"
    title_escaped = (title or "").replace("'", "\\'")
    cmd = f'''
    ffmpeg -y -i "{mixed_mp3_path}" -f lavfi -i color=c=black:s=1280x720:d=300 \
    -filter_complex "[1:v]drawtext=text='{title_escaped}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=100:box=1:boxcolor=black@0.8{lyrics_file_arg}" \
    -c:v libx264 -c:a aac -b:a 192k -shortest "{out_mp4_path}"
    '''
    subprocess.run(cmd, shell=True, check=True)
    return out_mp4_path
