"""
Scrapes the 2026 Winter Olympics medal table from Wikipedia
and updates data/medals.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import os

# Wikipedia URL for 2026 Winter Olympics medal table
WIKI_URL = "https://en.wikipedia.org/wiki/2026_Winter_Olympics_medal_table"

def fetch_medal_table():
    """Fetch and parse the medal table from Wikipedia."""
    print(f"Fetching medal data from {WIKI_URL}")

    response = requests.get(WIKI_URL, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; OlympicPoolBot/1.0)'
    })
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the medal table - Wikipedia uses wikitable class
    tables = soup.find_all('table', class_='wikitable')

    medals = []

    for table in tables:
        # Look for a table with Gold, Silver, Bronze headers
        headers = table.find_all('th')
        header_text = ' '.join([h.get_text().strip().lower() for h in headers])

        if 'gold' in header_text and 'silver' in header_text and 'bronze' in header_text:
            print("Found medal table!")

            rows = table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 5:
                    # Country name is usually in first cell (may have flag image)
                    country_cell = cells[0]
                    # Get text, removing any flag images or extra content
                    country = country_cell.get_text().strip()
                    # Clean up country name (remove asterisks, daggers, etc.)
                    country = ''.join(c for c in country if c.isalpha() or c.isspace()).strip()

                    if not country or country.lower() == 'total':
                        continue

                    try:
                        # Medal counts are typically in columns 1, 2, 3 (or sometimes with rank in 0)
                        # Find numeric values
                        numbers = []
                        for cell in cells[1:]:
                            text = cell.get_text().strip()
                            if text.isdigit():
                                numbers.append(int(text))

                        if len(numbers) >= 3:
                            gold, silver, bronze = numbers[0], numbers[1], numbers[2]
                            medals.append({
                                'Country': country,
                                'Gold': gold,
                                'Silver': silver,
                                'Bronze': bronze
                            })
                            print(f"  {country}: {gold}G {silver}S {bronze}B")
                    except (ValueError, IndexError) as e:
                        print(f"  Skipping row: {e}")
                        continue

            break  # Found our table, stop looking

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
