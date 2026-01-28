import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote

# ===================== CONFIGURATION =====================
INPUT_DIR = r"D:\Steam Project\Get the tags"
OUTPUT_DIR = r"D:\Steam Project\Get the tags\Output"

DELAY_SECONDS = 5  # Conservative delay to respect Steam's robots.txt and prevent IP bans
MAX_GAMES = 0      # Set to a positive number to limit the scrape (useful for testing)
ASK_START_ROW = False
# ==========================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Modern browser User-Agent to ensure the store page renders correctly
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def find_game_page(game_name):
    """Automates the Steam search bar to find the URL of a specific game."""
    search_url = "https://store.steampowered.com/search/?term=" + quote(game_name)
    r = requests.get(search_url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    # Locate the first search result link
    result = soup.select_one("a.search_result_row")
    return result["href"] if result else None

def extract_english_tags(game_url):
    """Navigates to the game page and extracts all user-defined tags in English."""
    game_url += "&l=english" # Force English tags for database consistency

    r = requests.get(game_url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    # Select all elements with the 'app_tag' class
    tags = [
        tag.get_text(strip=True)
        for tag in soup.select("a.app_tag")
        if tag.get_text(strip=True)
    ]

    return list(dict.fromkeys(tags))  # Remove duplicates while preserving list order

def process_csv(path):
    """Processes a CSV of game names and fetches tags for each entry."""
    df = pd.read_csv(path)
    names = df.iloc[:, 0].dropna().tolist()

    # Logic to resume scraping from a specific point
    start_index = 0
    if ASK_START_ROW:
        try:
            start = int(input("Start from which row (1 = first game)? "))
            start_index = max(start - 1, 0)
        except ValueError:
            start_index = 0

    # Limit the list of names if MAX_GAMES is set
    if MAX_GAMES > 0:
        names = names[start_index:start_index + MAX_GAMES]
    else:
        names = names[start_index:]

    rows = []

    for i, name in enumerate(names, start_index + 1):
        print(f"[Row {i}] Scrapping tags for: {name}")

        try:
            url = find_game_page(name)
            if not url:
                print("  ❌ Game not found on Steam")
                tags = []
            else:
                tags = extract_english_tags(url)
                print(f"  ✅ Found {len(tags)} tags")

        except Exception as e:
            print(f"  ⚠️ Scraping Error: {e}")
            tags = []

        # Store results as a comma-separated string for easier CSV storage
        rows.append({
            "name": name,
            "tags": ",".join(tags)
        })

        # Mandatory sleep to prevent rate-limiting (429 errors)
        time.sleep(DELAY_SECONDS)

    return pd.DataFrame(rows)

def run():
    """Batch processes all CSV files in the input directory."""
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".csv"):
            print(f"\n--- Starting Batch: {file} ---")
            df = process_csv(os.path.join(INPUT_DIR, file))
            
            out_path = os.path.join(OUTPUT_DIR, file)
            df.to_csv(out_path, index=False, encoding="utf-8")
            print(f"✅ Exported tagged data to: {out_path}")

if __name__ == "__main__":
    run()