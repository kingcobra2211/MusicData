import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

BASE_DIR = r"D:\Personal_project\MusicData_Scripts\MusicData"
URL_FILE = "albumUrls.txt"

def is_valid_url(url):
    return url.startswith("http")

def fetch_html(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def extract_image_url(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    # Try finding main album image (usually first big image)
    img_tag = soup.find("img")

    if img_tag and img_tag.get("src"):
        return urljoin(base_url, img_tag["src"])

    return None

def download_and_save_image(img_url, save_path):
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img = img.convert("RGB")  # Ensure PNG compatibility
            img.save(save_path, "PNG")
            print(f"Saved: {save_path}")
    except Exception as e:
        print(f"Error saving image: {e}")

def process():
    file_path = os.path.join(BASE_DIR, URL_FILE)

    if not os.path.exists(file_path):
        print("albumUrls.txt not found")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if ":" not in line:
            continue

        album_name, url = line.split(":", 1)
        album_name = album_name.strip()
        url = url.strip()

        if not is_valid_url(url):
            print(f"Skipping invalid URL: {url}")
            continue

        album_folder = os.path.join(BASE_DIR, album_name)

        if not os.path.exists(album_folder):
            print(f"Folder not found: {album_name}")
            continue

        print(f"Processing: {album_name}")

        html = fetch_html(url)
        if not html:
            continue

        img_url = extract_image_url(html, url)
        if not img_url:
            print(f"No image found for {album_name}")
            continue

        save_path = os.path.join(album_folder, f"{album_name}.png")

        download_and_save_image(img_url, save_path)


if __name__ == "__main__":
    process()