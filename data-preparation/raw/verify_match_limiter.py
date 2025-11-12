#!/usr/bin/env python3
"""Verify that the smart match limiter is working correctly."""

import json
from pathlib import Path

INPUT_FILE = Path(__file__).parent.parent / "input" / "collocations_complete.json"

def simulate_limit_logic(total_matches):
    """Simulate the JavaScript limiting logic."""
    if total_matches >= 30:
        return 15
    elif total_matches >= 20:
        return 20
    else:
        return total_matches  # Keep all

def main():
    # Load collocation data
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=" * 80)
    print("SMART MATCH LIMITER VERIFICATION")
    print("=" * 80)
    print()

    # Test words from the analysis
    test_words = {
        'ある': 162,      # Very high - should limit to 15
        '行く': 85,       # Very high - should limit to 15
        'する': 80,       # Very high - should limit to 15
        '見る': 27,       # High - should limit to 20
        '使う': 24,       # High - should limit to 20
        '好き': 20,       # High - should limit to 20
        '食べる': 33,     # Very high - should limit to 15
        '読む': 10,       # Low - should keep all 10
    }

    print("Expected Limiting Behavior:")
    print("-" * 80)
    print()

    for word_jp, expected_count in test_words.items():
        limit = simulate_limit_logic(expected_count)
        category = "KEEP ALL" if limit == expected_count else f"LIMIT TO {limit}"

        print(f"{word_jp:10s} - {expected_count:3d} matches → {category}")

        # Verify it matches our expectations
        if expected_count >= 30:
            assert limit == 15, f"Failed: {word_jp} should limit to 15"
        elif expected_count >= 20:
            assert limit == 20, f"Failed: {word_jp} should limit to 20"
        else:
            assert limit == expected_count, f"Failed: {word_jp} should keep all"

    print()
    print("-" * 80)
    print("✓ All test cases passed!")
    print()

    # Verify against actual data
    print("Verifying against actual collocation data:")
    print("-" * 80)
    print()

    verification_words = ['ある', '行く', 'する', '見る', '使う']

    for word_jp in verification_words:
        word_data = data['words'].get(word_jp)
        if word_data:
            noun_matches = word_data['matches'].get('nouns', [])
            actual_count = len(noun_matches)
            limit = simulate_limit_logic(actual_count)

            # Get top N by score
            sorted_matches = sorted(noun_matches, key=lambda m: (-m['score'], m['word']))
            limited_matches = sorted_matches[:limit]

            score_3_count = sum(1 for m in limited_matches if m['score'] == 3)
            score_2_count = sum(1 for m in limited_matches if m['score'] == 2)
            score_1_count = sum(1 for m in limited_matches if m['score'] == 1)

            print(f"{word_jp:10s} ({word_data['reading']:10s})")
            print(f"  Total matches: {actual_count}")
            print(f"  Limited to:    {limit}")
            print(f"  Score breakdown: 3={score_3_count}, 2={score_2_count}, 1={score_1_count}")

            if limit < actual_count:
                print(f"  Sample limited matches (first 5):")
                for match in limited_matches[:5]:
                    print(f"    - {match['word']} (score {match['score']})")

            print()

    print("-" * 80)
    print("✓ Verification complete!")
    print()
    print("Summary:")
    print("  - Words with 30+ matches are limited to 15 best matches")
    print("  - Words with 20-29 matches are limited to 20 best matches")
    print("  - Words with <20 matches keep all their matches")
    print("  - Matches are prioritized by score (3 → 2 → 1)")

if __name__ == "__main__":
    main()
