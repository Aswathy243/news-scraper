"""
Headline Analyser
=================
Reads headlines.csv (produced by scraper.py) and runs text analysis.

Produces:
    - Console summary (word frequencies, avg length, source breakdown)
    - top_words.csv — word frequency table ready for ML feature use

Usage:
    python analyser.py
"""

import pandas as pd
from collections import Counter
import re


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

INPUT_FILE    = "headlines.csv"
TOP_WORDS_OUT = "top_words.csv"
TOP_N         = 10  # how many top words to report

# Common English words that carry no real meaning (stopwords)
# Filtering these out means the top words reflect actual news topics
STOPWORDS = {
    "the", "a", "an", "is", "in", "on", "at", "to", "of", "and",
    "for", "with", "as", "by", "from", "it", "its", "be", "are",
    "was", "has", "have", "that", "this", "but", "or", "not", "he",
    "she", "his", "her", "they", "we", "you", "i", "my", "new",
    "after", "over", "into", "about", "up", "out", "more", "says",
}


# ──────────────────────────────────────────────
# Core functions
# ──────────────────────────────────────────────

def load_headlines(filepath: str) -> pd.DataFrame:
    """Load and clean the headlines CSV."""
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"File not found: '{filepath}'")
        print("Run scraper.py first to generate it.")
        return pd.DataFrame()

    original_count = len(df)

    # Remove duplicates and empty rows
    df = df.drop_duplicates(subset=["headline"])
    df = df.dropna(subset=["headline"])
    df["headline"] = df["headline"].str.strip()

    # Ensure word_count column exists
    if "word_count" not in df.columns:
        df["word_count"] = df["headline"].apply(lambda x: len(x.split()))

    print(f"Loaded {original_count} rows → {len(df)} unique headlines after cleaning.")
    return df


def get_top_words(df: pd.DataFrame, n: int = TOP_N) -> pd.DataFrame:
    """
    Count the most frequent meaningful words across all headlines.

    Steps:
      1. Extract all alphabetic words (re.findall strips punctuation)
      2. Lowercase everything for consistent counting
      3. Filter out stopwords
      4. Count with Counter and return top N
    """
    all_words = []

    for headline in df["headline"]:
        # \b[a-zA-Z]{3,}\b — word boundary, letters only, 3+ chars
        words = re.findall(r'\b[a-zA-Z]{3,}\b', headline.lower())
        meaningful = [w for w in words if w not in STOPWORDS]
        all_words.extend(meaningful)

    top = Counter(all_words).most_common(n)
    return pd.DataFrame(top, columns=["word", "count"])


def source_breakdown(df: pd.DataFrame) -> None:
    """Print how many headlines came from each RSS source."""
    if "source" not in df.columns:
        return
    print("\n── Headlines by source ──")
    for source, count in df["source"].value_counts().items():
        print(f"  {source}: {count}")


def analyse_headlines(input_file: str = INPUT_FILE) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Full analysis pipeline:
        load → clean → word frequency → length stats → save top_words CSV

    Returns (cleaned DataFrame, top_words DataFrame)
    """
    print("\n" + "=" * 50)
    print("       HEADLINE ANALYSER")
    print("=" * 50)

    df = load_headlines(input_file)
    if df.empty:
        return df, pd.DataFrame()

    # ── Word frequency ──
    top_words_df = get_top_words(df, n=TOP_N)
    print(f"\n── Top {TOP_N} words across all headlines ──")
    for _, row in top_words_df.iterrows():
        bar = "█" * row["count"]
        print(f"  {row['word']:<15} {row['count']:>3}  {bar}")

    # ── Length stats ──
    avg  = df["word_count"].mean()
    shortest = df.loc[df["word_count"].idxmin(), "headline"]
    longest  = df.loc[df["word_count"].idxmax(), "headline"]
    print(f"\n── Headline length ──")
    print(f"  Average  : {avg:.1f} words")
    print(f"  Shortest : {shortest}")
    print(f"  Longest  : {longest}")

    # ── Source breakdown ──
    source_breakdown(df)

    # ── Save ──
    top_words_df.to_csv(TOP_WORDS_OUT, index=False)
    print(f"\nSaved word frequencies → '{TOP_WORDS_OUT}'")

    return df, top_words_df


if __name__ == "__main__":
    analyse_headlines()