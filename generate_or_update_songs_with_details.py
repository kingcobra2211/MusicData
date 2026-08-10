import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
import mutagen
from mutagen.mp3 import MP3
from urllib.parse import quote

# Configuration
BASE_PATH = Path(r"D:\MusicData")
METADATA_FILE = BASE_PATH / "MusiDirector_Year.txt"
JSON_FILE = BASE_PATH / "songs_with_details.json"
SUPPORTED_IMAGE_EXTS = ['.png', '.jpg', '.jpeg', '.webp']

            
def normalize(name):
    return " ".join(
        name.lower()
            .replace("–", "-")
            .replace("_", " ")
            .split()
    )

def get_album_metadata():
    if not METADATA_FILE.exists():
        return {}
    try:
        content = METADATA_FILE.read_text(encoding='utf-8')
        # Extracting the dictionary string manually or using ast.literal_eval is safer
        import ast
        # Assuming the file content is exactly: ALBUM_METADATA = {...}
        code = compile(content, "<string>", "exec")
        context = {}
        exec(code, context)
        metadata = context.get("ALBUM_METADATA", {})

        return {
            normalize(k): v
            for k, v in metadata.items()
        }
        
    except Exception:
        return {}

def get_stable_id(val: str) -> str:
    return hashlib.sha256(val.lower().encode()).hexdigest()[:12]

def find_album_image(album_path: Path, album_name: str) -> str:

    possible_names = [
        f"{album_name}.png",
        f"{album_name}.jpg",
        f"{album_name}.jpeg",
        "folder.png",
        "folder.jpg",
        "cover.png",
        "cover.jpg",
        "cover.jpeg"
    ]
    for name in possible_names:
        p = album_path / name
        if p.exists():
            return name
    
    # Check for any image extension
    for ext in SUPPORTED_IMAGE_EXTS:
        for f in album_path.glob(f"*{ext}"):
            return f.name
    return ""

def process_mp3(file_path: Path):
    try:
        audio = MP3(file_path)
        duration = int(audio.info.length)
        minutes = duration // 60
        seconds = duration % 60
        duration_str = f"{minutes}:{seconds:02d}"
        
        return {
            "duration": duration_str,
            "bitrate": int(audio.info.bitrate),
            "sampleRate": int(audio.info.sample_rate),
            "channels": int(audio.info.channels),
            "fileSize": file_path.stat().st_size
        }
    except Exception:
        return {"duration": "0:00", "bitrate": 0, "sampleRate": 0, "channels": 0, "fileSize": 0}

