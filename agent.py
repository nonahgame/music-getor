# agent.py
import os
import uuid
import random
import string
import base64
import requests
from datetime import datetime
from pydub import AudioSegment
import subprocess
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = "output"
PUBLIC_DIR = "public_downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

FULL_BEATS = [
    "https://cdn.pixabay.com/download/audio/2023/03/20/audio_4d6c8f1a2b.mp3?filename=lofi-chill-109320.mp3",
    "https://cdn.pixabay.com.download/audio/2022/11/15/audio_5d3d5e8f2a.mp3?filename=chill-abstract-intention-12099.mp3",
    "https://cdn.pixabay.com/download/audio/2023/08/15/audio_8f2d4a5c5e.mp3?filename=lofi-study-112191.mp3",
    "https://cdn.pixabay.com/download/audio/2023/06/27/audio_7d8f9e3c1a.mp3?filename=lofi-vibes-160116.mp3"
]


# -----------------------------
# FFMPEG TEXT ESCAPER (for title only)
# -----------------------------
def escape_ffmpeg_text(t: str) -> str:
    if not t:
        return ""
    t = t.replace("\\", "\\\\")
    t = t.replace("'", "\\'")
    t = t.replace("\n", " ")
    return t


def upload_to_github(local_file_path, github_folder="d-output"):
    try:
        filename = os.path.basename(local_file_path)

        with open(local_file_path, "rb") as f:
            content = f.read()

        encoded = base64.b64encode(content).decode("utf-8")

        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{github_folder}/{filename}"

        data = {
            "message": f"Add generated file {filename}",
            "content": encoded
        }

        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        r = requests.put(url, json=data, headers=headers)

        if r.status_code in [200, 201]:
            print(f"Uploaded to GitHub: {filename}")
            return True

        print(f"GitHub upload failed: {r.text}")
        return False

    except Exception as e:
        print(f"GitHub upload error: {e}")
        return False


def download_file(url, dest):
    try:
        import urllib.request
        urllib.request.urlretrieve(url, dest)
        return os.path.getsize(dest) > 1000000
    except:
        return False



def run_agent(data):
    title = data.get("title", "My Hit Song")
    lyrics = data.get("lyrics", "Yeah yeah yeah")

    safe_title = escape_ffmpeg_text(title)

    # Create a text file for long lyrics
    lyrics_file = os.path.join(OUTPUT_DIR, "lyrics.txt")
    with open(lyrics_file, "w", encoding="utf-8") as f:
        f.write(lyrics)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    safe_file_title = "".join(c if c.isalnum() else "_" for c in title)[:25]
    base = f"{safe_file_title}_{ts}_{uid}"

    beat_path = f"{OUTPUT_DIR}/{base}_beat.mp3"

    success = False
    for url in FULL_BEATS:
        print("Downloading:", url)
        if download_file(url, beat_path):
            success = True
            break

    if not success:
        AudioSegment.silent(duration=180000).export(beat_path, format="mp3")

    beat = AudioSegment.from_mp3(beat_path)
    duration_ms = len(beat)
    vocal = AudioSegment.silent(duration=duration_ms) - 15
    mixed = beat.overlay(vocal)

    final_audio = f"{OUTPUT_DIR}/{base}_FINAL.mp3"
    mixed.export(final_audio, format="mp3", bitrate="192k")

    final_video = f"{OUTPUT_DIR}/{base}_FINAL.mp4"

    # -----------------------------
    # NEW SAFE FFMPEG USING TEXTFILE
    # -----------------------------
    cmd = f'''
    ffmpeg -y -i "{final_audio}" -f lavfi -i color=c=black:s=1280x720:d=300 \
    -filter_complex "\
    [0:a]showwaves=s=1280x200:mode=cline:colors=#00ff00[v];\
    [1:v][v]overlay=0:0[bg];\
    [bg]drawtext=text='{safe_title}':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=100:box=1:boxcolor=black@0.8,\
    drawtext=textfile='{lyrics_file}':fontcolor=yellow:fontsize=40:x=(w-text_w)/2:y=h-th-150\
    " \
    -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 192k -shortest "{final_video}"
    '''

    subprocess.run(cmd, shell=True, check=True)

    os.system(f"cp '{final_video}' '{PUBLIC_DIR}/'")

    print("Uploading to GitHub...")
    upload_to_github(final_audio)
    upload_to_github(final_video)

    print("Generation completed!")
