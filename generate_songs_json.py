# -*- coding: utf-8 -*-
import os
import json
import sys

try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3

try:
    import codecs
except ImportError:
    codecs = None

try:
    from collections import OrderedDict
except ImportError:
    # Fallback for Python < 2.7 (should not be needed)
    OrderedDict = dict

BASE_URL = "https://raw.githubusercontent.com/vamshivamshi9630/MusicData/main/"
OUTPUT_FILE = "songs.json"

# Load existing songs if file exists
if os.path.exists(OUTPUT_FILE):
    try:
        if codecs:
            with codecs.open(OUTPUT_FILE, "r", "utf-8") as f:
                existing_songs = json.load(f)
        else:
            with open(OUTPUT_FILE, "r") as f:
                existing_songs = json.load(f)
    except Exception:
        existing_songs = []
else:
    existing_songs = []

# Check if song already exists
def is_duplicate(song_name, album_name):
    for song in existing_songs:
        if song.get("name") == song_name and song.get("album") == album_name:
            return True
    return False

new_songs = []

# Process each album folder
for album_folder in sorted(os.listdir("."), reverse=True):
    if os.path.isdir(album_folder):
        album_image_url = None

        # Find album image
        for file in os.listdir(album_folder):
            if file.lower().endswith(".png"):
                album_image_url = BASE_URL + quote(album_folder) + "/" + quote(file)
                break

        # Process each .mp3 file
        for file in os.listdir(album_folder):
            if file.lower().endswith(".mp3"):
                song_name = os.path.splitext(file)[0]

                if not is_duplicate(song_name, album_folder):
                    song_url = BASE_URL + quote(album_folder) + "/" + quote(file)

                    new_songs.append(OrderedDict([
                        ("name", song_name),
                        ("album", album_folder),
                        ("url", song_url),
                        ("albumImageUrl", album_image_url)
                    ]))

# Prepend new songs
final_songs = new_songs + existing_songs

# Save to songs.json
try:
    if codecs:
        with codecs.open(OUTPUT_FILE, "w", "utf-8") as f:
            json.dump(final_songs, f, indent=2, ensure_ascii=False)
    else:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(final_songs, f, indent=2)
except Exception as e:
    print("❌ Error writing to songs.json:", e)
    sys.exit(1)

# Print summary
print("✅ songs.json updated: {} new songs added, {} total.".format(len(new_songs), len(final_songs)))