def main():
    metadata = get_album_metadata()
    existing_songs = []
    if JSON_FILE.exists():
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            existing_songs = json.load(f)

    existing_keys = {
        (
            s.get("album", "").strip().lower(),
            s.get("title", "").strip().lower()
        )
    
        for s in existing_songs
    }
    
    existing_song_map = {
        (
            s.get("album", "").strip().lower(),
            s.get("title", "").strip().lower()
        ): s
        for s in existing_songs
    }
    
    new_songs = []
    
    albums_processed = 0
    songs_added = 0
    songs_skipped = 0
    unknown_metadata = 0

    for album_dir in BASE_PATH.iterdir():
        if album_dir.is_dir():
            albums_processed += 1
            album_name = album_dir.name
            
            album_meta = metadata.get(
                normalize(album_name),
                {
                    "musicDirector": "Unknown",
                    "year": "Unknown"
                }
            )
            
            if album_meta["musicDirector"] == "Unknown":
                unknown_metadata += 1
            
            image_name = find_album_image(album_dir, album_name)
            
            for track_number, mp3_file in enumerate(sorted(album_dir.glob("*.mp3")), start=1):
                song_title = mp3_file.stem
                
                song_key = (
                    album_name.strip().lower(),
                    song_title.strip().lower()
                )

                if song_key in existing_keys:
                    existing_song = existing_song_map[song_key]
                
                    existing_song["musicDirector"] = album_meta["musicDirector"]
                    existing_song["artist"] = album_meta["musicDirector"]
                    existing_song["composer"] = album_meta["musicDirector"]
                    existing_song["year"] = album_meta["year"]
                
                    if image_name:
                        image_url = (
                            f"https://raw.githubusercontent.com/vamshivamshi9630/MusicData/main/"
                            f"{quote(album_name)}/{quote(image_name)}"
                        )
                
                        existing_song["albumImageUrl"] = image_url
                        existing_song["thumbnailUrl"] = image_url
                
                    songs_skipped += 1
                    continue
                
                mp3_info = process_mp3(mp3_file)
                
                # Build object using template structure
                song_data = {
                    "id": get_stable_id(f"{album_name}{song_title}"),
                    "title": song_title,
                    "subtitle": f"From {album_name}",
                    "album": album_name,
                    "albumId": get_stable_id(album_name),
                    "artist": album_meta["musicDirector"],
                    "artistId": get_stable_id(album_meta["musicDirector"]),
                    "musicDirector": album_meta["musicDirector"],
                    "composer": album_meta["musicDirector"],
                    "lyricist": "Unknown",
                    "singers": [album_meta["musicDirector"]],
                    "featuredArtists": [],
                    "genre": "Tollywood Soundtrack",
                    "language": "Telugu",
                    "country": "India",
                    "year": album_meta["year"],
                    "releaseDate": f"{album_meta['year']}-01-01" if album_meta["year"] != "Unknown" else "2026-01-01",
                    "trackNumber": track_number,
                    "discNumber": 1,
                    "duration": mp3_info["duration"],
                    "audioUrl": (
                        f"https://raw.githubusercontent.com/vamshivamshi9630/MusicData/main/"
                        f"{quote(album_name)}/{quote(mp3_file.name)}"
                    ),

                    "albumImageUrl": (
                        f"https://raw.githubusercontent.com/vamshivamshi9630/MusicData/main/"
                        f"{quote(album_name)}/{quote(image_name)}"
                    ) if image_name else "",

                    "thumbnailUrl": (
                        f"https://raw.githubusercontent.com/vamshivamshi9630/MusicData/main/"
                        f"{quote(album_name)}/{quote(image_name)}"
                    ) if image_name else "",
                    "bannerUrl": "", "lyrics": "", "lyricsUrl": "", "youtubeUrl": "", "videoUrl": "", "previewUrl": "",
                    "bitrate": mp3_info["bitrate"],
                    "codec": "mp3",
                    "sampleRate": mp3_info["sampleRate"],
                    "channels": mp3_info["channels"],
                    "fileSize": mp3_info["fileSize"],
                    "rating": 4.5, "likes": 0, "views": 0, "popularity": 0,
                    "favorite": False, "downloaded": False, "playCount": 0, "downloadCount": 0, "shareCount": 0,
                    "isTrending": False, "isLatest": False, "isRecommended": False, "isExplicit": False,
                    "tags": ["Telugu", "Tollywood", album_name],
                    "relatedSongs": [],
                    "credits": {"Composer": album_meta["musicDirector"], "Singer": album_meta["musicDirector"]},
                    "createdAt": datetime.now().isoformat() + "Z",
                    "updatedAt": datetime.now().isoformat() + "Z"
                }
                new_songs.append(song_data)
                existing_keys.add(song_key)
                songs_added += 1

    all_songs = existing_songs + new_songs

    all_songs.sort(
        key=lambda x: (
            x.get("album", ""),
            x.get("trackNumber", 0),
            x.get("title", "")
        )
    )
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(all_songs, f, indent=4, ensure_ascii=False)

    print(f"Albums Processed: {albums_processed}")
    print(f"Songs Added: {songs_added}")
    print(f"Songs Skipped: {songs_skipped}")
    print(f"Unknown Metadata: {unknown_metadata}")
    print(f"Total Songs: {len(existing_songs) + songs_added}")
    print(f"Output File: {JSON_FILE}")

if __name__ == "__main__":
    main()