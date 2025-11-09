#!/usr/bin/env python3
"""
Generate collocation pairs from N54 vocabulary.

This script generates verb-noun and adjective-noun collocations where BOTH words
must exist in the N54 vocabulary list. All natural pairings are included.
"""

import json
from pathlib import Path
from collocation_mappings import get_verb_noun_collocations, get_adjective_noun_collocations

INPUT_FILE = Path(__file__).parent / "vocabulary_by_type.json"
OUTPUT_FILE = Path(__file__).parent.parent / "input" / "collocations.json"


def load_vocabulary():
    """Load categorized vocabulary."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['categories']


def generate_verb_noun_collocations(verbs, nouns):
    """
    Generate verb-noun collocations using pre-defined mappings.

    Only includes pairs where both verb and noun exist in N54 vocabulary.

    Returns dict of verb -> list of {word, score, reading, english} matches
    """

    # Create lookups
    verb_dict = {v['japanese']: v for v in verbs}
    noun_dict = {n['japanese']: n for n in nouns}

    # Load pre-defined mappings
    mappings = get_verb_noun_collocations()

    collocations = {}
    total_pairs = 0
    skipped_verbs = 0
    skipped_nouns = 0

    for verb_jp, noun_pairs in mappings.items():
        # Check if verb exists in vocabulary
        if verb_jp not in verb_dict:
            skipped_verbs += 1
            continue

        verb_data = verb_dict[verb_jp]
        valid_matches = []

        for noun_jp, score in noun_pairs:
            # Check if noun exists in vocabulary
            if noun_jp not in noun_dict:
                skipped_nouns += 1
                continue

            noun_data = noun_dict[noun_jp]
            valid_matches.append({
                "word": noun_jp,
                "reading": noun_data['reading'],
                "english": noun_data['english'],
                "score": score
            })
            total_pairs += 1

        if valid_matches:
            collocations[verb_jp] = {
                "word": verb_jp,
                "reading": verb_data['reading'],
                "english": verb_data['english'],
                "type": "verb",
                "matches": valid_matches
            }

    print(f"Verb-noun collocations:")
    print(f"  Processed: {len(collocations)} verbs")
    print(f"  Generated: {total_pairs} verb-noun pairs")
    print(f"  Skipped: {skipped_verbs} verbs, {skipped_nouns} noun references (not in vocabulary)")

    return collocations


def generate_adjective_noun_collocations(adjectives, nouns):
    """
    Generate adjective-noun collocations using pre-defined mappings.

    Only includes pairs where both adjective and noun exist in N54 vocabulary.

    Returns dict of adjective -> list of {word, score, reading, english} matches
    """

    # Create lookups
    adj_dict = {a['japanese']: a for a in adjectives}
    noun_dict = {n['japanese']: n for n in nouns}

    # Load pre-defined mappings
    mappings = get_adjective_noun_collocations()

    collocations = {}
    total_pairs = 0
    skipped_adjectives = 0
    skipped_nouns = 0

    for adj_jp, noun_pairs in mappings.items():
        # Check if adjective exists in vocabulary
        if adj_jp not in adj_dict:
            skipped_adjectives += 1
            continue

        adj_data = adj_dict[adj_jp]
        valid_matches = []

        for noun_jp, score in noun_pairs:
            # Check if noun exists in vocabulary
            if noun_jp not in noun_dict:
                skipped_nouns += 1
                continue

            noun_data = noun_dict[noun_jp]
            valid_matches.append({
                "word": noun_jp,
                "reading": noun_data['reading'],
                "english": noun_data['english'],
                "score": score
            })
            total_pairs += 1

        if valid_matches:
            collocations[adj_jp] = {
                "word": adj_jp,
                "reading": adj_data['reading'],
                "english": adj_data['english'],
                "type": "adjective",
                "matches": valid_matches
            }

    print(f"Adjective-noun collocations:")
    print(f"  Processed: {len(collocations)} adjectives")
    print(f"  Generated: {total_pairs} adjective-noun pairs")
    print(f"  Skipped: {skipped_adjectives} adjectives, {skipped_nouns} noun references (not in vocabulary)")

    return collocations


def save_collocations(verb_noun, adjective_noun):
    """Save collocations to JSON file."""

    # Combine all collocations
    all_collocations = {}
    all_collocations.update(verb_noun)
    all_collocations.update(adjective_noun)

    output_data = {
        "version": "1.0.0",
        "generatedAt": "2025-11-09",
        "totalPairs": sum(len(matches) for matches in all_collocations.values()),
        "totalWords": len(all_collocations),
        "collocations": all_collocations
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {output_data['totalPairs']} collocation pairs")
    print(f"Covering {output_data['totalWords']} words")
    print(f"Output: {OUTPUT_FILE}")


def main():
    """Main generation function."""
    print("=" * 60)
    print("Collocation Generation - N54 Vocabulary")
    print("=" * 60)

    # Load vocabulary
    vocab = load_vocabulary()

    verbs = vocab.get('verb', [])
    nouns = vocab.get('noun', [])
    adjectives = vocab.get('adjective', [])

    print(f"\nVocabulary loaded:")
    print(f"  Verbs: {len(verbs)}")
    print(f"  Nouns: {len(nouns)}")
    print(f"  Adjectives: {len(adjectives)}")
    print()

    # Generate collocations
    verb_noun = generate_verb_noun_collocations(verbs, nouns)
    adjective_noun = generate_adjective_noun_collocations(adjectives, nouns)

    # Save results
    save_collocations(verb_noun, adjective_noun)


if __name__ == "__main__":
    main()
