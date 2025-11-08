#!/usr/bin/env python3
"""
Map Routledge frequency rankings to N5, N4, and N54 vocabulary CSV files.

This script reads the scraped Routledge frequency data and adds frequency rankings
to each vocabulary list based on matching Japanese words.
"""

import csv
from pathlib import Path
from typing import Dict

# File paths
INPUT_DIR = Path(__file__).parent.parent / "input"
FREQUENCY_FILE = INPUT_DIR / "routledge_frequency.csv"
N5_FILE = INPUT_DIR / "N5.csv"
N4_FILE = INPUT_DIR / "N4.csv"
N54_FILE = INPUT_DIR / "N54.csv"


def load_frequency_mapping(frequency_file: Path) -> Dict[str, int]:
    """
    Load frequency data and create a mapping from Japanese word to Routledge rank.

    Args:
        frequency_file: Path to the routledge_frequency.csv file

    Returns:
        Dictionary mapping Japanese word to frequency rank
    """
    frequency_map = {}

    with open(frequency_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            japanese = row['japanese']
            rank = int(row['routledge_rank'])

            # Store the lowest (best) rank if there are duplicates
            if japanese not in frequency_map or rank < frequency_map[japanese]:
                frequency_map[japanese] = rank

    print(f"Loaded {len(frequency_map)} unique words from frequency data")
    return frequency_map


def add_frequency_to_csv(input_file: Path, output_file: Path, frequency_map: Dict[str, int]) -> None:
    """
    Add frequency rankings to a vocabulary CSV file.

    Args:
        input_file: Path to input CSV file (e.g., N5.csv)
        output_file: Path to output CSV file with frequency data added
        frequency_map: Dictionary mapping Japanese word to frequency rank
    """
    print(f"\nProcessing: {input_file.name}")

    words_with_frequency = []
    words_without_frequency = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            japanese = row['japanese']

            # Look up frequency rank
            routledge_rank = frequency_map.get(japanese, '')

            # Create new row with frequency rank added
            new_row = {
                'japanese': row['japanese'],
                'reading': row['reading'],
                'english': row['english'],
                'type': row['type'],
                'routledge_rank': routledge_rank
            }

            if routledge_rank:
                words_with_frequency.append(new_row)
            else:
                words_without_frequency.append(new_row)

    # Combine rows (words with frequency first, sorted by rank)
    words_with_frequency.sort(key=lambda x: int(x['routledge_rank']))
    all_rows = words_with_frequency + words_without_frequency

    # Write to output file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['japanese', 'reading', 'english', 'type', 'routledge_rank']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    total = len(all_rows)
    matched = len(words_with_frequency)
    unmatched = len(words_without_frequency)

    print(f"  Total words: {total}")
    print(f"  Matched with frequency: {matched} ({matched/total*100:.1f}%)")
    print(f"  No frequency data: {unmatched} ({unmatched/total*100:.1f}%)")
    print(f"  ✓ Saved to: {output_file}")


def main():
    """Main function to map frequency data to all vocabulary files."""
    print("Starting frequency mapping process...")
    print(f"Loading frequency data from: {FREQUENCY_FILE}\n")

    # Load frequency mapping
    frequency_map = load_frequency_mapping(FREQUENCY_FILE)

    # Process each vocabulary file
    files_to_process = [
        (N5_FILE, N5_FILE),  # Overwrite in place
        (N4_FILE, N4_FILE),
        (N54_FILE, N54_FILE)
    ]

    for input_file, output_file in files_to_process:
        if input_file.exists():
            add_frequency_to_csv(input_file, output_file, frequency_map)
        else:
            print(f"Warning: {input_file} not found, skipping...")

    print("\n✓ Frequency mapping complete!")


if __name__ == "__main__":
    main()
