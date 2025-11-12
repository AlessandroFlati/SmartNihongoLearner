"""
Comprehensive validation of hint quality.

Checks:
1. Coverage: Every collocation pair has a hint
2. Specificity: No generic hints like "related items", "things that exist"
3. Length: Hints are appropriate length (2-8 words)
4. Diversity: Not too many repeated hints
"""

import json
from pathlib import Path
from collections import Counter

# Load the generated hints
HINTS_FILE = Path('../output/specialized_hints.json')
COLLOCATIONS_FILE = Path('../input/collocations_complete.json')

def load_data():
    """Load both hints and collocations."""
    with open(HINTS_FILE, 'r', encoding='utf-8') as f:
        hints_data = json.load(f)

    with open(COLLOCATIONS_FILE, 'r', encoding='utf-8') as f:
        collocations_data = json.load(f)

    return hints_data['hints'], collocations_data['words']

def validate_coverage(hints, collocations):
    """Check that every collocation pair has a hint."""
    print("=" * 80)
    print("COVERAGE VALIDATION")
    print("=" * 80)
    print()

    missing_verbs = []
    missing_pairs = []
    total_pairs = 0
    covered_pairs = 0

    for verb, verb_data in collocations.items():
        if 'matches' not in verb_data or 'nouns' not in verb_data['matches']:
            continue

        for noun_data in verb_data['matches']['nouns']:
            noun = noun_data['word']
            total_pairs += 1

            if verb not in hints:
                missing_verbs.append(verb)
                missing_pairs.append(f"{verb} + {noun}")
            elif noun not in hints[verb]:
                missing_pairs.append(f"{verb} + {noun}")
            else:
                covered_pairs += 1

    coverage_pct = (covered_pairs / total_pairs * 100) if total_pairs > 0 else 0

    print(f"Total collocation pairs: {total_pairs}")
    print(f"Covered pairs: {covered_pairs}")
    print(f"Missing pairs: {len(missing_pairs)}")
    print(f"Coverage: {coverage_pct:.1f}%")
    print()

    if missing_pairs:
        print("⚠️  Missing pairs (first 10):")
        for pair in missing_pairs[:10]:
            print(f"  - {pair}")
        print()
    else:
        print("✓ PERFECT COVERAGE - All pairs have hints!")
        print()

    return coverage_pct == 100.0

def validate_specificity(hints):
    """Check for generic/non-specific hints."""
    print("=" * 80)
    print("SPECIFICITY VALIDATION")
    print("=" * 80)
    print()

    # Generic patterns to detect
    generic_patterns = [
        'related items',
        'related elements',
        'things that exist',
        'items that exist',
        'described items',
        'activities performed',
        'elements present',
        'general',
        'various',
        'different',
        'multiple',
    ]

    generic_count = 0
    total_count = 0
    generic_examples = []

    for verb, noun_hints in hints.items():
        for noun, hint in noun_hints.items():
            total_count += 1
            hint_lower = hint.lower()

            for pattern in generic_patterns:
                if pattern in hint_lower:
                    generic_count += 1
                    if len(generic_examples) < 20:
                        generic_examples.append(f"{verb} + {noun} → '{hint}'")
                    break

    generic_pct = (generic_count / total_count * 100) if total_count > 0 else 0
    specific_pct = 100 - generic_pct

    print(f"Total hints: {total_count}")
    print(f"Generic hints: {generic_count} ({generic_pct:.1f}%)")
    print(f"Specific hints: {total_count - generic_count} ({specific_pct:.1f}%)")
    print()

    if generic_count > 0:
        print(f"⚠️  Generic hint examples (first 20):")
        for example in generic_examples:
            print(f"  - {example}")
        print()

    # Quality grade
    if specific_pct >= 95:
        print("✓ EXCELLENT - 95%+ specific hints")
        quality = "EXCELLENT"
    elif specific_pct >= 85:
        print("✓ GOOD - 85%+ specific hints")
        quality = "GOOD"
    elif specific_pct >= 70:
        print("⚠️  FAIR - 70%+ specific hints")
        quality = "FAIR"
    else:
        print("✗ POOR - Less than 70% specific hints")
        quality = "POOR"

    print()
    return quality

