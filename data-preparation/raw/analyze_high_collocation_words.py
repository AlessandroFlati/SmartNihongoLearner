#!/usr/bin/env python3
"""Analyze words with high numbers of collocations."""

import json
from pathlib import Path

INPUT_FILE = Path(__file__).parent.parent / "input" / "collocations_complete.json"
OUTPUT_FILE = Path(__file__).parent / "high_collocation_analysis.txt"

def main():
    # Load collocation data
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Analyze each word
    word_stats = []

    for word_jp, word_data in data['words'].items():
        word_type = word_data['type']
        reading = word_data['reading']
        english = word_data['english']

        if word_type in ['verb', 'adjective']:
            # Count noun matches
            noun_matches = word_data['matches'].get('nouns', [])
            total_matches = len(noun_matches)

            if total_matches > 0:
                word_stats.append({
                    'word': word_jp,
                    'reading': reading,
                    'english': english,
                    'type': word_type,
                    'total_matches': total_matches,
                    'noun_matches': noun_matches
                })

    # Sort by total matches (descending)
    word_stats.sort(key=lambda x: x['total_matches'], reverse=True)

    # Statistics
    total_words = len(word_stats)
    avg_matches = sum(w['total_matches'] for w in word_stats) / total_words if total_words > 0 else 0
    median_matches = word_stats[total_words // 2]['total_matches'] if total_words > 0 else 0

    # Find thresholds
    very_high = [w for w in word_stats if w['total_matches'] >= 30]
    high = [w for w in word_stats if 20 <= w['total_matches'] < 30]
    medium_high = [w for w in word_stats if 15 <= w['total_matches'] < 20]

    # Write report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("COLLOCATION ANALYSIS: Words with High Numbers of Matches\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total words analyzed: {total_words}\n")
        f.write(f"Average matches per word: {avg_matches:.2f}\n")
        f.write(f"Median matches per word: {median_matches}\n\n")

        f.write("=" * 80 + "\n")
        f.write("DISTRIBUTION ANALYSIS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Very High (30+ matches): {len(very_high)} words\n")
        f.write(f"High (20-29 matches): {len(high)} words\n")
        f.write(f"Medium-High (15-19 matches): {len(medium_high)} words\n\n")

        # Top 50 words with most matches
        f.write("=" * 80 + "\n")
        f.write("TOP 50 WORDS WITH MOST COLLOCATIONS\n")
        f.write("=" * 80 + "\n\n")

        for i, word in enumerate(word_stats[:50], 1):
            f.write(f"{i:2d}. {word['word']:10s} ({word['reading']:15s}) - {word['type']:10s}\n")
            f.write(f"    Matches: {word['total_matches']:3d} - {word['english'][:60]}\n")

            # Show breakdown by score
            score_3 = sum(1 for m in word['noun_matches'] if m['score'] == 3)
            score_2 = sum(1 for m in word['noun_matches'] if m['score'] == 2)
            score_1 = sum(1 for m in word['noun_matches'] if m['score'] == 1)
            f.write(f"    By Score: 3={score_3}, 2={score_2}, 1={score_1}\n\n")

        # Detailed analysis of very high words
        if very_high:
            f.write("=" * 80 + "\n")
            f.write(f"VERY HIGH COLLOCATION WORDS (30+): DETAILED ANALYSIS\n")
            f.write("=" * 80 + "\n\n")

            for word in very_high:
                f.write(f"\n{word['word']} ({word['reading']}) - {word['type']}\n")
                f.write(f"English: {word['english']}\n")
                f.write(f"Total Matches: {word['total_matches']}\n")
                f.write("-" * 80 + "\n")

                # Show all matches grouped by score
                for score in [3, 2, 1]:
                    matches_at_score = [m for m in word['noun_matches'] if m['score'] == score]
                    if matches_at_score:
                        f.write(f"\nScore {score} ({len(matches_at_score)} matches):\n")
                        for m in matches_at_score[:10]:  # Show first 10
                            f.write(f"  - {m['word']} ({m['reading']}) - {m['english'][:40]}\n")
                        if len(matches_at_score) > 10:
                            f.write(f"  ... and {len(matches_at_score) - 10} more\n")

                f.write("\n" + "=" * 80 + "\n")

        # Recommendations
        f.write("\n" + "=" * 80 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("=" * 80 + "\n\n")

        f.write("Based on the analysis:\n\n")

        if very_high:
            f.write(f"1. VERY HIGH (30+ matches): {len(very_high)} words\n")
            f.write("   Recommendation: Consider limiting to top 10-15 matches (score 3 + some score 2)\n")
            f.write("   These words are too difficult for a single game round.\n\n")

        if high:
            f.write(f"2. HIGH (20-29 matches): {len(high)} words\n")
            f.write("   Recommendation: Consider limiting to top 15-20 matches\n")
            f.write("   May be challenging but doable in a single round.\n\n")

        if medium_high:
            f.write(f"3. MEDIUM-HIGH (15-19 matches): {len(medium_high)} words\n")
            f.write("   Recommendation: Keep all matches (reasonable difficulty)\n\n")

    print(f"Analysis complete!")
    print(f"\nReport written to: {OUTPUT_FILE}")
    print(f"\nSummary:")
    print(f"  Total words analyzed: {total_words}")
    print(f"  Average matches: {avg_matches:.2f}")
    print(f"  Median matches: {median_matches}")
    print(f"\n  Very High (30+): {len(very_high)} words")
    print(f"  High (20-29): {len(high)} words")
    print(f"  Medium-High (15-19): {len(medium_high)} words")

    if very_high:
        print(f"\n  Top 10 words with most matches:")
        for i, word in enumerate(very_high[:10], 1):
            print(f"    {i:2d}. {word['word']:10s} ({word['total_matches']:3d} matches) - {word['english'][:40]}")

if __name__ == "__main__":
    main()
