#!/usr/bin/env python3
"""
Final comprehensive validation of deployed collocation hints.

This script analyzes hint quality by detecting generic/overused hints
and calculating quality scores for each verb/adjective.
"""

import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
from pathlib import Path


def load_hints(filepath: str) -> Dict:
    """Load the hints JSON file and extract the hints section."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Handle both direct hints dict and nested structure
        if 'hints' in data:
            return data['hints']
        return data


def analyze_hint_distribution(hints_data: Dict) -> Dict:
    """
    Analyze hint distribution for each verb/adjective.

    Returns:
        Dict with structure:
        {
            'verb': {
                'total_nouns': int,
                'hint_distribution': Counter,
                'nouns_by_hint': defaultdict(list),
                'unique_hints': int,
                'max_hint': str,
                'max_hint_count': int,
                'max_hint_percentage': float,
                'quality_score': float
            }
        }
    """
    analysis = {}

    for verb, nouns_data in hints_data.items():
        hint_distribution = Counter()
        nouns_by_hint = defaultdict(list)

        for noun, hint in nouns_data.items():
            hint_distribution[hint] += 1
            nouns_by_hint[hint].append(noun)

        total_nouns = len(nouns_data)
        max_hint = hint_distribution.most_common(1)[0][0] if hint_distribution else ""
        max_hint_count = hint_distribution.most_common(1)[0][1] if hint_distribution else 0
        max_hint_percentage = (max_hint_count / total_nouns * 100) if total_nouns > 0 else 0

        # Calculate quality score
        # Quality Score = 100 - (max_percentage_single_hint × 2)
        quality_score = max(0, 100 - (max_hint_percentage * 2))

        analysis[verb] = {
            'total_nouns': total_nouns,
            'hint_distribution': hint_distribution,
            'nouns_by_hint': nouns_by_hint,
            'unique_hints': len(hint_distribution),
            'max_hint': max_hint,
            'max_hint_count': max_hint_count,
            'max_hint_percentage': max_hint_percentage,
            'quality_score': quality_score
        }

    return analysis


def categorize_quality(score: float) -> str:
    """Categorize quality score into bands."""
    if score >= 90:
        return "EXCELLENT"
    elif score >= 70:
        return "GOOD"
    elif score >= 50:
        return "FAIR"
    elif score >= 30:
        return "POOR"
    else:
        return "VERY POOR"


def generate_report(analysis: Dict, output_path: str):
    """Generate comprehensive validation report."""

    # Calculate overall statistics
    total_verbs = len(analysis)
    quality_counts = defaultdict(int)
    total_quality_score = 0

    for verb_data in analysis.values():
        quality = categorize_quality(verb_data['quality_score'])
        quality_counts[quality] += 1
        total_quality_score += verb_data['quality_score']

    overall_quality = total_quality_score / total_verbs if total_verbs > 0 else 0

    # Calculate coverage
    total_nouns = sum(v['total_nouns'] for v in analysis.values())
    coverage_pct = 100.0  # All have hints in the deployed file

    # Sort verbs by quality score (worst first)
    sorted_verbs = sorted(analysis.items(), key=lambda x: x[1]['quality_score'])

    # Generate report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# FINAL VALIDATION REPORT V3\n\n")

        f.write(f"## OVERALL QUALITY SCORE: {overall_quality:.1f}/100\n\n")

        f.write("## EXECUTIVE SUMMARY\n")
        f.write(f"- Coverage: {coverage_pct:.1f}%\n")
        f.write(f"- Total verbs/adjectives analyzed: {total_verbs}\n")
        f.write(f"- Total nouns covered: {total_nouns}\n")
        f.write(f"- Verbs with EXCELLENT quality (90-100): {quality_counts['EXCELLENT']}\n")
        f.write(f"- Verbs with GOOD quality (70-89): {quality_counts['GOOD']}\n")
        f.write(f"- Verbs with FAIR quality (50-69): {quality_counts['FAIR']}\n")
        f.write(f"- Verbs with POOR quality (30-49): {quality_counts['POOR']}\n")
        f.write(f"- Verbs with VERY POOR quality (0-29): {quality_counts['VERY POOR']}\n\n")

        # Worst offenders table
        f.write("## WORST OFFENDERS (Bottom 10 verbs by quality)\n\n")
        f.write("| Verb | Quality Score | Worst Hint | Usage % | Example Nouns |\n")
        f.write("|------|---------------|------------|---------|---------------|\n")

        for verb, data in sorted_verbs[:10]:
            examples = ", ".join(data['nouns_by_hint'][data['max_hint']][:5])
            f.write(f"| {verb} | {data['quality_score']:.1f} | {data['max_hint']} | "
                   f"{data['max_hint_percentage']:.1f}% | {examples} |\n")

        f.write("\n")

        # Detailed analysis for all verbs
        f.write("## DETAILED VERB ANALYSIS (All verbs)\n\n")

        for verb, data in sorted_verbs:
            quality = categorize_quality(data['quality_score'])

            f.write(f"### {verb} - Quality Score: {data['quality_score']:.1f} ({quality})\n")
            f.write(f"- Total nouns: {data['total_nouns']}\n")
            f.write(f"- Unique hints: {data['unique_hints']}\n")
            f.write(f"- Most overused hint: \"{data['max_hint']}\" "
                   f"({data['max_hint_count']} uses, {data['max_hint_percentage']:.2f}%)\n")

            # Show top 5 most used hints
            f.write("- Top 5 most used hints:\n")
            for hint, count in data['hint_distribution'].most_common(5):
                pct = (count / data['total_nouns'] * 100)
                f.write(f"  * \"{hint}\" ({count} uses, {pct:.1f}%)\n")

            # Identify specific issues
            f.write("- Specific issues:\n")
            if data['max_hint_percentage'] > 50:
                f.write(f"  * CRITICAL: \"{data['max_hint']}\" is severely overused (>{data['max_hint_percentage']:.0f}%)\n")
            elif data['max_hint_percentage'] > 30:
                f.write(f"  * WARNING: \"{data['max_hint']}\" is too generic (>{data['max_hint_percentage']:.0f}%)\n")

            # Check for generic patterns
            generic_patterns = ['related', 'various', 'different', 'general', 'common',
                              'things', 'items', 'elements', 'aspects', 'types']
            for hint in data['hint_distribution'].keys():
                hint_lower = hint.lower()
                if any(pattern in hint_lower for pattern in generic_patterns):
                    count = data['hint_distribution'][hint]
                    pct = (count / data['total_nouns'] * 100)
                    if pct > 15:
                        f.write(f"  * Generic hint detected: \"{hint}\" ({pct:.1f}%)\n")

            # Show example nouns for worst hint
            examples = ", ".join(data['nouns_by_hint'][data['max_hint']][:10])
            f.write(f"- Example nouns using worst hint: {examples}\n")

            # Suggestions for improvement
            if quality in ["VERY POOR", "POOR"]:
                f.write("- **REQUIRES IMMEDIATE ATTENTION**: Hints need semantic diversification\n")

                # Try to suggest categories based on nouns
                nouns_for_worst = data['nouns_by_hint'][data['max_hint']]
                if len(nouns_for_worst) > 5:
                    f.write(f"  * Suggested approach: Categorize {len(nouns_for_worst)} nouns into semantic groups\n")

            f.write("\n")

        # Summary statistics by quality band
        f.write("## QUALITY DISTRIBUTION SUMMARY\n\n")
        f.write("| Quality Band | Count | Percentage |\n")
        f.write("|--------------|-------|------------|\n")
        for quality in ["EXCELLENT", "GOOD", "FAIR", "POOR", "VERY POOR"]:
            count = quality_counts[quality]
            pct = (count / total_verbs * 100) if total_verbs > 0 else 0
            f.write(f"| {quality} | {count} | {pct:.1f}% |\n")

        f.write("\n")

        # Generic hint warnings
        f.write("## GENERIC HINT PATTERNS DETECTED\n\n")
        f.write("Verbs/adjectives with potentially generic hints (>30% usage of any single hint):\n\n")

        generic_verbs = [(v, d) for v, d in analysis.items() if d['max_hint_percentage'] > 30]
        generic_verbs.sort(key=lambda x: x[1]['max_hint_percentage'], reverse=True)

        for verb, data in generic_verbs:
            f.write(f"- **{verb}**: \"{data['max_hint']}\" used {data['max_hint_percentage']:.1f}% of the time\n")

        if not generic_verbs:
            f.write("No generic hint patterns detected (all hints used <30% of the time).\n")

        f.write("\n")

        # Recommendations
        f.write("## RECOMMENDATIONS\n\n")

        very_poor_count = quality_counts['VERY POOR']
        poor_count = quality_counts['POOR']

        if very_poor_count > 0:
            f.write(f"### CRITICAL: {very_poor_count} verbs/adjectives have VERY POOR quality\n")
            f.write("These require immediate regeneration with semantic categorization.\n\n")

        if poor_count > 0:
            f.write(f"### HIGH PRIORITY: {poor_count} verbs/adjectives have POOR quality\n")
            f.write("These should be regenerated with better semantic diversification.\n\n")

        fair_count = quality_counts['FAIR']
        if fair_count > 0:
            f.write(f"### MEDIUM PRIORITY: {fair_count} verbs/adjectives have FAIR quality\n")
            f.write("These could benefit from review and refinement.\n\n")

        if quality_counts['EXCELLENT'] + quality_counts['GOOD'] == total_verbs:
            f.write("### EXCELLENT: All verbs/adjectives meet quality standards!\n")
            f.write("The hints are well-diversified with minimal repetition.\n")


def main():
    """Main execution function."""
    # File paths
    hints_file = Path(r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\public\data\collocation_hints.json")
    output_file = Path(r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\FINAL_VALIDATION_V3.md")

    print("Loading hints file...")
    hints_data = load_hints(hints_file)

    print(f"Analyzing {len(hints_data)} verbs/adjectives...")
    analysis = analyze_hint_distribution(hints_data)

    print("Generating comprehensive report...")
    generate_report(analysis, output_file)

    print(f"\nReport generated: {output_file}")

    # Print summary to console
    total_verbs = len(analysis)
    quality_counts = defaultdict(int)
    total_quality_score = 0

    for verb_data in analysis.values():
        quality = categorize_quality(verb_data['quality_score'])
        quality_counts[quality] += 1
        total_quality_score += verb_data['quality_score']

    overall_quality = total_quality_score / total_verbs if total_verbs > 0 else 0

    print(f"\n{'='*60}")
    print(f"OVERALL QUALITY SCORE: {overall_quality:.1f}/100")
    print(f"{'='*60}")
    print(f"EXCELLENT (90-100): {quality_counts['EXCELLENT']}")
    print(f"GOOD (70-89):       {quality_counts['GOOD']}")
    print(f"FAIR (50-69):       {quality_counts['FAIR']}")
    print(f"POOR (30-49):       {quality_counts['POOR']}")
    print(f"VERY POOR (0-29):   {quality_counts['VERY POOR']}")
    print(f"{'='*60}")

    # Show worst offenders
    sorted_verbs = sorted(analysis.items(), key=lambda x: x[1]['quality_score'])
    print("\nWORST 5 OFFENDERS:")
    for verb, data in sorted_verbs[:5]:
        print(f"  {verb}: {data['quality_score']:.1f} - "
              f"\"{data['max_hint']}\" ({data['max_hint_percentage']:.1f}%)")


if __name__ == "__main__":
    main()
