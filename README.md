# BBC News Headline Scraper & Analyser

A Python NLP pipeline that fetches live headlines from BBC News RSS feeds, cleans the data, and runs text frequency analysis — producing structured CSVs ready for downstream ML use.

## What it does

```
BBC RSS feeds (4 sources)
        ↓
  fetch + parse XML          ← feedparser
        ↓
  clean HTML in summaries    ← BeautifulSoup
        ↓
  deduplicate across feeds   ← pandas
        ↓
  headlines.csv              ← 109 headlines, word count, source, link
        ↓
  stopword filtering         ← regex + Counter
  word frequency analysis    ← collections
        ↓
  top_words.csv              ← ready for ML feature engineering
```

## Sample output

```
── Top 10 words across all headlines ──
  could             8  ████████
  trump             7  ███████
  prices            5  █████
  tech              4  ████

── Headline length ──
  Average  : 10.6 words
  Shortest : The £100Bn HS2 Debacle
  Longest  : COP30: Trump and many leaders are skipping it...

── Headlines by source ──
  BBC Top Stories: 33
  BBC Science: 32
  BBC World: 32
  BBC Technology: 12
```

## Setup

```bash
git clone https://github.com/Aswathy243/news-scraper
cd news-scraper
pip install -r requirements.txt
python main.py
```

## Files

| File | Purpose |
|---|---|
| `scraper.py` | Fetches and parses BBC RSS feeds, saves `headlines.csv` |
| `analyser.py` | Loads CSV, runs word frequency and length analysis, saves `top_words.csv` |
| `main.py` | Entry point — runs scraper then analyser |
| `headlines.csv` | Output: headline, summary, source, link, word\_count, scraped\_at |
| `top_words.csv` | Output: word, count — top keywords across all headlines |

## Why RSS instead of HTML scraping?

BBC loads headlines via JavaScript after the page renders. `requests` fetches the raw HTML before JS runs, so `BeautifulSoup` finds 0 headlines. BBC's RSS feeds provide the same data in clean XML — no browser needed, always reliable.

## Skills demonstrated

- HTTP requests with custom headers
- RSS/XML parsing with `feedparser`
- HTML cleaning with `BeautifulSoup`
- Data cleaning and deduplication with `pandas`
- Text preprocessing: regex tokenization, stopword filtering
- Word frequency analysis with `collections.Counter`
- Structured CSV output for downstream ML pipelines
