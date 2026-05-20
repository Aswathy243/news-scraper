"""
BBC News Headline Scraper
=========================
Uses BBC's public RSS feed instead of scraping HTML directly.
BBC loads headlines via JavaScript, so requests+BeautifulSoup gets 0 results.
RSS gives clean, structured, always-available data — no browser needed.

Install:
    pip install requests feedparser pandas beautifulsoup4 lxml

Usage:
    python scraper.py

Output:
    headlines.csv
"""

import requests
import feedparser
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

# BBC public RSS feeds — no login, always available
RSS_SOURCES = [
    ("BBC Top Stories",  "https://feeds.bbci.co.uk/news/rss.xml"),
    ("BBC World",        "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("BBC Technology",   "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("BBC Science",      "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
]

# Mimic a real browser — RSS feeds check this too
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (Chrome/120.0) Safari/537.36"
    )
}

MIN_WORDS = 4  # Filter out single-word labels or very short tags


# ──────────────────────────────────────────────
# Core functions
# ──────────────────────────────────────────────

def fetch_rss(url: str) -> str | None:
    """
    Fetch raw RSS XML from a URL.
    Returns the text content or None if the request fails.

    We fetch manually with requests (instead of feedparser.parse(url) directly)
    so we can pass custom headers — many sites block the default feedparser agent.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"  Failed ({response.status_code}): {url}")
            return None
        return response.text
    except requests.RequestException as e:
        print(f"  Network error: {e}")
        return None


def clean_summary(raw_html: str) -> str:
    """
    RSS summaries often contain raw HTML tags like <p>, <b>, <img>.
    BeautifulSoup strips all tags and returns clean plain text.
    """
    return BeautifulSoup(raw_html, "lxml").get_text(strip=True)


def is_valid_headline(text: str) -> bool:
    """Return True only if the text looks like a real news headline."""
    return len(text.split()) >= MIN_WORDS


def scrape_headlines(output_file: str = "headlines.csv") -> list[dict]:
    """
    Full pipeline:
        fetch RSS → parse entries → clean summaries → deduplicate → save CSV

    Returns the list of headline dicts.
    """
    print("\n" + "=" * 50)
    print("       BBC NEWS HEADLINE SCRAPER (RSS)")
    print("=" * 50)

    all_headlines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for source_name, url in RSS_SOURCES:
        print(f"\nFetching: {source_name}")

        xml = fetch_rss(url)
        if xml is None:
            continue

        # feedparser turns raw RSS XML into a Python object
        feed = feedparser.parse(xml)
        count = 0

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            summary = clean_summary(entry.get("summary", ""))
            link = entry.get("link", "")

            if not is_valid_headline(title):
                continue  # skip short/empty/nav entries

            all_headlines.append({
                "headline":   title,
                "summary":    summary,
                "source":     source_name,
                "link":       link,
                "word_count": len(title.split()),
                "scraped_at": timestamp,
            })
            count += 1

        print(f"  Found {count} headlines.")

    if not all_headlines:
        print("\nNo headlines found. Check your internet connection.")
        return []

    # Remove duplicate headlines that appear in multiple feeds
    df = pd.DataFrame(all_headlines)
    before = len(df)
    df = df.drop_duplicates(subset=["headline"]).reset_index(drop=True)
    after = len(df)
    print(f"\nRemoved {before - after} duplicates across feeds.")

    # Sort: most words first (main stories tend to have longer headlines)
    df = df.sort_values("word_count", ascending=False)

    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} headlines → '{output_file}'")

    # Quick preview
    print(f"\n── Sample headlines ──")
    for _, row in df.head(5).iterrows():
        print(f"  [{row['word_count']}w] {row['headline']}")

    return df.to_dict("records")


if __name__ == "__main__":
    scrape_headlines()