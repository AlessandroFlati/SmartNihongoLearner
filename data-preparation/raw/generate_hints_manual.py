#!/usr/bin/env python3
"""Helper script to generate hints manually in batches."""

import json
from pathlib import Path

INPUT_FILE = Path(__file__).parent.parent / "input" / "collocations_complete.json"
OUTPUT_FILE = Path(__file__).parent.parent / "input" / "collocation_hints.json"
PROGRESS_FILE = Path(__file__).parent / "hints_progress.txt"

def load_data():
    """Load collocation data."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_words_with_collocations(data):
    """Get all verbs/adjectives that have noun collocations."""
    words = []
    for word_jp, word_data in data['words'].items():
        if word_data['type'] in ['verb', 'adjective']:
            nouns = word_data.get('matches', {}).get('nouns', [])
            if nouns:
                words.append({
                    'word': word_jp,
                    'reading': word_data['reading'],
                    'english': word_data['english'],
                    'type': word_data['type'],
                    'noun_count': len(nouns),
                    'nouns': nouns
                })
    return words

def display_word_batch(words, start_idx, batch_size=5):
    """Display a batch of words with their collocations for manual hint generation."""
    print("=" * 80)
    print(f"BATCH {start_idx // batch_size + 1}")
    print("=" * 80)
    print()

    for i in range(start_idx, min(start_idx + batch_size, len(words))):
        word_data = words[i]
        print(f"\n[{i+1}/{len(words)}] {word_data['word']} ({word_data['reading']}) - {word_data['english']}")
        print(f"Type: {word_data['type']}")
        print(f"Noun collocations: {word_data['noun_count']}")
        print("-" * 80)

        # Group nouns by score for easier categorization
        for score in [3, 2, 1]:
            nouns_at_score = [n for n in word_data['nouns'] if n['score'] == score]
            if nouns_at_score:
                print(f"\nScore {score} ({len(nouns_at_score)} nouns):")
                for noun in nouns_at_score:
                    print(f"  • {noun['word']} ({noun['reading']}) - {noun['english']}")

        print()

def main():
    """Main function."""
    print("Loading collocation data...")
    data = load_data()
    words = get_words_with_collocations(data)

    print(f"\nTotal words to process: {len(words)}")
    print(f"Verbs: {sum(1 for w in words if w['type'] == 'verb')}")
    print(f"Adjectives: {sum(1 for w in words if w['type'] == 'adjective')}")

    # Display first batch
    batch_size = 5
    display_word_batch(words, 0, batch_size)

    print("\n" + "=" * 80)
    print("INSTRUCTIONS:")
    print("=" * 80)
    print("For each word above, analyze the noun collocations and provide semantic category hints.")
    print("Group similar nouns together with the same hint.")
    print()
    print("Examples:")
    print("  - 水, コーヒー, お茶 → 'beverages'")
    print("  - 本, 雑誌, 新聞 → 'reading materials'")
    print("  - 服, シャツ, 靴 → 'clothing items'")
    print()
    print("The hints will be used in the 'I'm Stuck' button during gameplay.")

if __name__ == "__main__":
    main()
