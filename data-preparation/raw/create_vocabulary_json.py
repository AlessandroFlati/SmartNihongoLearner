#!/usr/bin/env python3
"""Convert vocabulary_by_type.json to a flat array with UUIDs for React app."""

import json
import uuid
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "vocabulary_by_type.json"
OUTPUT_FILE = Path(__file__).parent.parent / "input" / "vocabulary.json"

def main():
    # Load vocabulary by type
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)

    # Flatten to array with UUIDs
    vocabulary = []

    for category, words in vocab_data['categories'].items():
        for word in words:
            vocabulary.append({
                "id": str(uuid.uuid4()),
                "japanese": word['japanese'],
                "reading": word['reading'],
                "english": word['english'],
                "type": word['type'],
                "frequency": word['frequency']
            })

    # Sort by frequency (descending) for better user experience
    vocabulary.sort(key=lambda x: x['frequency'], reverse=True)

    # Create output structure
    output = {
        "version": "1.0.0",
        "generatedAt": "2025-11-10",
        "totalWords": len(vocabulary),
        "vocabulary": vocabulary
    }

    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Created vocabulary.json with {len(vocabulary)} words")
    print(f"Output: {OUTPUT_FILE}")

    # Print statistics by type
    type_counts = {}
    for word in vocabulary:
        word_type = word['type']
        type_counts[word_type] = type_counts.get(word_type, 0) + 1

    print("\nWord counts by type:")
    for word_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {word_type:15s}: {count:4d}")

if __name__ == "__main__":
    main()
