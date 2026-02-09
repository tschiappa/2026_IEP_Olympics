"""
Scrapes the 2026 Winter Olympics medal table from Wikipedia
using the Firecrawl API and updates data/medals.csv
"""

import requests
import csv
import os
import re
import json

# Firecrawl API config
FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1/scrape"
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

# Wikipedia URL for 2026 Winter Olympics medal table
WIKI_URL = "https://en.wikipedia.org/wiki/2026_Winter_Olympics_medal_table"

# Normalize Wikipedia country names to match picks.csv conventions
COUNTRY_NAME_MAP = {
    "United States": "USA",
    "Republic of Korea": "South Korea",
    "Korean Republic": "South Korea",
    "Korea": "South Korea",
    "Peoples Republic of China": "China",
    "Chinese Taipei": "Chinese Taipei",
    "Great Britain": "Great Britain",
    "Russian Olympic Committee": "ROC",
    "Czechia": "Czech Republic",
}


def normalize_country(name):
    """Normalize a country name scraped from Wikipedia to match picks.csv."""
    # Strip markdown images FIRST, then links (order matters!)
    name = re.sub(r'!\[.*?\]\(.*?\)', '', name)  # remove markdown images
    name = re.sub(r'\[([^\]]*)\]\(.*?\)', r'\1', name)  # replace links with their text
    name = re.sub(r'[*†!\[\]()\\]', '', name)      # remove special chars
    name = name.strip()

    # Extract just the country name from remaining text
    # Wikipedia markdown often leaves the country name as plain text after image removal
    # e.g. "Norway" or "United States"
    name = re.sub(r'\s+', ' ', name).strip()

    return COUNTRY_NAME_MAP.get(name, name)


def fetch_medal_table():
    """Fetch and parse the medal table from Wikipedia via Firecrawl."""
    print(f"Fetching medal data from {WIKI_URL} via Firecrawl API")

    if not FIRECRAWL_API_KEY:
        raise ValueError(
            "FIRECRAWL_API_KEY environment variable is not set. "
            "Set it before running this script."
        )

    response = requests.post(
        FIRECRAWL_API_URL,
        headers={
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "url": WIKI_URL,
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise RuntimeError(f"Firecrawl request failed: {data}")

    markdown = data["data"]["markdown"]
    return parse_medal_table(markdown)


def parse_medal_table(markdown):
    """Parse the medal table from the page markdown."""
    medals = []

    # Find the medal table section — look for the markdown table with
    # Rank | NOC | Gold | Silver | Bronze | Total headers
    lines = markdown.split('\n')

    in_table = False
    header_found = False

    for line in lines:
        stripped = line.strip()

        # Detect the header row of the medal table
        if not header_found and '|' in stripped:
            lower = stripped.lower()
            if 'gold' in lower and 'silver' in lower and 'bronze' in lower and 'noc' in lower:
                header_found = True
                in_table = True
                print("Found medal table!")
                continue

        # Skip the separator row (| --- | --- | ...)
        if in_table and re.match(r'^\|[\s\-|]+\|$', stripped):
            continue

        # Parse data rows
        if in_table and '|' in stripped:
            cells = [c.strip() for c in stripped.split('|')]
            # Remove empty first/last cells from leading/trailing pipes
            cells = [c for c in cells if c]

            if not cells:
                continue

            # Check for "Totals" row — end of table
            combined = ' '.join(cells).lower()
            if 'total' in combined and any(c.isdigit() for c in combined):
                # Check if this is the totals/summary row
                if 'entries' in combined or cells[0].lower().startswith('total'):
                    print("  (end of table)")
                    break

            # Expect: Rank | NOC | Gold | Silver | Bronze | Total
            # Some rows omit rank when tied (rank cell is empty)
            # Try to extract country and medal counts
            try:
                numbers = []
                country_parts = []

                for cell in cells:
                    # Try to parse as integer
                    clean = cell.strip()
                    if clean.isdigit():
                        numbers.append(int(clean))
                    elif re.match(r'^\d+$', clean.replace(',', '')):
                        numbers.append(int(clean.replace(',', '')))
                    else:
                        # Likely country/NOC cell or rank-less cell
                        # Skip pure rank numbers that weren't caught
                        if clean and not clean.startswith('---'):
                            country_parts.append(clean)

                # We need at least 3 numbers (gold, silver, bronze) and a country
                if len(numbers) >= 3 and country_parts:
                    # The country is the text cell (usually the longest one with letters)
                    raw_country = max(country_parts, key=len)
                    country = normalize_country(raw_country)

                    if not country or country.lower() == 'total':
                        continue

                    # 5+ numbers: [rank, gold, silver, bronze, total]
                    # 4 numbers: [gold, silver, bronze, total] (rank omitted for tied rows)
                    # 3 numbers: [gold, silver, bronze]
                    if len(numbers) >= 5:
                        gold, silver, bronze = numbers[1], numbers[2], numbers[3]
                    else:
                        gold, silver, bronze = numbers[0], numbers[1], numbers[2]

                    medals.append({
                        'Country': country,
                        'Gold': gold,
                        'Silver': silver,
                        'Bronze': bronze,
                    })
                    print(f"  {country}: {gold}G {silver}S {bronze}B")

            except (ValueError, IndexError) as e:
                print(f"  Skipping row: {e}")
                continue

    return medals

def write_csv(medals, filepath):
    """Write medal data to CSV file."""
    print(f"\nWriting {len(medals)} countries to {filepath}")

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Country', 'Gold', 'Silver', 'Bronze'])
        writer.writeheader()
        writer.writerows(medals)

    print("Done!")

def main():
    # Get the script's directory to find the data folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    csv_path = os.path.join(repo_root, 'data', 'medals.csv')

    try:
        medals = fetch_medal_table()

        if medals:
            write_csv(medals, csv_path)
        else:
            print("No medal data found. The Olympics may not have started yet.")
            print("Keeping existing medals.csv unchanged.")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    main()
