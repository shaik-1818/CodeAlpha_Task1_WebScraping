# =============================================================================
# CodeAlpha Data Analytics Internship
# TASK 1 — Web Scraping
# Topic  : IPL 2025 Batting Statistics
# Source : Wikipedia (public, no login required)
# Tools  : requests, BeautifulSoup, pandas
# Author : [Your Name]
# =============================================================================

# ── STEP 0 : Install libraries (run once in terminal) ──────────────────────
# pip install requests beautifulsoup4 pandas lxml

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

print("=" * 60)
print("  CodeAlpha — Task 1 : Web Scraping")
print("  Scraping IPL 2025 Stats from Wikipedia")
print("=" * 60)

# ── STEP 1 : Setup ────────────────────────────────────────────────────────
# Headers mimic a real browser so the website doesn't block us
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Wikipedia page for IPL 2025
URL = "https://en.wikipedia.org/wiki/2025_Indian_Premier_League"

# Output folder
os.makedirs("scraped_data", exist_ok=True)

# ── STEP 2 : Fetch the Page ───────────────────────────────────────────────
print("\n[1/5] Connecting to Wikipedia...")

try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()           # raises error if status != 200
    print(f"      ✅ Connected! Status Code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("      ❌ No internet connection. Please check your network.")
    exit()
except requests.exceptions.Timeout:
    print("      ❌ Request timed out. Try again.")
    exit()
except requests.exceptions.HTTPError as e:
    print(f"      ❌ HTTP Error: {e}")
    exit()

# ── STEP 3 : Parse HTML ───────────────────────────────────────────────────
print("\n[2/5] Parsing HTML content...")
soup = BeautifulSoup(response.text, "lxml")

# Find all tables with class 'wikitable'
all_tables = soup.find_all("table", class_="wikitable")
print(f"      Found {len(all_tables)} tables on the page")

# ── STEP 4 : Extract Tables ───────────────────────────────────────────────
print("\n[3/5] Extracting data from tables...")

scraped_tables = {}   # store all tables by name

for idx, table in enumerate(all_tables):
    # Get table caption/heading
    caption = table.find("caption")
    table_name = caption.get_text(strip=True) if caption else f"Table_{idx+1}"

    rows = table.find_all("tr")
    table_data = []

    # Extract headers from the first row
    headers_row = rows[0].find_all(["th", "td"])
    col_headers = [h.get_text(strip=True) for h in headers_row]

    # Extract data rows
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        row_data = [cell.get_text(strip=True) for cell in cells]

        # Only add rows that have same length as headers
        if len(row_data) == len(col_headers):
            table_data.append(row_data)

    if table_data and col_headers:
        df = pd.DataFrame(table_data, columns=col_headers)
        scraped_tables[table_name] = df
        print(f"      ✅ Table {idx+1}: '{table_name[:50]}' → {df.shape[0]} rows × {df.shape[1]} cols")

# ── STEP 5 : Save to CSV ──────────────────────────────────────────────────
print("\n[4/5] Saving scraped data to CSV files...")

saved_files = []
for name, df in scraped_tables.items():
    # Clean filename (remove special characters)
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    safe_name = safe_name[:50].strip().replace(" ", "_")
    filename = f"scraped_data/{safe_name}.csv"

    df.to_csv(filename, index=False, encoding="utf-8")
    saved_files.append(filename)
    print(f"      💾 Saved: {filename}")

# ── STEP 6 : Also scrape specific team-wise data from IPL pages ──────────
print("\n[5/5] Scraping individual IPL team pages for extra data...")

# IPL 2025 team Wikipedia pages (bonus scraping)
TEAM_URLS = {
    "GT":   "https://en.wikipedia.org/wiki/Gujarat_Titans_in_IPL_2025",
    "MI":   "https://en.wikipedia.org/wiki/Mumbai_Indians_in_IPL_2025",
    "RCB":  "https://en.wikipedia.org/wiki/Royal_Challengers_Bengaluru_in_IPL_2025",
    "CSK":  "https://en.wikipedia.org/wiki/Chennai_Super_Kings_in_IPL_2025",
}

team_summaries = []

for team, team_url in TEAM_URLS.items():
    try:
        time.sleep(1)   # polite delay between requests
        resp = requests.get(team_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            tsoup = BeautifulSoup(resp.text, "lxml")
            # Extract introductory text (first paragraph)
            intro = tsoup.find("div", class_="mw-parser-output")
            first_para = intro.find("p").get_text(strip=True) if intro else "N/A"
            team_summaries.append({"Team": team, "URL": team_url, "Summary": first_para[:200]})
            print(f"      ✅ {team} page scraped")
        else:
            print(f"      ⚠️  {team}: Status {resp.status_code}")
    except Exception as e:
        print(f"      ⚠️  {team}: {e}")

if team_summaries:
    df_teams = pd.DataFrame(team_summaries)
    df_teams.to_csv("scraped_data/team_summaries.csv", index=False)
    print("      💾 Saved: scraped_data/team_summaries.csv")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  ✅  SCRAPING COMPLETE — SUMMARY")
print("=" * 60)
print(f"  • Total tables scraped : {len(scraped_tables)}")
print(f"  • Total files saved    : {len(saved_files) + (1 if team_summaries else 0)}")
print(f"  • Output folder        : scraped_data/")
print()
print("  Files created:")
for f in saved_files:
    print(f"    📄 {f}")
if team_summaries:
    print("    📄 scraped_data/team_summaries.csv")

print()
print("  Next Step → Open Task2_EDA.ipynb and load these CSV files")
print("=" * 60)