def validate_length(hints):
    """Check hint lengths are appropriate."""
    print("=" * 80)
    print("LENGTH VALIDATION")
    print("=" * 80)
    print()

    too_short = []
    too_long = []
    good_length = 0
    total = 0

    for verb, noun_hints in hints.items():
        for noun, hint in noun_hints.items():
            total += 1
            word_count = len(hint.split())

            if word_count < 2:
                too_short.append(f"{verb} + {noun} → '{hint}' ({word_count} word)")
            elif word_count > 8:
                too_long.append(f"{verb} + {noun} → '{hint}' ({word_count} words)")
            else:
                good_length += 1

    good_pct = (good_length / total * 100) if total > 0 else 0

    print(f"Total hints: {total}")
    print(f"Good length (2-8 words): {good_length} ({good_pct:.1f}%)")
    print(f"Too short (<2 words): {len(too_short)}")
    print(f"Too long (>8 words): {len(too_long)}")
    print()

    if too_short:
        print(f"⚠️  Too short (first 10):")
        for hint in too_short[:10]:
            print(f"  - {hint}")
        print()

    if too_long:
        print(f"⚠️  Too long (first 10):")
        for hint in too_long[:10]:
            print(f"  - {hint}")
        print()

    if good_pct >= 95:
        print("✓ EXCELLENT - 95%+ good length")
    elif good_pct >= 90:
        print("✓ GOOD - 90%+ good length")
    else:
        print("⚠️  Some hints need length adjustment")

    print()
    return good_pct

def validate_diversity(hints):
    """Check that hints are diverse (not too repetitive)."""
    print("=" * 80)
    print("DIVERSITY VALIDATION")
    print("=" * 80)
    print()

    all_hints = []
    for verb, noun_hints in hints.items():
        for noun, hint in noun_hints.items():
            all_hints.append(hint)

    hint_counts = Counter(all_hints)
    total_hints = len(all_hints)
    unique_hints = len(hint_counts)

    # Find most repeated hints
    most_common = hint_counts.most_common(20)

    print(f"Total hints: {total_hints}")
    print(f"Unique hints: {unique_hints}")
    print(f"Diversity: {unique_hints / total_hints * 100:.1f}%")
    print()

    print("Most repeated hints:")
    for hint, count in most_common:
        pct = count / total_hints * 100
        print(f"  {count:4d} ({pct:5.1f}%) - '{hint}'")
    print()

    # Check if top hint is overused
    max_count = most_common[0][1]
    max_pct = max_count / total_hints * 100

    if max_pct < 2:
        print("✓ EXCELLENT - No hint used more than 2%")
    elif max_pct < 5:
        print("✓ GOOD - Most common hint used less than 5%")
    elif max_pct < 10:
        print("⚠️  FAIR - Most common hint used less than 10%")
    else:
        print("✗ POOR - Most common hint overused")

    print()

def sample_hints(hints, n=30):
    """Show random sample of hints."""
    print("=" * 80)
    print(f"SAMPLE HINTS ({n} random examples)")
    print("=" * 80)
    print()

    samples = []
    for verb, noun_hints in hints.items():
        for noun, hint in noun_hints.items():
            samples.append(f"{verb} + {noun} → '{hint}'")
            if len(samples) >= n:
                break
        if len(samples) >= n:
            break

    for sample in samples:
        print(f"  {sample}")
    print()

def main():
    """Run all validations."""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "HINT QUALITY VALIDATION REPORT" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Load data
    hints, collocations = load_data()

    # Run validations
    coverage_ok = validate_coverage(hints, collocations)
    specificity_quality = validate_specificity(hints)
    length_pct = validate_length(hints)
    validate_diversity(hints)
    sample_hints(hints, n=30)

    # Overall summary
    print("=" * 80)
    print("OVERALL ASSESSMENT")
    print("=" * 80)
    print()

    if coverage_ok and specificity_quality in ["EXCELLENT", "GOOD"] and length_pct >= 90:
        print("🎉 SUCCESS! Hints are ready for production deployment!")
        print()
        print("Next steps:")
        print("  1. Copy specialized_hints.json to public/data/collocation_hints.json")
        print("  2. Test in the WhatCouldMatch game")
        print("  3. Monitor user feedback")
    elif coverage_ok and specificity_quality in ["FAIR", "GOOD"]:
        print("✓ ACCEPTABLE - Hints are usable but could be improved")
        print()
        print("Recommendations:")
        print("  - Consider manual review of generic hints")
        print("  - Test with users to get feedback")
    else:
        print("⚠️  NEEDS IMPROVEMENT")
        print()
        print("Issues to address:")
        if not coverage_ok:
            print("  - Missing hints for some pairs")
        if specificity_quality == "POOR":
            print("  - Too many generic hints")
        if length_pct < 90:
            print("  - Hint lengths need adjustment")

    print()

if __name__ == '__main__':
    main()
