#!/usr/bin/env python3
"""
Convert study list CSV files to JSON format for use in the web app
"""

import csv
import json
from pathlib import Path
from datetime import datetime

def convert_csv_to_json(csv_path, output_path):
    """Convert a CSV study list to JSON format"""
    words = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words.append(row['japanese'])

    # Create JSON structure
    data = {
        "version": "1.0.0",
        "generatedAt": datetime.now().strftime("%Y-%m-%d"),
        "totalWords": len(words),
        "words": words
    }

    # Write to JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Converted {csv_path.name} -> {output_path.name} ({len(words)} words)")

def main():
    # Input and output directories
    input_dir = Path(__file__).parent / 'input'
    output_dir = Path(__file__).parent.parent / 'public' / 'data'

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert study lists
    convert_csv_to_json(
        input_dir / 'N5.csv',
        output_dir / 'studylist_n5.json'
    )

    convert_csv_to_json(
        input_dir / 'N54.csv',
        output_dir / 'studylist_n54.json'
    )

    print("\nAll study lists converted successfully!")

if __name__ == '__main__':
    main()
