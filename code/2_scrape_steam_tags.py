import requests
import pandas as pd
import time
import random
import os
import glob
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# =========================
# SETTINGS & ANTI-BLOCKING
# =========================
BASE_DELAY = 2.5  # Average wait time between requests
JITTER = 1.0      # Randomness added to delay to mimic human behavior

INPUT_FOLDER = r"D:\Steam Project\Get the review\Input"
OUTPUT_FOLDER = r"D:\Steam Project\Get the review"

GAME_ID_FILE = os.path.join(OUTPUT_FOLDER, "game_id.csv")
STEAMSPY_FILE = os.path.join(OUTPUT_FOLDER, "steamspy_playtime.csv")

# Identify as a standard browser to avoid basic bot detection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# =========================
# HELPERS
# =========================
def human_sleep():
    """Implements a randomized sleep timer to stay under rate limits."""
    delay = max(1.0, BASE_DELAY + random.uniform(-JITTER, JITTER))
    print(f"Sleeping {delay:.2f}s...")
    time.sleep(delay)

def safe_append(df, path):
    """Writes data to CSV, handling file-locking issues common in batch processing."""
    for _ in range(5):
        try:
            if os.path.exists(path):
                df.to_csv(path, mode="a", index=False, header=False)
            else:
                df.to_csv(path, index=False)
            return
        except PermissionError:
            print("File locked, retrying...")
            time.sleep(2)
    raise PermissionError(f"Could not write to {path}")

def get_appid_from_name(game_name):
    """Queries Steam Store API to resolve a Game Name into an AppID."""
    url = f"https://store.steampowered.com/api/storesearch/?term={game_name}&cc=FR"
    resp = requests.get(url, headers=HEADERS, timeout=30).json()
    if resp.get("total", 0) == 0:
        raise ValueError(f"Game '{game_name}' not found on Steam")
    return resp["items"][0]["id"]

def parse_playtime_text(text):
    """
    Converts 'HH:MM' time strings into integer minutes for numerical analysis.
    Example: '25:17' -> 1517 minutes
    """
    try:
        parts = text.strip().split()
        avg_h, avg_m = map(int, parts[0].split(":"))
        med_h, med_m = map(int, parts[2].split(":"))
        avg_minutes = avg_h * 60 + avg_m
        median_minutes = med_h * 60 + med_m
        return avg_minutes, median_minutes
    except Exception as e:
        print(f"⚠️ Parsing error on '{text}': {e}")
        return None, None

def fetch_steamspy_playtime(appid, game_name):
    """Scrapes SteamSpy HTML for playtime statistics using BeautifulSoup."""
    url = f"https://steamspy.com/app/{appid}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            return None, None
        
        soup = BeautifulSoup(resp.text, "html.parser")
        strong_tag = soup.find("strong", string="Playtime total:")
        
        if not strong_tag:
            return None, None
            
        text = strong_tag.next_sibling
        avg_minutes, median_minutes = parse_playtime_text(text)
        return avg_minutes, median_minutes
    except Exception as e:
        print(f"❌ SteamSpy Scrape Error for {game_name}: {e}")
        return None, None

# =========================
# EXECUTION PIPELINE
# =========================
def main():
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    csvs = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))
    if not csvs:
        print("Error: No input CSV found.")
        return

    input_csv = csvs[0]
    start_row = int(input("Enter row to start from (allows resuming interrupted sessions): "))

    # Read game names from the first column of the input file
    games = pd.read_csv(input_csv).iloc[:, 0]

    for idx in range(start_row, len(games)):
        game_name = str(games.iloc[idx]).strip()
        print(f"\n[{idx}] Processing '{game_name}'")

        try:
            # 1. Fetch AppID from Steam API
            appid = get_appid_from_name(game_name)
            
            # Log the ID and timestamp (Auditing)
            collected_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            df_game_id = pd.DataFrame([{"app_id": appid, "game_name": game_name, "collected_at_utc": collected_at}])
            safe_append(df_game_id, GAME_ID_FILE)

            # 2. Fetch Performance Metrics from SteamSpy
            avg_minutes, median_minutes = fetch_steamspy_playtime(appid, game_name)
            df_playtime = pd.DataFrame([{
                "game_name": game_name, 
                "avg_playtime_minutes": avg_minutes, 
                "median_playtime_minutes": median_minutes
            }])
            safe_append(df_playtime, STEAMSPY_FILE)
            
        except Exception as e:
            print(f"❌ Skipping '{game_name}': {e}")
            continue

        human_sleep()

    print("\n✅ Enrichment complete. Playtime data exported to CSV.")

if __name__ == "__main__":
    main(