#!/usr/bin/env python3
"""Find adjectives not yet in collocation mappings."""

import json
from pathlib import Path
from collocation_mappings import get_adjective_noun_collocations

INPUT_FILE = Path(__file__).parent / "vocabulary_by_type.json"

def main():
    # Load all adjectives from vocabulary
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_adjectives = {a['japanese'] for a in data['categories'].get('adjective', [])}

    # Load mapped adjectives
    mapped = set(get_adjective_noun_collocations().keys())

    # Find missing
    missing = all_adjectives - mapped

    print(f"Total adjectives in vocabulary: {len(all_adjectives)}")
    print(f"Adjectives with collocation mappings: {len(mapped)}")
    print(f"Missing adjectives: {len(missing)}")
    print(f"\nMissing adjectives (sorted by frequency):")

    # Get full adjective data for sorting
    all_adj_data = {a['japanese']: a for a in data['categories'].get('adjective', [])}
    missing_adjectives = [all_adj_data[a] for a in missing]
    missing_adjectives.sort(key=lambda x: x['frequency'], reverse=True)

    # Write to file to avoid encoding issues
    output_file = Path(__file__).parent / "missing_adjectives_output.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, a in enumerate(missing_adjectives[:100], 1):  # Show first 100
            f.write(f"{i:3d}. {a['japanese']:15s} (freq: {a['frequency']:.2f}) - {a['english'][:50]}\n")

    print(f"\nMissing adjectives list written to: {output_file}")

if __name__ == "__main__":
    main()
