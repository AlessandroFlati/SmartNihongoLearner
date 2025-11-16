#!/usr/bin/env python3
"""
Analyze similarity between forward and reverse hints to determine if we can
optimize future regenerations by deriving one from the other.
"""

import json
from pathlib import Path
from difflib import SequenceMatcher

def load_hints():
    """Load both forward and reverse hints"""
    forward_path = Path("public/data/collocation_hints.json")
    reverse_path = Path("public/data/reverse_hints.json")

    with open(forward_path, 'r', encoding='utf-8') as f:
        forward_data = json.load(f)

    with open(reverse_path, 'r', encoding='utf-8') as f:
        reverse_data = json.load(f)

    return forward_data['hints'], reverse_data['hints']

def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def analyze_hints():
    """Compare forward and reverse hints for the same word pairs"""
    forward_hints, reverse_hints = load_hints()

    comparisons = []
    total_pairs = 0

    # Compare matching pairs
    for verb_japanese, noun_hints in forward_hints.items():
        for noun_japanese, forward_hint in noun_hints.items():
            # Check if reverse hint exists for this pair
            if noun_japanese in reverse_hints:
                reverse_noun_hints = reverse_hints[noun_japanese]
                if verb_japanese in reverse_noun_hints:
                    reverse_hint = reverse_noun_hints[verb_japanese]

                    similarity = calculate_similarity(forward_hint, reverse_hint)

                    comparisons.append({
                        'verb': verb_japanese,
                        'noun': noun_japanese,
                        'forward_hint': forward_hint,
                        'reverse_hint': reverse_hint,
                        'similarity': similarity
                    })
                    total_pairs += 1

    # Calculate statistics
    similarities = [c['similarity'] for c in comparisons]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0

    # Find examples of different similarity levels
    very_similar = [c for c in comparisons if c['similarity'] >= 0.8]
    somewhat_similar = [c for c in comparisons if 0.5 <= c['similarity'] < 0.8]
    different = [c for c in comparisons if c['similarity'] < 0.5]

    # Print analysis
    print("="*80)
    print("HINT SIMILARITY ANALYSIS")
    print("="*80)
    print(f"\nTotal matching pairs analyzed: {total_pairs}")
    print(f"Average similarity: {avg_similarity:.2%}")
    print(f"\nSimilarity distribution:")
    print(f"  Very similar (>=80%): {len(very_similar)} ({len(very_similar)/total_pairs*100:.1f}%)")
    print(f"  Somewhat similar (50-80%): {len(somewhat_similar)} ({len(somewhat_similar)/total_pairs*100:.1f}%)")
    print(f"  Different (<50%): {len(different)} ({len(different)/total_pairs*100:.1f}%)")

    # Show examples (English only to avoid Unicode errors)
    print(f"\n{'='*80}")
    print("EXAMPLES OF VERY SIMILAR PAIRS (>=80% similarity)")
    print("="*80)
    for i, example in enumerate(very_similar[:5], 1):
        print(f"\n{i}. Similarity: {example['similarity']:.1%}")
        print(f"   Forward:  {example['forward_hint']}")
        print(f"   Reverse:  {example['reverse_hint']}")

    print(f"\n{'='*80}")
    print("EXAMPLES OF SOMEWHAT SIMILAR PAIRS (50-80%)")
    print("="*80)
    for i, example in enumerate(somewhat_similar[:5], 1):
        print(f"\n{i}. Similarity: {example['similarity']:.1%}")
        print(f"   Forward:  {example['forward_hint']}")
        print(f"   Reverse:  {example['reverse_hint']}")

    print(f"\n{'='*80}")
    print("EXAMPLES OF DIFFERENT PAIRS (<50%)")
    print("="*80)
    for i, example in enumerate(different[:5], 1):
        print(f"\n{i}. Similarity: {example['similarity']:.1%}")
        print(f"   Forward:  {example['forward_hint']}")
        print(f"   Reverse:  {example['reverse_hint']}")

    # Recommendation
    print(f"\n{'='*80}")
    print("RECOMMENDATION")
    print("="*80)

    if avg_similarity >= 0.8:
        print(f"\nHINTS ARE VERY SIMILAR ({avg_similarity:.1%} average)")
        print("Recommendation: Future regenerations can derive reverse hints from forward hints")
        print("               with simple transformations, saving ~50% of API calls.")
    elif avg_similarity >= 0.6:
        print(f"\nHINTS ARE SOMEWHAT SIMILAR ({avg_similarity:.1%} average)")
        print("Recommendation: Some optimization possible, but may require careful review.")
        print("               Consider hybrid approach: derive simple cases, regenerate complex ones.")
    else:
        print(f"\nHINTS ARE QUITE DIFFERENT ({avg_similarity:.1%} average)")
        print("Recommendation: Continue regenerating both forward and reverse hints separately")
        print("               to maintain quality and clarity.")

    # Save detailed analysis
    output_path = Path("data-preparation/hint_similarity_analysis.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_pairs': total_pairs,
            'average_similarity': avg_similarity,
            'very_similar_count': len(very_similar),
            'somewhat_similar_count': len(somewhat_similar),
            'different_count': len(different),
            'very_similar_examples': very_similar[:10],
            'somewhat_similar_examples': somewhat_similar[:10],
            'different_examples': different[:10]
        }, f, ensure_ascii=False, indent=2)

    print(f"\nDetailed analysis saved to: {output_path}")

if __name__ == "__main__":
    analyze_hints()
