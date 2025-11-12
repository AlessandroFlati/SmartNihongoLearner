"""
Check additional sample verbs to validate hint quality across different verb types.
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_samples():
    """Load and display diverse samples to validate quality."""
    with open('input/collocation_hints_refined.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    hints = data['hints']

    print("Diverse verb samples across different categories:")
    print("=" * 80)

    # Different categories of verbs/adjectives
    samples = {
        "Movement verbs": ['行く', '来る', '帰る', '歩く', '走る'],
        "Consumption verbs": ['食べる', 'のむ', '吸う'],
        "Communication verbs": ['話す', '言う', '聞く', '読む', '書く'],
        "State verbs": ['ある', 'いる', 'なる'],
        "Action verbs": ['する', '作る', '使う', '買う', '売る'],
        "Cognitive verbs": ['知る', '分かる', '考える', '覚える'],
        "Physical verbs": ['見る', '聞く', '触る', '持つ'],
        "Common adjectives": ['良い', '悪い', '高い', '安い', '大きい', '小さい'],
    }

    for category, verbs in samples.items():
        print(f"\n{category}:")
        print("-" * 80)
        for verb in verbs:
            if verb in hints:
                verb_hints = hints[verb]
                # Count by category
                category_counts = {}
                for noun, hint in verb_hints.items():
                    category_counts[hint] = category_counts.get(hint, 0) + 1

                # Show top 5 categories by noun count
                top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]

                print(f"  {verb}: {len(verb_hints)} nouns across {len(category_counts)} categories")
                for cat, count in top_categories:
                    print(f"    - {cat} ({count} nouns)")


if __name__ == '__main__':
    check_samples()
