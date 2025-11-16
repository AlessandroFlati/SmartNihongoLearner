#!/usr/bin/env python3
"""
Find and group synonym/alternative writing collocation pairs.

This script identifies noun pairs that are synonyms or alternative writings, such as:
- 晩ご飯 vs 夕飯 (dinner)
- 弁当 vs お弁当 (lunch box, honorific vs plain)
- Alternative kanji/hiragana writings
"""

import json
from pathlib import Path
from difflib import SequenceMatcher

def load_vocabulary():
    """Load vocabulary from JSON file"""
    vocab_path = Path("public/data/vocabulary.json")
    with open(vocab_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['vocabulary']

def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def remove_honorific_prefix(word):
    """Remove お or ご prefix"""
    if word.startswith('お'):
        return word[1:]
    if word.startswith('ご'):
        return word[1:]
    return word

def find_synonym_groups(vocabulary):
    """
    Find groups of words that are synonyms or alternative writings.

    Returns:
        List of groups, where each group is a list of related words
    """
    # Filter only nouns (since collocations involve nouns)
    nouns = [w for w in vocabulary if w['type'] == 'noun']

    print(f"Analyzing {len(nouns)} nouns for synonym groups...")

    groups = []
    used_words = set()

    for i, word1 in enumerate(nouns):
        if word1['japanese'] in used_words:
            continue

        group = [word1]

        for word2 in nouns[i+1:]:
            if word2['japanese'] in used_words:
                continue

            # Check for various types of relationships
            is_related = False
            relationship_type = None

            # 1. Honorific vs plain (お弁当 vs 弁当)
            w1_no_hon = remove_honorific_prefix(word1['japanese'])
            w2_no_hon = remove_honorific_prefix(word2['japanese'])

            if w1_no_hon == w2_no_hon and w1_no_hon != word1['japanese'] and w2_no_hon != word2['japanese']:
                is_related = True
                relationship_type = "honorific_vs_plain"
            elif w1_no_hon == word2['japanese'] or w2_no_hon == word1['japanese']:
                is_related = True
                relationship_type = "honorific_vs_plain"

            # 2. Very similar English meanings (synonym)
            if not is_related:
                similarity = calculate_similarity(word1['english'], word2['english'])
                if similarity >= 0.85:  # High similarity threshold
                    is_related = True
                    relationship_type = "english_synonym"

            # 3. Same reading, different kanji
            if not is_related:
                if word1['reading'] == word2['reading'] and word1['japanese'] != word2['japanese']:
                    # Check if English is also similar
                    similarity = calculate_similarity(word1['english'], word2['english'])
                    if similarity >= 0.6:  # Moderate similarity for same reading
                        is_related = True
                        relationship_type = "same_reading_different_kanji"

            if is_related:
                group.append(word2)
                used_words.add(word2['japanese'])


        if len(group) > 1:
            # Calculate all pairwise English similarities within group
            similarities = []
            for j, w1 in enumerate(group):
                for w2 in group[j+1:]:
                    sim = calculate_similarity(w1['english'], w2['english'])
                    similarities.append(sim)

            avg_similarity = sum(similarities) / len(similarities) if similarities else 0

            groups.append({
                'words': group,
                'count': len(group),
                'average_similarity': avg_similarity,
                'examples': [
                    {
                        'japanese': w['japanese'],
                        'reading': w['reading'],
                        'english': w['english']
                    } for w in group
                ]
            })
            used_words.add(word1['japanese'])

    return groups

def main():
    """Main function to find and save synonym groups"""
    vocabulary = load_vocabulary()

    groups = find_synonym_groups(vocabulary)

    # Sort by group size (largest first)
    groups.sort(key=lambda g: g['count'], reverse=True)

    # Prepare output
    output = {
        "total_groups": len(groups),
        "total_words_in_groups": sum(g['count'] for g in groups),
        "groups": groups
    }

    # Save to JSON
    output_path = Path("data-preparation/synonym_groups.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Found {len(groups)} synonym groups")
    print(f"  Total words involved: {output['total_words_in_groups']}")
    print(f"  Output saved to: {output_path}")

    # Print some examples
    print("\n=== Top 10 Synonym Groups ===")
    for i, group in enumerate(groups[:10], 1):
        print(f"\n{i}. Group of {group['count']} words (similarity: {group['average_similarity']:.2%}):")
        for example in group['examples']:
            print(f"   - {example['japanese']} ({example['reading']}) = {example['english']}")

if __name__ == "__main__":
    main()
