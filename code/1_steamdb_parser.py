import os
import re
import csv
from datetime import datetime

# --- CONFIGURATION ---
# Define source directory for raw text files and target for cleaned CSVs
INPUT_DIR = r"D:\Steam Project\STEAM DB TEXT"
OUTPUT_DIR = r"D:\Steam Project\CSV STEAM DB"

# Ensure output directory exists before starting
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mapping for date normalization
MONTHS = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

def normalize_price(value):
    """Converts price strings to floats, handling 'Free' and null markers."""
    if value in ("Free", "—"):
        return 0.0
    return float(value.replace("$", ""))

def normalize_date(day_month, year):
    """Transforms 'DD Mon' and year into ISO format YYYY-MM-DD."""
    day, month = day_month.split()
    return f"{year}-{MONTHS[month]}-{int(day):02d}"

def parse_txt_file(path):
    """
    Parses SteamDB raw text data into structured rows.
    Uses regex to handle varying line structures like rankings and discounts.
    """
    # Extract the year from the filename (e.g., '2024.txt' -> '2024')
    year = os.path.splitext(os.path.basename(path))[0]
    rows = []

    with open(path, encoding="utf-8") as f:
        # Remove empty lines and whitespace
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    while i < len(lines):
        # 1. Detect Ranking: Look for patterns like '35.'
        if re.match(r"^\d+\.$", lines[i]):
            name = lines[i + 1] # The line after the number is the Game Name
            i += 2

            # 2. Handle Discounts: Skip lines like '-10%' if they exist
            if re.match(r"^-\d+%$", lines[i]):
                i += 1

            # 3. Data Extraction: Split the tab-separated metrics
            data = lines[i]
            i += 1

            parts = data.split("\t")

            # Transform raw strings into proper data types for database ingestion
            price = normalize_price(parts[0])
            rating = float(parts[1].replace("%", ""))
            release = normalize_date(parts[2], year)
            follows = int(parts[3].replace(",", ""))
            reviews = int(parts[4].replace(",", ""))
            peak = int(parts[5].replace(",", ""))

            rows.append([
                name, price, rating, release, follows, reviews, peak
            ])
        else:
            i += 1 # Continue searching for next entry

    return rows

def convert_all_files():
    """Main execution loop to batch process all .txt files in the input directory."""
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".txt"):
            input_path = os.path.join(INPUT_DIR, file)
            output_path = os.path.join(
                OUTPUT_DIR,
                file.replace(".txt", ".csv")
            )

            # Process the file
            rows = parse_txt_file(input_path)

            # Write results to CSV with headers
            with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "name", "price", "rating",
                    "release", "follows", "reviews", "peak"
                ])
                writer.writerows(rows)

            print(f"Successfully Processed: {file} → {os.path.basename(output_path)}")

if __name__ == "__main__":
    convert_all_files()