"""
Verify the refined hints by sampling a few entries.
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def verify_hints():
    """Load and display sample hints to verify quality."""
    with open('input/collocation_hints_refined.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    hints = data['hints']

    print("Sample verbs and their refined hints:")
    print("=" * 70)

    # Sample verbs to check
    samples = ['いる', 'のむ', '行く', '食べる', '読む', 'ある', '見る']

    for verb in samples:
        if verb in hints:
            print(f"\n{verb}:")
            verb_hints = hints[verb]
            # Group by hint category
            category_groups = {}
            for noun, hint in verb_hints.items():
                if hint not in category_groups:
                    category_groups[hint] = []
                category_groups[hint].append(noun)

            for hint, nouns in sorted(category_groups.items()):
                print(f"  [{hint}]")
                print(f"    {', '.join(nouns[:10])}")
                if len(nouns) > 10:
                    print(f"    ... and {len(nouns) - 10} more")

    print("\n" + "=" * 70)
    print("\nMetadata:")
    print(f"  Version: {data['version']}")
    print(f"  Generated: {data['generated_date']}")
    print(f"  Total words: {data['total_words']}")
    print(f"  Total nouns with hints: {data['total_nouns_with_hints']}")
    print(f"  Average nouns per word: {data['total_nouns_with_hints'] / data['total_words']:.1f}")

    # Check for unique hint categories
    all_hints = set()
    for verb_hints in hints.values():
        all_hints.update(verb_hints.values())

    print(f"\n  Unique hint categories: {len(all_hints)}")
    print(f"\n  Sample categories:")
    for hint in sorted(list(all_hints))[:20]:
        print(f"    - {hint}")


if __name__ == '__main__':
    verify_hints()
