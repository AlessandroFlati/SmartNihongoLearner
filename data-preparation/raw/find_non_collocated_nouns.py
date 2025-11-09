#!/usr/bin/env python3
"""Find nouns that have no collocations (not paired with any verb or adjective)."""

import json
from pathlib import Path

INPUT_VOCAB = Path(__file__).parent / "vocabulary_by_type.json"
INPUT_COLLOCATIONS = Path(__file__).parent.parent / "input" / "collocations_complete.json"

def main():
    # Load all nouns from vocabulary
    with open(INPUT_VOCAB, 'r', encoding='utf-8') as f:
        vocab_data = json.load(f)

    all_nouns = {n['japanese']: n for n in vocab_data['categories'].get('noun', [])}

    # Load complete collocation data
    with open(INPUT_COLLOCATIONS, 'r', encoding='utf-8') as f:
        colloc_data = json.load(f)

    # Find nouns that appear in collocations (either as targets or with reverse mappings)
    collocated_nouns = set()

    for word_jp, word_data in colloc_data['words'].items():
        word_type = word_data['type']

        if word_type == 'noun':
            # This noun has reverse mappings (verbs/adjectives that pair with it)
            collocated_nouns.add(word_jp)
        elif word_type in ['verb', 'adjective']:
            # Check all nouns this verb/adjective pairs with
            for match in word_data['matches']['nouns']:
                collocated_nouns.add(match['word'])

    # Find missing nouns
    missing_nouns = set(all_nouns.keys()) - collocated_nouns

    print(f"Total nouns in vocabulary: {len(all_nouns)}")
    print(f"Nouns with collocations: {len(collocated_nouns)}")
    print(f"Non-collocated nouns: {len(missing_nouns)}")

    # Sort by frequency
    missing_noun_data = [all_nouns[n] for n in missing_nouns]
    missing_noun_data.sort(key=lambda x: x['frequency'], reverse=True)

    # Write to file
    output_file = Path(__file__).parent / "non_collocated_nouns.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Non-collocated nouns: {len(missing_nouns)}\n")
        f.write(f"{'='*80}\n\n")

        for i, n in enumerate(missing_noun_data, 1):
            f.write(f"{i:3d}. {n['japanese']:20s} (freq: {n['frequency']:.2f}) - {n['english']}\n")

    print(f"\nNon-collocated nouns list written to: {output_file}")

    # Also show top 20 in console
    print(f"\nTop 20 non-collocated nouns by frequency:")
    for i, n in enumerate(missing_noun_data[:20], 1):
        try:
            print(f"{i:3d}. {n['japanese']:20s} (freq: {n['frequency']:.2f}) - {n['english'][:50]}")
        except UnicodeEncodeError:
            print(f"{i:3d}. [Japanese text] (freq: {n['frequency']:.2f}) - {n['english'][:50]}")

if __name__ == "__main__":
    main()
