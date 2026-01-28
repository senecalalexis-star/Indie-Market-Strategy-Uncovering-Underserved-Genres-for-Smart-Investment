# Steam Market Data Engineering Pipeline  
*Uncovering Underserved Indie Genres for Smart Investment*

This folder contains a **custom-built Python ETL and web-scraping ecosystem** designed to collect, normalize, and enrich Steam market data.  
The pipeline transforms **raw SteamDB exports and live Steam web data** into clean, relational CSV tables ready for SQL analysis and market research.

The architecture is modular and follows classic **data engineering best practices**: extraction, normalization, enrichment, and dimensional modeling.

---

## 1. SteamDB Text → Structured CSV  
**File:** `steamdb_txt_to_csv.py`

This script is the **entry point of the pipeline**. It converts raw `.txt` exports from SteamDB into clean, analysis-ready CSV files.

**Key Technical Features:**
- **Regex-Driven Parsing:** Detects ranked entries, skips discount markers (e.g. `-10%`), and adapts to inconsistent line structures.
- **Robust Data Normalization:**
  - Prices (`$`, `Free`, `—`) → numeric floats
  - Ratings (`85%`) → numeric values
  - Dates (`DD Mon + year from filename`) → ISO format (`YYYY-MM-DD`)
- **Schema Enforcement:** Ensures consistent column ordering for database ingestion.

**Output Columns:**
- `name`, `price`, `rating`, `release`, `follows`, `reviews`, `peak`

**Libraries Used:** `os`, `re`, `csv`, `datetime`

---

## 2. Steam AppID Resolution & Playtime Enrichment  
**Files:**  
- `steam_playtime_enrichment.py`

This module enriches the dataset with **official Steam identifiers** and **player engagement metrics** scraped from SteamSpy.

> ⚠️ N2, N3, and N5 are functionally identical versions of the same enrichment pipeline.

**Pipeline Logic:**
1. Resolve **Game Name → Steam AppID** using the Steam Store API
2. Scrape **average & median playtime** from SteamSpy
3. Persist results incrementally to CSV for fault tolerance

**Key Technical Features:**
- **Anti-Blocking Strategy:**
  - Randomized request delays
  - Browser-grade User-Agent headers
- **Resume-Safe Execution:** Allows restarting from any row after interruptions
- **Audit Logging:** Each AppID is timestamped (`UTC`) for traceability
- **Fault Isolation:** Failed games are skipped without stopping the pipeline

**Outputs:**
- `game_id.csv` → AppID mapping
- `steamspy_playtime.csv` → engagement metrics

**Libraries Used:**  
`requests`, `pandas`, `bs4 (BeautifulSoup)`, `time`, `random`, `datetime`

---

## 3. Steam Tag Scraper  
**File:** `get_steam_tags.py`

This script scrapes **user-defined Steam tags** directly from the Steam Store, enabling genre and thematic analysis.

**Key Technical Features:**
- **Automated Steam Search:** Simulates the Steam search bar to locate game pages
- **Language Normalization:** Forces English tags (`&l=english`) for dataset consistency
- **Rate-Limit Safe:** Conservative fixed delays to comply with Steam’s scraping policies
- **Resume & Batch Support:** Handles multiple CSV inputs seamlessly

**Output:**
- CSV files containing:
  - `name`
  - `tags` (comma-separated)

**Libraries Used:**  
`requests`, `pandas`, `bs4`, `urllib.parse`, `time`

---

## 4. Tag Normalization & Relational Modeling  
**File:** `tag_normalization.py`

This script converts raw tag strings into a **fully normalized relational structure**, suitable for SQL joins and dimensional modeling.

**Key Technical Features:**
- **Master Data Management (MDM):**
  - Maintains a persistent `tags.csv` dimension table
  - Guarantees stable tag IDs across multiple runs
- **Automatic ID Assignment:** New tags are assigned incrementally without collisions
- **Junction Table Creation:** Builds a many-to-many `game_tag` table

**Outputs:**
- `tags.csv` → Tag dimension table  
- `game_tag.csv` → Game-Tag junction table

**Relational Model:**
- `game (name)` ⟷ `game_tag` ⟷ `tag (id, tag_name)`

**Libraries Used:** `pandas`, `os`

---

## End-to-End Data Flow

