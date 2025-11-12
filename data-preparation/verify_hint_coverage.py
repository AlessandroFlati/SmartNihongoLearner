"""
Systematic verification of collocation hints coverage.

This script analyzes the collocations_complete.json file against the
collocation_hints_refined.json file to ensure all verb-noun pairs have
appropriate hints assigned.
"""

import json
from collections import defaultdict
from typing import Dict, List, Tuple, Set
from pathlib import Path


def load_json_file(filepath: Path) -> Dict:
    """
    Load and parse a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Parsed JSON data as dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_verb_noun_pairs(collocations_data: Dict) -> Dict[str, Set[str]]:
    """
    Extract all verb-noun pairs from collocations data.

    Args:
        collocations_data: Complete collocations dictionary

    Returns:
        Dictionary mapping verb keys to sets of noun keys
    """
    verb_noun_pairs = defaultdict(set)

    # Extract from the 'words' section
    words_data = collocations_data.get('words', {})

    for verb_key, verb_data in words_data.items():
        if isinstance(verb_data, dict) and 'matches' in verb_data:
            matches = verb_data['matches']
            if isinstance(matches, dict) and 'nouns' in matches:
                nouns_list = matches['nouns']
                if isinstance(nouns_list, list):
                    for noun_obj in nouns_list:
                        if isinstance(noun_obj, dict) and 'word' in noun_obj:
                            verb_noun_pairs[verb_key].add(noun_obj['word'])

    return verb_noun_pairs


def analyze_hint_coverage(
    collocations_data: Dict,
    hints_data: Dict,
    verb_noun_pairs: Dict[str, Set[str]]
) -> Dict:
    """
    Analyze hint coverage across all verb-noun pairs.

    Args:
        collocations_data: Complete collocations dictionary
        hints_data: Hints dictionary
        verb_noun_pairs: Dictionary mapping verbs to their noun pairs

    Returns:
        Dictionary containing analysis results
    """
    results = {
        'total_verbs': len(verb_noun_pairs),
        'verbs_with_hints': 0,
        'verbs_without_hints': [],
        'total_noun_collocations': 0,
        'nouns_with_hints': 0,
        'nouns_without_hints': 0,
        'verb_details': [],
        'missing_hints_by_verb': defaultdict(list),
        'hint_usage': defaultdict(list),  # Maps hint phrases to list of (verb, noun) tuples
    }

    # Get the words and hints dictionaries
    words_data = collocations_data.get('words', {})
    hints_dict = hints_data.get('hints', {})

    # Analyze each verb
    for verb_key, noun_set in verb_noun_pairs.items():
        verb_info = words_data.get(verb_key, {})
        verb_display = f"{verb_info.get('word', verb_key)} ({verb_info.get('reading', '')}) - {verb_info.get('english', '')}"

        total_nouns = len(noun_set)
        results['total_noun_collocations'] += total_nouns

        # Check if verb has hints
        verb_hints = hints_dict.get(verb_key, {})

        if not verb_hints:
            results['verbs_without_hints'].append(verb_display)
            results['missing_hints_by_verb'][verb_display] = list(noun_set)
            continue

        results['verbs_with_hints'] += 1

        # Count nouns with hints
        nouns_with_hints = 0
        missing_nouns = []
        hint_distribution = defaultdict(int)

        for noun_key in noun_set:
            if noun_key in verb_hints:
                hint_phrase = verb_hints[noun_key]
                nouns_with_hints += 1
                hint_distribution[hint_phrase] += 1
                results['hint_usage'][hint_phrase].append((verb_key, noun_key))
            else:
                missing_nouns.append(noun_key)

        results['nouns_with_hints'] += nouns_with_hints
        results['nouns_without_hints'] += len(missing_nouns)

        # Store verb details
        verb_detail = {
            'verb_key': verb_key,
            'verb_display': verb_display,
            'total_nouns': total_nouns,
            'nouns_with_hints': nouns_with_hints,
            'missing_hints': len(missing_nouns),
            'hint_distribution': dict(hint_distribution),
            'missing_noun_keys': missing_nouns
        }
        results['verb_details'].append(verb_detail)

        if missing_nouns:
            results['missing_hints_by_verb'][verb_display] = missing_nouns

    # Sort verb details by total nouns (descending)
    results['verb_details'].sort(key=lambda x: x['total_nouns'], reverse=True)

    return results


def find_noun_info(noun_word: str, collocations_data: Dict) -> Dict:
    """
    Find noun information from collocations data.

    Args:
        noun_word: The noun word to search for
        collocations_data: Complete collocations dictionary

    Returns:
        Dictionary containing noun info (word, reading, english)
    """
    words_data = collocations_data.get('words', {})

    # Search through all verbs to find the noun
    for verb_data in words_data.values():
        if isinstance(verb_data, dict) and 'matches' in verb_data:
            matches = verb_data['matches']
            if isinstance(matches, dict) and 'nouns' in matches:
                nouns_list = matches['nouns']
                if isinstance(nouns_list, list):
                    for noun_obj in nouns_list:
                        if isinstance(noun_obj, dict) and noun_obj.get('word') == noun_word:
                            return noun_obj

    return {'word': noun_word, 'reading': '', 'english': ''}


def generate_markdown_report(
    results: Dict,
    collocations_data: Dict,
    output_path: Path
) -> str:
    """
    Generate a comprehensive markdown report of hint coverage.

    Args:
        results: Analysis results dictionary
        collocations_data: Complete collocations dictionary for lookups
        output_path: Path to save the markdown report

    Returns:
        Report content as string
    """
    lines = []

    # Header
    lines.append("# COLLOCATION HINTS COVERAGE REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append("This report provides a systematic verification of collocation hints")
    lines.append("to ensure complete coverage of all verb-noun pairs.")
    lines.append("")

    # Coverage Summary
    lines.append("## COVERAGE SUMMARY")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"**Total verbs in collocation data:** {results['total_verbs']}")
    lines.append(f"**Total verbs with hints:** {results['verbs_with_hints']}")

    missing_verbs_count = len(results['verbs_without_hints'])
    lines.append(f"**Missing verbs (no hints):** {missing_verbs_count}")
    lines.append("")
    lines.append(f"**Total noun collocations:** {results['total_noun_collocations']}")
    lines.append(f"**Nouns with hints:** {results['nouns_with_hints']}")
    lines.append(f"**Nouns missing hints:** {results['nouns_without_hints']}")
    lines.append("")

    # Coverage percentage
    coverage_pct = (results['nouns_with_hints'] / results['total_noun_collocations'] * 100) if results['total_noun_collocations'] > 0 else 0
    lines.append(f"**Overall Coverage:** {coverage_pct:.2f}%")
    lines.append("")

    # Detailed Breakdown by Verb (Top 20)
    lines.append("## DETAILED BREAKDOWN BY VERB (Top 20)")
    lines.append("=" * 80)
    lines.append("")

    for verb_detail in results['verb_details'][:20]:
        lines.append(f"### Verb: {verb_detail['verb_display']}")
        lines.append("")
        lines.append(f"- **Total nouns:** {verb_detail['total_nouns']}")
        lines.append(f"- **Nouns with hints:** {verb_detail['nouns_with_hints']}")
        lines.append(f"- **Missing hints:** {verb_detail['missing_hints']}")

        if verb_detail['hint_distribution']:
            lines.append("- **Sample hint distribution:**")
            # Show top 5 most common hints for this verb
            sorted_hints = sorted(
                verb_detail['hint_distribution'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for hint, count in sorted_hints[:5]:
                lines.append(f"  * \"{hint}\": {count} nouns")

        lines.append("")

    # Missing Hints Section
    if results['missing_hints_by_verb']:
        lines.append("## MISSING HINTS")
        lines.append("=" * 80)
        lines.append("")

        for verb_display, missing_nouns in list(results['missing_hints_by_verb'].items())[:10]:
            lines.append(f"### Verb: {verb_display}")
            lines.append("")
            lines.append("**Missing nouns:**")
            for noun_key in missing_nouns[:10]:  # Show first 10
                noun_info = find_noun_info(noun_key, collocations_data)
                noun_display = f"{noun_info.get('word', noun_key)} ({noun_info.get('reading', '')}) - {noun_info.get('english', '')}"
                lines.append(f"- {noun_display}")

            if len(missing_nouns) > 10:
                lines.append(f"- ... and {len(missing_nouns) - 10} more")

            lines.append("")

    # Duplicate Hint Check
    lines.append("## DUPLICATE HINT CHECK")
    lines.append("=" * 80)
    lines.append("")
    lines.append("This section identifies hints that are used across multiple verb-noun pairs,")
    lines.append("which may indicate lack of specificity.")
    lines.append("")

    # Find hints used by multiple verb-noun pairs
    multi_use_hints = {
        hint: pairs for hint, pairs in results['hint_usage'].items()
        if len(pairs) > 1
    }

    # Sort by number of uses
    sorted_multi_hints = sorted(
        multi_use_hints.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    lines.append(f"**Total unique hints:** {len(results['hint_usage'])}")
    lines.append(f"**Hints used multiple times:** {len(multi_use_hints)}")
    lines.append("")

    if sorted_multi_hints:
        lines.append("### Top 20 Most Reused Hints")
        lines.append("")

        for hint, pairs in sorted_multi_hints[:20]:
            lines.append(f"#### Hint: \"{hint}\" (used {len(pairs)} times)")
            lines.append("")

            # Check if used across different verbs
            verbs_using_hint = set(verb for verb, _ in pairs)
            if len(verbs_using_hint) > 1:
                lines.append(f"⚠️ **Used across {len(verbs_using_hint)} different verbs**")
                lines.append("")

            # Show sample pairs
            lines.append("**Sample verb-noun pairs:**")
            words_data = collocations_data.get('words', {})
            for verb_key, noun_key in pairs[:5]:
                verb_info = words_data.get(verb_key, {})
                noun_info = find_noun_info(noun_key, collocations_data)
                verb_disp = f"{verb_info.get('word', verb_key)} ({verb_info.get('reading', '')})"
                noun_disp = f"{noun_info.get('word', noun_key)} ({noun_info.get('reading', '')})"
                lines.append(f"- {verb_disp} + {noun_disp}")

            if len(pairs) > 5:
                lines.append(f"- ... and {len(pairs) - 5} more")

            lines.append("")

    # Key Findings
    lines.append("## KEY FINDINGS")
    lines.append("=" * 80)
    lines.append("")

    if coverage_pct == 100:
        lines.append("✅ **COMPLETE COVERAGE**: All verb-noun pairs have hints assigned.")
    else:
        lines.append(f"⚠️ **INCOMPLETE COVERAGE**: {results['nouns_without_hints']} noun collocations are missing hints ({100-coverage_pct:.2f}%).")

    lines.append("")

    if missing_verbs_count > 0:
        lines.append(f"⚠️ **MISSING VERBS**: {missing_verbs_count} verbs have no hints at all.")
    else:
        lines.append("✅ **ALL VERBS COVERED**: Every verb has at least some hints defined.")

    lines.append("")

    # Check hint specificity
    cross_verb_hints = sum(
        1 for hint, pairs in results['hint_usage'].items()
        if len(set(verb for verb, _ in pairs)) > 1
    )

    if cross_verb_hints > 0:
        pct_cross_verb = (cross_verb_hints / len(results['hint_usage']) * 100) if results['hint_usage'] else 0
        lines.append(f"⚠️ **HINT SPECIFICITY**: {cross_verb_hints} hints ({pct_cross_verb:.1f}%) are used across different verbs, which may indicate lack of specificity.")
    else:
        lines.append("✅ **HINT SPECIFICITY**: All hints are specific to individual verbs.")

    lines.append("")

    # Write to file
    report_content = "\n".join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return report_content


def main():
    """Main execution function."""
    # Define paths
    base_dir = Path(__file__).parent
    collocations_path = base_dir / "input" / "collocations_complete.json"
    hints_path = base_dir / "input" / "collocation_hints_refined.json"
    output_path = base_dir / "HINT_COVERAGE_REPORT.md"

    print("Loading collocation data...")
    collocations_data = load_json_file(collocations_path)

    print("Loading hints data...")
    hints_data = load_json_file(hints_path)

    print("Extracting verb-noun pairs...")
    verb_noun_pairs = extract_verb_noun_pairs(collocations_data)

    print("Analyzing hint coverage...")
    results = analyze_hint_coverage(collocations_data, hints_data, verb_noun_pairs)

    print("Generating markdown report...")
    generate_markdown_report(results, collocations_data, output_path)

    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total verbs: {results['total_verbs']}")
    print(f"Verbs with hints: {results['verbs_with_hints']}")
    print(f"Total noun collocations: {results['total_noun_collocations']}")
    print(f"Nouns with hints: {results['nouns_with_hints']}")
    print(f"Nouns missing hints: {results['nouns_without_hints']}")

    coverage_pct = (results['nouns_with_hints'] / results['total_noun_collocations'] * 100) if results['total_noun_collocations'] > 0 else 0
    print(f"Overall coverage: {coverage_pct:.2f}%")
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
