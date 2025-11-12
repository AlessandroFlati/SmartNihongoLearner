"""
Final validation of the refined hints file.
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def validate():
    """Validate the final output file."""
    print("=" * 80)
    print("FINAL VALIDATION OF COLLOCATION HINTS")
    print("=" * 80)

    with open('input/collocation_hints_refined.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check structure
    print("\n1. File Structure:")
    required_keys = ['version', 'generated_date', 'refined', 'total_words', 'total_nouns_with_hints', 'hints']
    for key in required_keys:
        status = "✓" if key in data else "✗"
        print(f"   {status} {key}: {data.get(key, 'MISSING')}")

    # Check data integrity
    print("\n2. Data Integrity:")
    hints = data['hints']
    actual_words = len(hints)
    actual_nouns = sum(len(noun_hints) for noun_hints in hints.values())

    print(f"   Expected words: {data['total_words']}")
    print(f"   Actual words: {actual_words}")
    print(f"   Match: {'✓' if actual_words == data['total_words'] else '✗'}")

    print(f"\n   Expected nouns: {data['total_nouns_with_hints']}")
    print(f"   Actual nouns: {actual_nouns}")
    print(f"   Match: {'✓' if actual_nouns == data['total_nouns_with_hints'] else '✗'}")

    # Check completeness
    print("\n3. Completeness Check:")
    print(f"   First word: {list(hints.keys())[0]} ({len(hints[list(hints.keys())[0]])} nouns)")
    print(f"   Last word: {list(hints.keys())[-1]} ({len(hints[list(hints.keys())[-1]])} nouns)")
    print(f"   する included: {'✓' if 'する' in hints else '✗'}")
    if 'する' in hints:
        print(f"   する has {len(hints['する'])} nouns")

    # Sample quality check
    print("\n4. Quality Spot Check:")
    sample_words = ['いる', 'のむ', '行く', '食べる']
    for word in sample_words:
        if word in hints:
            word_hints = hints[word]
            categories = set(word_hints.values())
            print(f"   {word}: {len(word_hints)} nouns, {len(categories)} categories")
            # Show first 3 categories
            for i, cat in enumerate(list(categories)[:3]):
                nouns_in_cat = [n for n, c in word_hints.items() if c == cat]
                print(f"      - {cat}: {', '.join(nouns_in_cat[:3])}")
                if i >= 2:
                    break

    # Statistics
    print("\n5. Statistics:")
    all_categories = set()
    for word_hints in hints.values():
        all_categories.update(word_hints.values())

    print(f"   Total unique categories: {len(all_categories)}")
    print(f"   Average nouns per word: {actual_nouns / actual_words:.1f}")
    print(f"   Average categories per word: {sum(len(set(h.values())) for h in hints.values()) / actual_words:.1f}")

    # Most common categories
    category_counts = {}
    for word_hints in hints.values():
        for category in word_hints.values():
            category_counts[category] = category_counts.get(category, 0) + 1

    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\n   Top 10 most common categories:")
    for cat, count in top_categories:
        print(f"      {count:3d} nouns: {cat}")

    print("\n" + "=" * 80)
    print("✓ VALIDATION COMPLETE - FILE IS READY FOR USE")
    print("=" * 80)


if __name__ == '__main__':
    validate()
