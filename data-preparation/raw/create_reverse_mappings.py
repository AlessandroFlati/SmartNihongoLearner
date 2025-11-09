#!/usr/bin/env python3
"""
Create reverse collocation mappings.

This script takes the existing verb→noun and adjective→noun mappings
and creates the reverse: noun→verbs and noun→adjectives.

This allows the game to work in both directions:
- "What verbs/adjectives go with this noun?"
- "What nouns go with this verb/adjective?"
"""

import json
from pathlib import Path

INPUT_FILE = Path(__file__).parent.parent / "input" / "collocations.json"
OUTPUT_FILE = Path(__file__).parent.parent / "input" / "collocations_complete.json"


def load_collocations():
    """Load existing collocation data."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_reverse_mappings(collocations_data):
    """
    Create reverse mappings: noun → [verbs/adjectives that pair with it].

    Args:
        collocations_data: The original collocation data

    Returns:
        dict of noun → {verbs: [], adjectives: []}
    """

    reverse_map = {}

    # Process each word in the collocation database
    for word_jp, word_data in collocations_data['collocations'].items():
        word_type = word_data['type']

        # For each match (noun) this word pairs with
        for match in word_data['matches']:
            noun_jp = match['word']

            # Initialize noun entry if not exists
            if noun_jp not in reverse_map:
                reverse_map[noun_jp] = {
                    'word': noun_jp,
                    'reading': match['reading'],
                    'english': match['english'],
                    'type': 'noun',
                    'verbs': [],
                    'adjectives': []
                }

            # Add this word to the appropriate list
            pairing = {
                'word': word_jp,
                'reading': word_data['reading'],
                'english': word_data['english'],
                'score': match['score']
            }

            if word_type == 'verb':
                reverse_map[noun_jp]['verbs'].append(pairing)
            elif word_type == 'adjective':
                reverse_map[noun_jp]['adjectives'].append(pairing)

    # Sort each noun's verb/adjective lists by score (highest first)
    for noun_data in reverse_map.values():
        noun_data['verbs'].sort(key=lambda x: x['score'], reverse=True)
        noun_data['adjectives'].sort(key=lambda x: x['score'], reverse=True)

    return reverse_map


def merge_bidirectional_data(original_data, reverse_map):
    """
    Merge original and reverse mappings into a complete bidirectional structure.

    Structure:
    {
      "words": {
        "verb_or_adj": {
          "word": "...",
          "type": "verb",
          "matches": {
            "nouns": [...]  // nouns that pair with this verb/adj
          }
        },
        "noun": {
          "word": "...",
          "type": "noun",
          "matches": {
            "verbs": [...],      // verbs that pair with this noun
            "adjectives": [...]  // adjectives that pair with this noun
          }
        }
      }
    }
    """

    merged = {
        "version": "2.0.0",
        "generatedAt": original_data['generatedAt'],
        "totalPairs": original_data['totalPairs'],
        "totalWords": original_data['totalWords'] + len(reverse_map),
        "words": {}
    }

    # Add all original verbs and adjectives
    for word_jp, word_data in original_data['collocations'].items():
        merged['words'][word_jp] = {
            'word': word_data['word'],
            'reading': word_data['reading'],
            'english': word_data['english'],
            'type': word_data['type'],
            'matches': {
                'nouns': word_data['matches']
            }
        }

    # Add all reverse-mapped nouns
    for noun_jp, noun_data in reverse_map.items():
        merged['words'][noun_jp] = {
            'word': noun_data['word'],
            'reading': noun_data['reading'],
            'english': noun_data['english'],
            'type': 'noun',
            'matches': {
                'verbs': noun_data['verbs'],
                'adjectives': noun_data['adjectives']
            }
        }

    return merged


def save_complete_collocations(data):
    """Save the complete bidirectional collocation data."""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved complete collocation database")
    print(f"✓ Output: {OUTPUT_FILE}")


def main():
    """Main function."""
    print("=" * 60)
    print("Creating Reverse Collocation Mappings")
    print("=" * 60)

    # Load original data
    print("\nLoading original collocation data...")
    original_data = load_collocations()
    print(f"  Original: {original_data['totalWords']} words, {original_data['totalPairs']} pairs")

    # Create reverse mappings
    print("\nCreating reverse mappings (noun → verbs/adjectives)...")
    reverse_map = create_reverse_mappings(original_data)
    print(f"  Reverse: {len(reverse_map)} nouns")

    # Calculate statistics
    total_verb_links = sum(len(n['verbs']) for n in reverse_map.values())
    total_adj_links = sum(len(n['adjectives']) for n in reverse_map.values())

    print(f"\nReverse mapping statistics:")
    print(f"  Nouns with verb pairings: {sum(1 for n in reverse_map.values() if n['verbs'])}")
    print(f"  Nouns with adjective pairings: {sum(1 for n in reverse_map.values() if n['adjectives'])}")
    print(f"  Total noun→verb links: {total_verb_links}")
    print(f"  Total noun→adjective links: {total_adj_links}")

    # Show example
    sample_noun = list(reverse_map.keys())[0]
    sample_data = reverse_map[sample_noun]
    print(f"\nExample: {sample_noun}")
    print(f"  Verbs: {', '.join(v['word'] for v in sample_data['verbs'][:5])}")
    print(f"  Adjectives: {', '.join(a['word'] for a in sample_data['adjectives'][:5])}")

    # Merge into bidirectional structure
    print("\nMerging into complete bidirectional structure...")
    complete_data = merge_bidirectional_data(original_data, reverse_map)
    print(f"  Total words in complete database: {complete_data['totalWords']}")

    # Save
    save_complete_collocations(complete_data)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✓ Complete bidirectional collocation database created")
    print(f"✓ {complete_data['totalWords']} total words")
    print(f"✓ {original_data['totalWords']} verbs/adjectives → nouns")
    print(f"✓ {len(reverse_map)} nouns → verbs/adjectives")
    print(f"✓ Game can now work in both directions!")
    print("=" * 60)


if __name__ == "__main__":
    main()
