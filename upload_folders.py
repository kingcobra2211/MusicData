import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRANCH = "main"
REMOTE = "origin"

# Files/folders that should NEVER be uploaded as albums
IGNORE = {
    ".git",
    ".git_old_backup",
    "resume_upload.py",
    "upload_folders.py",
}

# Root-level files to upload only after all albums
ROOT_FILES = {
    "AlbumImageFind.py",
    "MusiDirector_Year.txt",
    "SongsCleaning.py",
    "cleanup_duplicate_songs.py",
    "generate_or_update_songs_with_details.py",
    "generate_songs_json.py",
    "songs.json",
    "songs_with_details.json",
    "songs_with_details_backup.json",
    "README.md",
}


def run(cmd):
    print("\n>", " ".join(str(x) for x in cmd))

    result = subprocess.run(
        cmd,
        cwd=ROOT
    )

    if result.returncode != 0:
        print("\n❌ COMMAND FAILED")
        print(" ".join(str(x) for x in cmd))
        sys.exit(result.returncode)


def is_tracked(path):
    """
    Check whether the folder/file is already tracked by Git.
    """
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


def folder_size_gb(folder):
    total = 0

    for file in folder.rglob("*"):
        if file.is_file():
            try:
                total += file.stat().st_size
            except OSError:
                pass

    return total / (1024 ** 3)


def main():

    print("=" * 65)
    print("MusicData - RESUME Album-by-Album GitHub Uploader")
    print("=" * 65)

    # ---------------------------------------------------------
    # Check Git
    # ---------------------------------------------------------

    if not (ROOT / ".git").exists():
        print("\n❌ .git not found.")
        print("This script must be run inside D:\\MusicData")
        sys.exit(1)

    # ---------------------------------------------------------
    # Check remote
    # ---------------------------------------------------------

    print("\nCurrent remote:")

    run(["git", "remote", "-v"])

    # ---------------------------------------------------------
    # Check current branch
    # ---------------------------------------------------------

    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        capture_output=True,
        text=True
    )

    branch = result.stdout.strip()

    if branch != BRANCH:
        print(f"\n⚠️ Current branch is: {branch}")
        print(f"Switching to {BRANCH}...")
        run(["git", "checkout", BRANCH])

    # ---------------------------------------------------------
    # Get folders
    # ---------------------------------------------------------

    folders = []

    for item in ROOT.iterdir():

        if not item.is_dir():
            continue

        if item.name in IGNORE:
            continue

        if item.name.startswith("."):
            continue

        folders.append(item)

    folders.sort(key=lambda x: x.name.lower())

    print(f"\nTotal album folders found: {len(folders)}")

    # ---------------------------------------------------------
    # Upload folders
    # ---------------------------------------------------------

    uploaded = 0
    skipped = 0

    for index, folder in enumerate(folders, 1):

        print("\n")
        print("=" * 65)
        print(f"[{index}/{len(folders)}] {folder.name}")
        print("=" * 65)

        # -----------------------------------------------------
        # Already tracked?
        # -----------------------------------------------------

        if is_tracked(folder.name):

            print("✅ Already uploaded/tracked. Skipping.")
            skipped += 1
            continue

        # -----------------------------------------------------
        # Folder size
        # -----------------------------------------------------

        size = folder_size_gb(folder)

        print(f"Folder size: {size:.2f} GB")

        # -----------------------------------------------------
        # Protect against >2 GB push
        # -----------------------------------------------------

        if size >= 1.8:

            print("\n⚠️ WARNING")
            print("This album is close to GitHub's 2 GB push limit.")

            answer = input(
                "Do you want to continue? (YES/NO): "
            )

            if answer.strip().upper() != "YES":
                print("⏭️ Skipping:", folder.name)
                skipped += 1
                continue

        # -----------------------------------------------------
        # Add album
        # -----------------------------------------------------

        run([
            "git",
            "add",
            "--",
            folder.name
        ])

        # -----------------------------------------------------
        # Check staged changes
        # -----------------------------------------------------

        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT
        )

        if result.returncode == 0:

            print("⚠️ Nothing new to commit.")
            skipped += 1
            continue

        # -----------------------------------------------------
        # Commit
        # -----------------------------------------------------

        run([
            "git",
            "commit",
            "-m",
            f"Add album: {folder.name}"
        ])

        # -----------------------------------------------------
        # Push
        # -----------------------------------------------------

        run([
            "git",
            "push",
            "origin",
            BRANCH
        ])

        print(f"\n✅ SUCCESS: {folder.name}")

        uploaded += 1

    # ---------------------------------------------------------
    # Root files
    # ---------------------------------------------------------

    print("\n")
    print("=" * 65)
    print("Uploading root files")
    print("=" * 65)

    root_files_to_add = []

    for filename in ROOT_FILES:

        path = ROOT / filename

        if path.exists() and not is_tracked(filename):
            root_files_to_add.append(filename)

    if root_files_to_add:

        print("\nFiles to upload:")

        for filename in root_files_to_add:
            print("  ", filename)
            run([
                "git",
                "add",
                "--",
                filename
            ])

        run([
            "git",
            "commit",
            "-m",
            "Add repository metadata and JSON files"
        ])

        run([
            "git",
            "push",
            "origin",
            BRANCH
        ])

    # ---------------------------------------------------------
    # Final status
    # ---------------------------------------------------------

    print("\n")
    print("=" * 65)
    print("🎉 RESUME UPLOAD FINISHED")
    print("=" * 65)

    print(f"\nUploaded this run : {uploaded}")
    print(f"Skipped           : {skipped}")

    print("\nCurrent Git status:")
    run(["git", "status", "--short"])

    print("\n✅ Repository:")
    print("https://github.com/kingcobra2211/MusicData")


if __name__ == "__main__":
    main()