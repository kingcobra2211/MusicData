import os
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

BASE_DIR = r"D:\MusicData"

deleted = 0
renamed = 0
skipped = 0


def get_track(path):
    try:
        audio = EasyID3(path)
        track = audio.get("tracknumber", [""])[0]
        return track.split("/")[0].strip()
    except:
        return ""


def get_title(path):
    try:
        audio = EasyID3(path)
        return audio.get("title", [""])[0].strip().lower()
    except:
        return ""


for album in os.listdir(BASE_DIR):

    album_path = os.path.join(BASE_DIR, album)

    if not os.path.isdir(album_path):
        continue

    print(f"\n📁 {album}")

    groups = {}

    # Group by Track Number
    for file in os.listdir(album_path):

        if not file.lower().endswith(".mp3"):
            continue

        path = os.path.join(album_path, file)

        track = get_track(path)

        # if metadata missing use filename
        if not track:
            track = os.path.splitext(file)[0].replace(" Song", "").lower()

        groups.setdefault(track, []).append(file)

    # Process each track
    for track, files in groups.items():

        if len(files) == 1:

            file = files[0]

            if not file.endswith(" Song.mp3"):

                old = os.path.join(album_path, file)

                base = os.path.splitext(file)[0]

                new = base + " Song.mp3"

                new_path = os.path.join(album_path, new)

                if not os.path.exists(new_path):
                    os.rename(old, new_path)
                    renamed += 1
                    print(f"✏️ {file}  ->  {new}")
                else:
                    skipped += 1

            continue

        # duplicates

        song_version = None
        normal_version = None

        for f in files:

            if f.endswith(" Song.mp3"):
                song_version = f
            else:
                normal_version = f

        if song_version and normal_version:

            delete_path = os.path.join(album_path, normal_version)

            os.remove(delete_path)

            deleted += 1

            print(f"🗑 Deleted duplicate: {normal_version}")

        else:
            print(f"⚠ Multiple files for Track {track}")
            for f in files:
                print("   ", f)

print("\n========================")
print("Renamed :", renamed)
print("Deleted :", deleted)
print("Skipped :", skipped)
print("========================")