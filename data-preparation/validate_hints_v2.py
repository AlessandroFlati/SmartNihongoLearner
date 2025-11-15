"""
Comprehensive second-round validation for hint coverage and specificity.

This script performs:
1. Complete coverage check
2. Specificity analysis
3. Quality assessment
4. Detailed reporting
"""

import json
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import re


def load_json(filepath: str) -> dict:
    """
    Load JSON file and return parsed data.

    Args:
        filepath: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_pair_key(verb: str, noun: str) -> str:
    """
    Create a unique key for verb-noun pair.

    Args:
        verb: Verb in dictionary form
        noun: Noun

    Returns:
        Unique key string
    """
    return f"{verb}||{noun}"


def extract_all_pairs_from_collocations(colloc_data: dict) -> Set[str]:
    """
    Extract all verb-noun pairs from collocations_complete.json.

    Args:
        colloc_data: Parsed collocations data with structure:
                    words -> {verb} -> matches -> nouns -> list of noun objects

    Returns:
        Set of pair keys
    """
    pairs = set()

    # Handle nested 'words' key structure
    words_data = colloc_data.get('words', {})

    for verb, verb_data in words_data.items():
        if isinstance(verb_data, dict) and 'matches' in verb_data:
            matches = verb_data['matches']
            if isinstance(matches, dict) and 'nouns' in matches:
                nouns_list = matches['nouns']
                if isinstance(nouns_list, list):
                    for noun_obj in nouns_list:
                        if isinstance(noun_obj, dict) and 'word' in noun_obj:
                            noun = noun_obj['word']
                            pairs.add(create_pair_key(verb, noun))
    return pairs


def extract_all_pairs_from_hints(hints_data: dict) -> Tuple[Set[str], Dict[str, str], Dict[str, List[Tuple[str, str]]]]:
    """
    Extract all verb-noun pairs from collocation_hints.json.

    Args:
        hints_data: Parsed hints data (may have 'hints' key with nested structure)

    Returns:
        Tuple of:
        - Set of pair keys
        - Dict mapping pair key to hint phrase
        - Dict mapping hint phrase to list of (verb, noun) tuples
    """
    pairs = set()
    pair_to_hint = {}
    hint_to_pairs = defaultdict(list)

    # Handle both direct structure and nested 'hints' key
    verb_hints = hints_data.get('hints', hints_data)

    for verb, verb_data in verb_hints.items():
        if isinstance(verb_data, dict):
            for noun, hint_phrase in verb_data.items():
                # Skip if hint_phrase is not a string (metadata fields)
                if not isinstance(hint_phrase, str):
                    continue
                pair_key = create_pair_key(verb, noun)
                pairs.add(pair_key)
                pair_to_hint[pair_key] = hint_phrase
                hint_to_pairs[hint_phrase].append((verb, noun))

    return pairs, pair_to_hint, dict(hint_to_pairs)


def count_verbs_per_hint(hint_to_pairs: Dict[str, List[Tuple[str, str]]]) -> Dict[str, Set[str]]:
    """
    Count how many different verbs use each hint phrase.

    Args:
        hint_to_pairs: Mapping of hint phrases to list of (verb, noun) tuples

    Returns:
        Dict mapping hint phrase to set of verbs
    """
    hint_to_verbs = {}
    for hint_phrase, pairs in hint_to_pairs.items():
        verbs = set(verb for verb, noun in pairs)
        hint_to_verbs[hint_phrase] = verbs
    return hint_to_verbs


def analyze_hint_quality(hint_phrase: str, verb_count: int, pair_count: int) -> List[str]:
    """
    Analyze quality issues with a hint phrase.

    Args:
        hint_phrase: The hint phrase to analyze
        verb_count: Number of different verbs using this hint
        pair_count: Number of pairs using this hint

    Returns:
        List of quality issues identified
    """
    issues = []

    # Check for generic phrases
    generic_patterns = [
        "actions you do",
        "things you do",
        "activities you do",
        "people or animals",
        "objects or things",
        "places or locations",
        "abstract concepts",
        "general concepts",
    ]

    hint_lower = hint_phrase.lower()
    for pattern in generic_patterns:
        if pattern in hint_lower:
            issues.append(f"Too vague: Contains '{pattern}'")

    # Check for auto-generated markers
    if "[" in hint_phrase and "]" in hint_phrase:
        issues.append("Auto-generated: Contains [verb] markers")

    # Check for too short hints
    word_count = len(hint_phrase.split())
    if word_count <= 2:
        issues.append(f"Too short: Only {word_count} word(s)")

    # Check for high verb sharing
    if verb_count >= 10:
        issues.append(f"Extremely generic: Used by {verb_count} different verbs")
    elif verb_count >= 5:
        issues.append(f"Too generic: Used by {verb_count} different verbs")

    return issues


def generate_report(
    colloc_pairs: Set[str],
    hint_pairs: Set[str],
    pair_to_hint: Dict[str, str],
    hint_to_pairs: Dict[str, List[Tuple[str, str]]],
    hint_to_verbs: Dict[str, Set[str]],
    colloc_data: dict,
    output_path: str
) -> None:
    """
    Generate comprehensive validation report.

    Args:
        colloc_pairs: Set of all pairs from collocations data
        hint_pairs: Set of all pairs from hints data
        pair_to_hint: Mapping of pair keys to hint phrases
        hint_to_pairs: Mapping of hint phrases to pairs
        hint_to_verbs: Mapping of hint phrases to verb sets
        colloc_data: Original collocations data
        output_path: Path to write report
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# SECOND VALIDATION REPORT - HINT SPECIFICITY\n\n")

        # Executive Summary
        f.write("## EXECUTIVE SUMMARY\n\n")
        total_pairs = len(colloc_pairs)
        pairs_with_hints = len(hint_pairs)
        missing_pairs = colloc_pairs - hint_pairs
        coverage = (pairs_with_hints / total_pairs * 100) if total_pairs > 0 else 0

        f.write(f"- Total pairs in collocation data: {total_pairs}\n")
        f.write(f"- Total pairs with hints: {pairs_with_hints}\n")
        f.write(f"- Missing pairs: {len(missing_pairs)}\n")
        f.write(f"- Coverage: {coverage:.2f}%\n\n")

        # Specificity statistics
        verb_specific = sum(1 for verbs in hint_to_verbs.values() if len(verbs) == 1)
        shared_hints = sum(1 for verbs in hint_to_verbs.values() if 2 <= len(verbs) <= 4)
        generic_hints = sum(1 for verbs in hint_to_verbs.values() if len(verbs) >= 5)
        total_unique_hints = len(hint_to_verbs)

        f.write(f"- Verb-specific hints (used by 1 verb only): {verb_specific} ({verb_specific/total_unique_hints*100:.2f}%)\n")
        f.write(f"- Shared hints (used by 2-4 verbs): {shared_hints} ({shared_hints/total_unique_hints*100:.2f}%)\n")
        f.write(f"- Generic hints (used by 5+ verbs): {generic_hints} ({generic_hints/total_unique_hints*100:.2f}%)\n\n")

        # Critical Issues
        f.write("## CRITICAL ISSUES\n\n")

        # Missing pairs
        if missing_pairs:
            f.write("### Missing Pairs\n\n")
            f.write(f"**Total missing: {len(missing_pairs)}**\n\n")
            if len(missing_pairs) <= 50:
                for pair_key in sorted(missing_pairs):
                    verb, noun = pair_key.split("||")
                    f.write(f"- {verb} + {noun}\n")
            else:
                f.write("**Too many to list individually. First 50:**\n\n")
                for pair_key in sorted(list(missing_pairs)[:50]):
                    verb, noun = pair_key.split("||")
                    f.write(f"- {verb} + {noun}\n")
            f.write("\n")
        else:
            f.write("### Missing Pairs\n\n")
            f.write("**None! 100% coverage achieved.**\n\n")

        # Most generic hints
        f.write("### Most Generic Hints (Used by 10+ verbs)\n\n")
        generic_hints_list = [(hint, verbs, hint_to_pairs[hint])
                              for hint, verbs in hint_to_verbs.items()
                              if len(verbs) >= 10]
        generic_hints_list.sort(key=lambda x: len(x[1]), reverse=True)

        if generic_hints_list:
            f.write("| Hint Phrase | Verb Count | Pair Count | Sample Verbs |\n")
            f.write("|-------------|------------|------------|---------------|\n")
            for hint, verbs, pairs in generic_hints_list[:20]:
                verb_count = len(verbs)
                pair_count = len(pairs)
                sample_verbs = ", ".join(sorted(list(verbs))[:5])
                if len(verbs) > 5:
                    sample_verbs += ", ..."
                f.write(f"| {hint} | {verb_count} | {pair_count} | {sample_verbs} |\n")
            f.write("\n")
        else:
            f.write("**None found! All hints are used by fewer than 10 verbs.**\n\n")

        # Quality Issues by Category
        f.write("### Quality Issues by Category\n\n")

        # Categorize all issues
        issues_by_type = defaultdict(list)
        for hint, verbs in hint_to_verbs.items():
            pairs = hint_to_pairs[hint]
            issues = analyze_hint_quality(hint, len(verbs), len(pairs))
            for issue in issues:
                issues_by_type[issue.split(":")[0]].append((hint, len(verbs), len(pairs)))

        for issue_type, hints in sorted(issues_by_type.items()):
            f.write(f"**Category: {issue_type}**\n\n")
            # Sort by verb count descending, show top 10
            hints.sort(key=lambda x: x[1], reverse=True)
            for hint, verb_count, pair_count in hints[:10]:
                f.write(f"- \"{hint}\": Used by {verb_count} verb(s) across {pair_count} pair(s)\n")
            if len(hints) > 10:
                f.write(f"- ... and {len(hints) - 10} more\n")
            f.write("\n")

        # Verb-by-verb analysis
        f.write("## VERB-BY-VERB ANALYSIS\n\n")
        f.write("*Top 20 verbs by number of collocations*\n\n")

        # Get verb statistics
        verb_stats = {}
        # Handle nested 'words' key structure
        words_data = colloc_data.get('words', {})

        for verb, verb_data in words_data.items():
            if isinstance(verb_data, dict) and 'matches' in verb_data:
                matches = verb_data['matches']
                if isinstance(matches, dict) and 'nouns' in matches:
                    nouns_list = matches['nouns']
                    if isinstance(nouns_list, list):
                        # Extract noun words
                        nouns = [noun_obj['word'] for noun_obj in nouns_list
                                if isinstance(noun_obj, dict) and 'word' in noun_obj]
                        total_pairs = len(nouns)

                        # Count hints for this verb
                        hints_for_verb = []
                        for noun in nouns:
                            pair_key = create_pair_key(verb, noun)
                            if pair_key in pair_to_hint:
                                hints_for_verb.append(pair_to_hint[pair_key])

                        unique_hints = len(set(hints_for_verb))
                        hint_counts = defaultdict(int)
                        for hint in hints_for_verb:
                            hint_counts[hint] += 1

                        most_common_hint = None
                        most_common_count = 0
                        if hint_counts:
                            most_common_hint = max(hint_counts.items(), key=lambda x: x[1])
                            most_common_count = most_common_hint[1]
                            most_common_hint = most_common_hint[0]

                        verb_stats[verb] = {
                            'total_pairs': total_pairs,
                            'total_hints': len(hints_for_verb),
                            'unique_hints': unique_hints,
                            'most_common_hint': most_common_hint,
                            'most_common_count': most_common_count
                        }

        # Sort by total pairs
        top_verbs = sorted(verb_stats.items(), key=lambda x: x[1]['total_pairs'], reverse=True)[:20]

        for verb, stats in top_verbs:
            f.write(f"### {verb} - {stats['total_pairs']} pairs\n\n")
            f.write(f"- Total hints: {stats['total_hints']}\n")
            f.write(f"- Unique hint phrases: {stats['unique_hints']}\n")

            if stats['most_common_hint']:
                percentage = (stats['most_common_count'] / stats['total_pairs'] * 100) if stats['total_pairs'] > 0 else 0
                f.write(f"- Most common hint: \"{stats['most_common_hint']}\" ({stats['most_common_count']} pairs, {percentage:.2f}%)\n")

                # Quality assessment
                if percentage > 50:
                    f.write(f"- Quality score: **POOR** (over 50% use same hint)\n")
                elif percentage > 30:
                    f.write(f"- Quality score: **FAIR** (over 30% use same hint)\n")
                elif stats['unique_hints'] == stats['total_pairs']:
                    f.write(f"- Quality score: **EXCELLENT** (all hints unique)\n")
                else:
                    f.write(f"- Quality score: **GOOD**\n")

            f.write("\n")

        # Specificity Detailed Breakdown
        f.write("## SPECIFICITY DETAILED BREAKDOWN\n\n")
        f.write("*All hints used by 3+ verbs*\n\n")

        multi_verb_hints = [(hint, verbs, hint_to_pairs[hint])
                           for hint, verbs in hint_to_verbs.items()
                           if len(verbs) >= 3]
        multi_verb_hints.sort(key=lambda x: len(x[2]), reverse=True)

        if multi_verb_hints:
            f.write("| Hint | Verb Count | Pair Count | Verbs Using It |\n")
            f.write("|------|------------|------------|----------------|\n")
            for hint, verbs, pairs in multi_verb_hints:
                verb_count = len(verbs)
                pair_count = len(pairs)
                verb_list = ", ".join(sorted(list(verbs)))
                f.write(f"| {hint} | {verb_count} | {pair_count} | {verb_list} |\n")
            f.write("\n")
        else:
            f.write("**None found! All hints are verb-specific or shared by at most 2 verbs.**\n\n")

        # Recommendations
        f.write("## RECOMMENDATIONS\n\n")

        # Priority 1: Most generic hints
        top_generic = [(hint, verbs, pairs) for hint, verbs, pairs in
                      [(h, hint_to_verbs[h], hint_to_pairs[h]) for h in hint_to_verbs.keys()]
                      if len(verbs) >= 5]
        top_generic.sort(key=lambda x: len(x[2]), reverse=True)

        if top_generic:
            total_pairs_affected = sum(len(pairs) for _, _, pairs in top_generic)
            f.write(f"1. **HIGH PRIORITY**: Replace generic hints used by 5+ verbs ({len(top_generic)} hints, {total_pairs_affected} pairs affected)\n")
            for hint, verbs, pairs in top_generic[:5]:
                f.write(f"   - \"{hint}\" ({len(verbs)} verbs, {len(pairs)} pairs)\n")
            if len(top_generic) > 5:
                f.write(f"   - ... and {len(top_generic) - 5} more\n")
            f.write("\n")

        # Priority 2: Quality issues
        if "Too vague" in issues_by_type:
            vague_count = len(issues_by_type["Too vague"])
            f.write(f"2. **MEDIUM PRIORITY**: Improve vague hint phrases ({vague_count} hints)\n\n")

        # Priority 3: Auto-generated markers
        if "Auto-generated" in issues_by_type:
            autogen_count = len(issues_by_type["Auto-generated"])
            f.write(f"3. **LOW PRIORITY**: Remove auto-generated [verb] markers ({autogen_count} hints)\n\n")

        # Priority 4: Missing coverage
        if missing_pairs:
            f.write(f"4. **MISSING COVERAGE**: Add hints for {len(missing_pairs)} missing pairs\n\n")

        f.write("## CONCLUSION\n\n")
        f.write(f"This validation analyzed {total_pairs} verb-noun pairs and {len(hint_to_verbs)} unique hint phrases.\n")
        f.write(f"Coverage is {coverage:.2f}% with {len(missing_pairs)} missing pairs.\n")
        f.write(f"Specificity distribution: {verb_specific} verb-specific, {shared_hints} shared, {generic_hints} generic.\n\n")

        if generic_hints > 0:
            f.write("**Key finding**: The presence of generic hints suggests opportunities for improved specificity.\n")
        else:
            f.write("**Key finding**: All hints show good specificity with no generic patterns.\n")


