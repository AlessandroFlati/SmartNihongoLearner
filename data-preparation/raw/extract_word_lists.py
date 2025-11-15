#!/usr/bin/env python3
"""Extract simple word lists for collocation generation."""

import json
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "vocabulary_by_type.json"


def extract_word_lists():
    """Extract word lists by type."""

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vocab = data['categories']

    # Extract verbs
    verbs = [w['japanese'] for w in vocab.get('verb', [])]
    nouns = [w['japanese'] for w in vocab.get('noun', [])]
    adjectives = [w['japanese'] for w in vocab.get('adjective', [])]

    print("VERBS ({} total):".format(len(verbs)))
    print(", ".join(verbs[:50]))
    print(f"... and {len(verbs) - 50} more\n")

    print("NOUNS ({} total):".format(len(nouns)))
    print(", ".join(nouns[:50]))
    print(f"... and {len(nouns) - 50} more\n")

    print("ADJECTIVES ({} total):".format(len(adjectives)))
    print(", ".join(adjectives))


if __name__ == "__main__":
    extract_word_lists()
