import os
import re

BASE_DIR = r"D:\Personal_project\MusicData_Scripts\MusicData"

def clean_filename(filename):
    name, ext = os.path.splitext(filename)

    # remove everything from '['
    name = re.sub(r'\[.*$', '', name)

    # clean extra spaces
    name = re.sub(r'\s+', ' ', name).strip()

    return name + ext


def process_folder(folder):
    for file in os.listdir(folder):
        if not file.endswith(".mp3"):
            continue

        if "[" not in file:
            continue

        old_path = os.path.join(folder, file)
        new_name = clean_filename(file)
        new_path = os.path.join(folder, new_name)

        # avoid overwrite
        if os.path.exists(new_path):
            print(f"⚠️ Already exists, skipping: {new_name}")
            continue

        print(f"🔄 Renaming:\n   {file}\n   → {new_name}")
        os.rename(old_path, new_path)


def process_all():
    for album in os.listdir(BASE_DIR):
        path = os.path.join(BASE_DIR, album)

        if os.path.isdir(path):
            print(f"\n📁 Processing: {album}")
            process_folder(path)


if __name__ == "__main__":
    process_all()