def main():
    """Main execution function."""
    import sys
    import io

    # Set UTF-8 encoding for stdout to handle Japanese characters
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("Loading collocations data...")
    colloc_data = load_json(r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json")

    print("Loading hints data...")
    hints_data = load_json(r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\public\data\collocation_hints.json")

    print("Extracting pairs from collocations...")
    colloc_pairs = extract_all_pairs_from_collocations(colloc_data)

    print("Extracting pairs from hints...")
    hint_pairs, pair_to_hint, hint_to_pairs = extract_all_pairs_from_hints(hints_data)

    print("Analyzing hint sharing patterns...")
    hint_to_verbs = count_verbs_per_hint(hint_to_pairs)

    print("Generating comprehensive report...")
    output_path = r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\VALIDATION_REPORT_V2.md"
    generate_report(colloc_pairs, hint_pairs, pair_to_hint, hint_to_pairs, hint_to_verbs, colloc_data, output_path)

    print(f"\nReport generated: {output_path}")

    # Print summary statistics
    print("\n=== SUMMARY ===")
    print(f"Total pairs in collocations: {len(colloc_pairs)}")
    print(f"Total pairs with hints: {len(hint_pairs)}")
    print(f"Missing pairs: {len(colloc_pairs - hint_pairs)}")
    print(f"Coverage: {len(hint_pairs)/len(colloc_pairs)*100:.2f}%")
    print(f"\nUnique hint phrases: {len(hint_to_verbs)}")
    print(f"Verb-specific hints: {sum(1 for v in hint_to_verbs.values() if len(v) == 1)}")
    print(f"Generic hints (5+ verbs): {sum(1 for v in hint_to_verbs.values() if len(v) >= 5)}")

    # Top 5 most generic hints
    top_generic = sorted([(h, len(v), len(hint_to_pairs[h])) for h, v in hint_to_verbs.items()],
                        key=lambda x: x[1], reverse=True)[:5]
    print("\nTop 5 most generic hints:")
    for hint, verb_count, pair_count in top_generic:
        print(f"  - \"{hint}\": {verb_count} verbs, {pair_count} pairs")


if __name__ == "__main__":
    main()
