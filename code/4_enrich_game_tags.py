import os
import pandas as pd

# ================== CONFIGURATION ==================
# Directories for input raw data and normalized output
INPUT_DIR = r"D:\Steam Project\Tag into Id\Input"
OUTPUT_DIR = r"D:\Steam Project\Tag into Id\Output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ===================================================

# Load existing master tag list to maintain consistency across different runs
tags_csv_path = os.path.join(OUTPUT_DIR, "tags.csv")
if os.path.exists(tags_csv_path):
    existing_tags_df = pd.read_csv(tags_csv_path)
    # Create a lookup dictionary for fast ID retrieval
    tag_to_id = dict(zip(existing_tags_df['tag_name'], existing_tags_df['id']))
    next_id = existing_tags_df['id'].max() + 1
    print(f"Loaded {len(tag_to_id)} existing tags, next ID = {next_id}")
else:
    tag_to_id = {}
    next_id = 1

def process_file(path):
    """
    Parses each CSV, splits comma-separated tags, and maps them to unique IDs.
    Returns a list of dictionaries connecting games to tag IDs.
    """
    global next_id
    df = pd.read_csv(path)
    game_tag_rows = []
    
    for _, row in df.iterrows():
        game_name = row['name']
        # Split the tag string into individual elements
        tags = str(row['tags']).split(",")
        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue

            # Assign a new ID only if the tag hasn't been encountered before
            if tag not in tag_to_id:
                tag_to_id[tag] = next_id
                next_id += 1

            # Create the link between the Game and the Tag ID (Junction Row)
            game_tag_rows.append({
                'game_name': game_name,
                'tag_id': tag_to_id[tag]
            })
    
    return game_tag_rows

def run():
    """Batch processes all input files and exports normalized relational tables."""
    all_game_tag_rows = []
    
    # Process every CSV in the input directory
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".csv"):
            path = os.path.join(INPUT_DIR, file)
            print(f"Normalizing tags in: {file}")
            rows = process_file(path)
            all_game_tag_rows.extend(rows)
    
    # Export the Master Tag List (The 'tag' dimension table)
    tags_df = pd.DataFrame(list(tag_to_id.items()), columns=['tag_name', 'id'])
    tags_df = tags_df[['id', 'tag_name']]  # Ensure ID is the first column
    tags_df.to_csv(tags_csv_path, index=False, encoding="utf-8")
    print(f"✅ Updated master list: tags.csv ({len(tags_df)} unique tags)")
    
    # Export the Game-Tag Mapping (The 'game_tag' junction table)
    game_tag_df = pd.DataFrame(all_game_tag_rows)
    game_tag_df.to_csv(os.path.join(OUTPUT_DIR, "game_tag.csv"), index=False, encoding="utf-8")
    print(f"✅ Created junction table: game_tag.csv ({len(game_tag_df)} associations)")

if __name__ == "__main__":
    run()