"""
main.py — entry point
Runs the full pipeline: scrape → analyse
"""

from scraper  import scrape_headlines
from analyser import analyse_headlines


def main():
    # Step 1: fetch headlines from BBC RSS and save to CSV
    headlines = scrape_headlines(output_file="headlines.csv")

    if not headlines:
        print("No headlines found. Exiting.")
        return

    # Step 2: analyse the saved CSV
    df, top_words = analyse_headlines(input_file="headlines.csv")
    print("\nDone.")


if __name__ == "__main__":
    main()