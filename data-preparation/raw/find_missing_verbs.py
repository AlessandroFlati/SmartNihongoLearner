#!/usr/bin/env python3
"""Find verbs not yet in collocation mappings."""

import json
from pathlib import Path
from collocation_mappings import get_verb_noun_collocations

INPUT_FILE = Path(__file__).parent / "vocabulary_by_type.json"

def main():
    # Load all verbs from vocabulary
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_verbs = {v['japanese'] for v in data['categories'].get('verb', [])}

    # Load mapped verbs
    mapped = set(get_verb_noun_collocations().keys())

    # Find missing
    missing = all_verbs - mapped

    print(f"Total verbs in vocabulary: {len(all_verbs)}")
    print(f"Verbs with collocation mappings: {len(mapped)}")
    print(f"Missing verbs: {len(missing)}")
    print(f"\nMissing verbs (sorted by frequency):")

    # Get full verb data for sorting
    all_verb_data = {v['japanese']: v for v in data['categories'].get('verb', [])}
    missing_verbs = [all_verb_data[v] for v in missing]
    missing_verbs.sort(key=lambda x: x['frequency'], reverse=True)

    # Write to file to avoid encoding issues
    output_file = Path(__file__).parent / "missing_verbs_output.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, v in enumerate(missing_verbs[:100], 1):  # Show first 100
            f.write(f"{i:3d}. {v['japanese']:15s} (freq: {v['frequency']:.2f}) - {v['english'][:50]}\n")

    print(f"\nMissing verbs list written to: {output_file}")

if __name__ == "__main__":
    main()
