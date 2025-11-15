#!/usr/bin/env python3
"""
Categorize vocabulary by word type for collocation generation.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

INPUT_DIR = Path(__file__).parent.parent / "input"
N54_FILE = INPUT_DIR / "N54.csv"
OUTPUT_FILE = Path(__file__).parent / "vocabulary_by_type.json"


def categorize_vocabulary():
    """Load and categorize vocabulary by type."""

    vocab_by_type = defaultdict(list)

    with open(N54_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            word_data = {
                'japanese': row['japanese'],
                'reading': row['reading'],
                'english': row['english'],
                'type': row['type'],
                'frequency': float(row['frequency']) if row['frequency'] else 0
            }

            # Categorize by primary type
            word_type = row['type'].lower()
            vocab_by_type[word_type].append(word_data)

    # Sort each category by frequency (highest first)
    for word_type in vocab_by_type:
        vocab_by_type[word_type].sort(key=lambda x: x['frequency'], reverse=True)

    # Save to JSON
    output_data = {
        'total_words': sum(len(words) for words in vocab_by_type.values()),
        'categories': dict(vocab_by_type)
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"\nVocabulary Categorization Summary")
    print(f"=" * 60)
    print(f"Total words: {output_data['total_words']}")
    print(f"\nBreakdown by type:")

    for word_type, words in sorted(vocab_by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {word_type:20s}: {len(words):4d} words")
        # Show top 5 most frequent
        print(f"    Top 5: {', '.join(w['japanese'] for w in words[:5])}")

    print(f"\n✓ Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    categorize_vocabulary()
