import os
import requests
from pathlib import Path
import sys

# Constants
GITHUB_API_BASE = "https://api.github.com/repos/github/codeql/contents/python/ql/src/Security"
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data/queries/python/issues"
HEADERS = {}

# Check for GitHub Token
token = os.environ.get("GITHUB_TOKEN")
if token:
    HEADERS["Authorization"] = f"token {token}"
else:
    print("Warning: No GITHUB_TOKEN found. API rate limits may apply.")

def fetch_contents(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching {url}: {response.status_code}")
        return []
    return response.json()

def download_file(download_url, file_name):
    print(f"Downloading {file_name}...")
    response = requests.get(download_url, headers=HEADERS)
    if response.status_code == 200:
        file_path = os.path.join(OUTPUT_DIR, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(response.text)
    else:
        print(f"Failed to download {file_name}")

def traverse_and_download(url):
    items = fetch_contents(url)
    for item in items:
        if item["type"] == "dir":
            # Recursively explore directories (like CWE-xxx)
            traverse_and_download(item["url"])
        elif item["type"] == "file" and item["name"].endswith(".ql"):
            # Download .ql files
            download_file(item["download_url"], item["name"])

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Starting download of Python Security queries to {OUTPUT_DIR}...")
    traverse_and_download(GITHUB_API_BASE)
    print("Download complete.")

if __name__ == "__main__":
    main()
