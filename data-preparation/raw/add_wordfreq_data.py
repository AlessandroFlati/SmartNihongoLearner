#!/usr/bin/env python3
"""
Add wordfreq frequency data to vocabulary CSV files.

This script uses the wordfreq library to add Zipf frequency scores to each word.
Zipf scale: 0-8, where higher = more frequent. Common words are 4+, very common are 6+.
"""

import csv
from pathlib import Path
from wordfreq import zipf_frequency

# File paths
INPUT_DIR = Path(__file__).parent.parent / "input"
N5_FILE = INPUT_DIR / "N5.csv"
N4_FILE = INPUT_DIR / "N4.csv"
N54_FILE = INPUT_DIR / "N54.csv"


def add_wordfreq_to_csv(input_file: Path, output_file: Path) -> None:
    """
    Add wordfreq Zipf scores to a vocabulary CSV file.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file with wordfreq data added
    """
    print(f"\nProcessing: {input_file.name}")

    rows = []
    zipf_scores = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            japanese = row['japanese']

            # Get Zipf frequency (0-8 scale, higher = more frequent)
            zipf_score = zipf_frequency(japanese, 'ja')

            # Round to 2 decimal places for readability
            zipf_score = round(zipf_score, 2)

            # Create new row with wordfreq score added
            new_row = {
                'japanese': row['japanese'],
                'reading': row['reading'],
                'english': row['english'],
                'type': row['type'],
                'routledge_rank': row.get('routledge_rank', ''),
                'wordfreq_zipf': zipf_score if zipf_score > 0 else ''
            }

            rows.append(new_row)
            if zipf_score > 0:
                zipf_scores.append(zipf_score)

    # Calculate statistics
    total = len(rows)
    matched = len(zipf_scores)
    unmatched = total - matched

    if zipf_scores:
        avg_zipf = sum(zipf_scores) / len(zipf_scores)
        min_zipf = min(zipf_scores)
        max_zipf = max(zipf_scores)
    else:
        avg_zipf = min_zipf = max_zipf = 0

    # Write to output file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['japanese', 'reading', 'english', 'type', 'routledge_rank', 'wordfreq_zipf']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  Total words: {total}")
    print(f"  Words with wordfreq data: {matched} ({matched/total*100:.1f}%)")
    print(f"  Words without wordfreq data: {unmatched} ({unmatched/total*100:.1f}%)")
    if zipf_scores:
        print(f"  Zipf score range: {min_zipf:.2f} - {max_zipf:.2f}")
        print(f"  Average Zipf score: {avg_zipf:.2f}")
    print(f"  ✓ Saved to: {output_file}")


def main():
    """Main function to add wordfreq data to all vocabulary files."""
    print("Adding wordfreq frequency data to vocabulary files...")
    print("Zipf scale: 0-8 (higher = more frequent)")
    print("  - Common words: 4+")
    print("  - Very common words: 6+")
    print("  - Most common words: 7+")

    # Process each vocabulary file
    files_to_process = [
        (N5_FILE, N5_FILE),  # Overwrite in place
        (N4_FILE, N4_FILE),
        (N54_FILE, N54_FILE)
    ]

    for input_file, output_file in files_to_process:
        if input_file.exists():
            add_wordfreq_to_csv(input_file, output_file)
        else:
            print(f"Warning: {input_file} not found, skipping...")

    print("\n✓ Wordfreq data added successfully!")


if __name__ == "__main__":
    main()
