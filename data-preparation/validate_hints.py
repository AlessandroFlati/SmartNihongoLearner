#!/usr/bin/env python3
"""
Comprehensive validation script for collocation hints.
Validates coverage, specificity, and quality of hints.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple


class HintValidator:
    """Validates collocation hints for coverage, specificity, and quality."""

    def __init__(self, collocations_path: str, hints_path: str):
        """
        Initialize validator with input files.

        Args:
            collocations_path: Path to collocations_complete.json
            hints_path: Path to collocation_hints.json
        """
        self.collocations_path = Path(collocations_path)
        self.hints_path = Path(hints_path)

        # Load data
        with open(self.collocations_path, 'r', encoding='utf-8') as f:
            collocations_raw = json.load(f)

        # Extract words structure
        if 'words' in collocations_raw:
            # New format with nested structure
            self.collocations_data = {}
            for verb, verb_data in collocations_raw['words'].items():
                if 'matches' in verb_data and 'nouns' in verb_data['matches']:
                    # Extract just the noun words
                    self.collocations_data[verb] = [noun['word'] for noun in verb_data['matches']['nouns']]
        else:
            # Old format - direct verb to noun list mapping
            self.collocations_data = collocations_raw

        with open(self.hints_path, 'r', encoding='utf-8') as f:
            self.hints_data = json.load(f)

        self.hints = self.hints_data.get('hints', {})

        # Validation results
        self.coverage_stats = {}
        self.specificity_stats = {}
        self.quality_issues = []

    def validate_coverage(self) -> Dict:
        """
        Validate coverage of hints for all verbs and nouns.

        Returns:
            Dict containing coverage statistics
        """
        total_verbs = 0
        verbs_with_hints = 0
        verbs_without_hints = []
        total_pairs = 0
        pairs_with_hints = 0

        verb_coverage = {}

        for verb, noun_list in self.collocations_data.items():
            total_verbs += 1

            # Get hints for this verb
            verb_hints = self.hints.get(verb, {})

            # Count nouns
            total_nouns = len(noun_list)
            nouns_with_hints = 0
            missing_nouns = []

            for noun in noun_list:
                total_pairs += 1
                if noun in verb_hints:
                    nouns_with_hints += 1
                    pairs_with_hints += 1
                else:
                    missing_nouns.append(noun)

            # Calculate coverage percentage
            coverage_pct = (nouns_with_hints / total_nouns * 100) if total_nouns > 0 else 0

            verb_coverage[verb] = {
                'total_nouns': total_nouns,
                'with_hints': nouns_with_hints,
                'missing': len(missing_nouns),
                'coverage_pct': coverage_pct,
                'missing_nouns': missing_nouns
            }

            if nouns_with_hints > 0:
                verbs_with_hints += 1
            else:
                verbs_without_hints.append(verb)

        self.coverage_stats = {
            'summary': {
                'total_verbs': total_verbs,
                'verbs_with_hints': verbs_with_hints,
                'verbs_missing_hints': len(verbs_without_hints),
                'verbs_without_hints': verbs_without_hints,
                'total_pairs': total_pairs,
                'pairs_with_hints': pairs_with_hints,
                'pairs_missing_hints': total_pairs - pairs_with_hints,
                'overall_coverage_pct': (pairs_with_hints / total_pairs * 100) if total_pairs > 0 else 0
            },
            'by_verb': verb_coverage
        }

        return self.coverage_stats

    def validate_specificity(self) -> Dict:
        """
        Validate specificity of hints - check for reuse across verbs.

        Returns:
            Dict containing specificity statistics
        """
        # Track which verbs use each hint phrase
        hint_to_verbs = defaultdict(set)

        for verb, noun_hints in self.hints.items():
            for noun, hint_phrase in noun_hints.items():
                hint_to_verbs[hint_phrase].add(verb)

        # Count hint phrase usage
        total_unique_hints = len(hint_to_verbs)
        hints_in_one_verb = sum(1 for verbs in hint_to_verbs.values() if len(verbs) == 1)
        hints_in_two_verbs = sum(1 for verbs in hint_to_verbs.values() if len(verbs) == 2)
        hints_in_three_plus = sum(1 for verbs in hint_to_verbs.values() if len(verbs) >= 3)

        # Find cross-verb hints (used in 3+ verbs)
        cross_verb_hints = []
        for hint_phrase, verbs in hint_to_verbs.items():
            if len(verbs) >= 3:
                cross_verb_hints.append({
                    'hint_phrase': hint_phrase,
                    'count': len(verbs),
                    'verbs': sorted(list(verbs))
                })

        # Sort by count descending
        cross_verb_hints.sort(key=lambda x: x['count'], reverse=True)

        # Calculate specificity by verb
        verb_specificity = {}
        for verb, noun_hints in self.hints.items():
            hint_phrases = list(noun_hints.values())
            unique_hints = sum(1 for phrase in set(hint_phrases) if len(hint_to_verbs[phrase]) == 1)
            shared_hints = len(set(hint_phrases)) - unique_hints
            total_hint_types = len(set(hint_phrases))

            specificity_pct = (unique_hints / total_hint_types * 100) if total_hint_types > 0 else 0

            verb_specificity[verb] = {
                'unique_hints': unique_hints,
                'shared_hints': shared_hints,
                'total_hint_types': total_hint_types,
                'specificity_pct': specificity_pct
            }

        self.specificity_stats = {
            'summary': {
                'total_unique_hints': total_unique_hints,
                'hints_in_one_verb': hints_in_one_verb,
                'hints_in_one_verb_pct': (hints_in_one_verb / total_unique_hints * 100) if total_unique_hints > 0 else 0,
                'hints_in_two_verbs': hints_in_two_verbs,
                'hints_in_two_verbs_pct': (hints_in_two_verbs / total_unique_hints * 100) if total_unique_hints > 0 else 0,
                'hints_in_three_plus': hints_in_three_plus,
                'hints_in_three_plus_pct': (hints_in_three_plus / total_unique_hints * 100) if total_unique_hints > 0 else 0
            },
            'cross_verb_hints': cross_verb_hints,
            'by_verb': verb_specificity
        }

        return self.specificity_stats

    def validate_quality(self) -> List[Dict]:
        """
        Validate quality of hints - identify generic or vague hints.

        Returns:
            List of quality issues found
        """
        # Generic/vague terms to flag
        generic_terms = [
            'things', 'various', 'general', 'stuff', 'items', 'something',
            'activities', 'events', 'occasions', 'situations'
        ]

        # Short hints that might be too vague
        min_hint_length = 5

        for verb, noun_hints in self.hints.items():
            for noun, hint_phrase in noun_hints.items():
                # Check for generic terms
                for generic_term in generic_terms:
                    if generic_term in hint_phrase.lower():
                        self.quality_issues.append({
                            'type': 'generic_term',
                            'verb': verb,
                            'noun': noun,
                            'hint': hint_phrase,
                            'issue': f"Contains generic term '{generic_term}'"
                        })
                        break

                # Check for very short hints
                if len(hint_phrase) < min_hint_length:
                    self.quality_issues.append({
                        'type': 'too_short',
                        'verb': verb,
                        'noun': noun,
                        'hint': hint_phrase,
                        'issue': f"Hint too short (< {min_hint_length} chars)"
                    })

                # Check if hint doesn't describe relationship (just categorizes)
                # This is subjective, but we can flag single-word hints
                if ' ' not in hint_phrase:
                    self.quality_issues.append({
                        'type': 'single_word',
                        'verb': verb,
                        'noun': noun,
                        'hint': hint_phrase,
                        'issue': "Single-word hint may not describe relationship"
                    })

        return self.quality_issues

    def generate_report(self, output_path: str):
        """
        Generate comprehensive validation report in Markdown format.

        Args:
            output_path: Path to save the report
        """
        # Run all validations
        self.validate_coverage()
        self.validate_specificity()
        self.validate_quality()

        # Generate report
        report_lines = []
        report_lines.append("# COLLOCATION HINTS VALIDATION REPORT\n")
        report_lines.append(f"Generated: {self.hints_data.get('generated_date', 'Unknown')}\n")
        report_lines.append("\n---\n\n")

        # COVERAGE ANALYSIS
        report_lines.append("## 1. COVERAGE ANALYSIS\n")

        summary = self.coverage_stats['summary']
        report_lines.append("### Summary\n")
        report_lines.append(f"- **Total verbs in collocation data**: {summary['total_verbs']}\n")
        report_lines.append(f"- **Verbs with hints**: {summary['verbs_with_hints']}\n")
        report_lines.append(f"- **Verbs missing hints**: {summary['verbs_missing_hints']}\n")
        if summary['verbs_without_hints']:
            report_lines.append(f"  - Missing: {', '.join(summary['verbs_without_hints'])}\n")
        report_lines.append("\n")

        report_lines.append(f"- **Total collocation pairs**: {summary['total_pairs']}\n")
        report_lines.append(f"- **Pairs with hints**: {summary['pairs_with_hints']}\n")
        report_lines.append(f"- **Pairs missing hints**: {summary['pairs_missing_hints']}\n")
        report_lines.append(f"- **Overall coverage**: {summary['overall_coverage_pct']:.1f}%\n")
        report_lines.append("\n")

        # Coverage by verb (top 20)
        report_lines.append("### Coverage by Verb (Top 20 by Total Nouns)\n")
        report_lines.append("\n")
        report_lines.append("| Verb | Total Nouns | With Hints | Missing | Coverage % |\n")
        report_lines.append("|------|-------------|------------|---------|------------|\n")

        sorted_verbs = sorted(
            self.coverage_stats['by_verb'].items(),
            key=lambda x: x[1]['total_nouns'],
            reverse=True
        )[:20]

        for verb, stats in sorted_verbs:
            report_lines.append(
                f"| {verb} | {stats['total_nouns']} | {stats['with_hints']} | "
                f"{stats['missing']} | {stats['coverage_pct']:.1f}% |\n"
            )

        report_lines.append("\n")

        # Missing hints detail (top 10 verbs with most missing)
        report_lines.append("### Missing Hints Detail (Top 10 Verbs)\n")
        report_lines.append("\n")

        sorted_missing = sorted(
            self.coverage_stats['by_verb'].items(),
            key=lambda x: x[1]['missing'],
            reverse=True
        )[:10]

        for verb, stats in sorted_missing:
            if stats['missing'] > 0:
                report_lines.append(f"**{verb}** (missing {stats['missing']} out of {stats['total_nouns']})\n")
                missing_list = stats['missing_nouns'][:20]  # Show first 20
                report_lines.append(f"- {', '.join(missing_list)}")
                if len(stats['missing_nouns']) > 20:
                    report_lines.append(f", ... and {len(stats['missing_nouns']) - 20} more")
                report_lines.append("\n\n")

        report_lines.append("\n")

        # SPECIFICITY ANALYSIS
        report_lines.append("## 2. SPECIFICITY ANALYSIS\n")

        spec_summary = self.specificity_stats['summary']
        report_lines.append("### Summary\n")
        report_lines.append(f"- **Total unique hint phrases**: {spec_summary['total_unique_hints']}\n")
        report_lines.append(f"- **Hints used in 1 verb only**: {spec_summary['hints_in_one_verb']} "
                          f"({spec_summary['hints_in_one_verb_pct']:.1f}%)\n")
        report_lines.append(f"- **Hints used in 2 verbs**: {spec_summary['hints_in_two_verbs']} "
                          f"({spec_summary['hints_in_two_verbs_pct']:.1f}%)\n")
        report_lines.append(f"- **Hints used in 3+ verbs**: {spec_summary['hints_in_three_plus']} "
                          f"({spec_summary['hints_in_three_plus_pct']:.1f}%)\n")
        report_lines.append("\n")

        # Cross-verb hints (top 20)
        report_lines.append("### Cross-Verb Hints (Used in 3+ Verbs)\n")
        report_lines.append("\n")

        if self.specificity_stats['cross_verb_hints']:
            report_lines.append("| Hint Phrase | Count | Verbs Using It |\n")
            report_lines.append("|-------------|-------|----------------|\n")

            for hint_info in self.specificity_stats['cross_verb_hints'][:20]:
                verbs_str = ', '.join(hint_info['verbs'])
                report_lines.append(
                    f"| \"{hint_info['hint_phrase']}\" | {hint_info['count']} | {verbs_str} |\n"
                )
        else:
            report_lines.append("No hints are used in 3 or more verbs.\n")

        report_lines.append("\n")

        # Specificity by verb (top 10 most specific and least specific)
        report_lines.append("### Specificity Score by Verb\n")
        report_lines.append("\n")
        report_lines.append("**Top 10 Most Specific Verbs:**\n\n")
        report_lines.append("| Verb | Unique Hints | Shared Hints | Specificity % |\n")
        report_lines.append("|------|--------------|--------------|---------------|\n")

        sorted_spec = sorted(
            self.specificity_stats['by_verb'].items(),
            key=lambda x: x[1]['specificity_pct'],
            reverse=True
        )[:10]

        for verb, stats in sorted_spec:
            report_lines.append(
                f"| {verb} | {stats['unique_hints']} | {stats['shared_hints']} | "
                f"{stats['specificity_pct']:.1f}% |\n"
            )

        report_lines.append("\n")
        report_lines.append("**Top 10 Least Specific Verbs:**\n\n")
        report_lines.append("| Verb | Unique Hints | Shared Hints | Specificity % |\n")
        report_lines.append("|------|--------------|--------------|---------------|\n")

        sorted_spec_low = sorted(
            self.specificity_stats['by_verb'].items(),
            key=lambda x: x[1]['specificity_pct']
        )[:10]

        for verb, stats in sorted_spec_low:
            report_lines.append(
                f"| {verb} | {stats['unique_hints']} | {stats['shared_hints']} | "
                f"{stats['specificity_pct']:.1f}% |\n"
            )

        report_lines.append("\n")

        # QUALITY ISSUES
        report_lines.append("## 3. QUALITY ISSUES\n")
        report_lines.append("\n")
        report_lines.append(f"**Total quality issues found**: {len(self.quality_issues)}\n\n")

        # Group by type
        issues_by_type = defaultdict(list)
        for issue in self.quality_issues:
            issues_by_type[issue['type']].append(issue)

        for issue_type, issues in issues_by_type.items():
            report_lines.append(f"### {issue_type.replace('_', ' ').title()} ({len(issues)} issues)\n")
            report_lines.append("\n")

            # Show first 20 examples
            for issue in issues[:20]:
                report_lines.append(f"- **{issue['verb']}** + {issue['noun']}: \"{issue['hint']}\" "
                                  f"- {issue['issue']}\n")

            if len(issues) > 20:
                report_lines.append(f"\n... and {len(issues) - 20} more\n")

            report_lines.append("\n")

        # RECOMMENDATIONS
        report_lines.append("## 4. RECOMMENDATIONS\n")
        report_lines.append("\n")

        recommendations = []

        # Coverage recommendations
        if summary['pairs_missing_hints'] > 0:
            recommendations.append(
                f"1. **Add missing hints**: {summary['pairs_missing_hints']} collocation pairs "
                f"({summary['overall_coverage_pct']:.1f}% coverage) still need hints. "
                f"Priority should be given to high-frequency verbs."
            )

        # Specificity recommendations
        if spec_summary['hints_in_three_plus'] > 10:
            recommendations.append(
                f"2. **Improve specificity**: {spec_summary['hints_in_three_plus']} hint phrases "
                f"are used across 3 or more verbs. Consider making these more verb-specific "
                f"to better describe the unique relationship."
            )

        # Quality recommendations
        if issues_by_type['generic_term']:
            recommendations.append(
                f"3. **Replace generic hints**: {len(issues_by_type['generic_term'])} hints "
                f"contain generic terms like 'things' or 'various'. Replace with specific "
                f"descriptions of the verb-noun relationship."
            )

        if issues_by_type['single_word']:
            recommendations.append(
                f"4. **Expand single-word hints**: {len(issues_by_type['single_word'])} hints "
                f"are single words. Consider expanding to describe the relationship better."
            )

        # General recommendation
        recommendations.append(
            "5. **Consistency check**: Review hints across verbs to ensure consistent "
            "style and level of detail."
        )

        for rec in recommendations:
            report_lines.append(f"{rec}\n\n")

        # Write report
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(report_lines)

        print(f"Validation report generated: {output_file}")
        print(f"\nKey Statistics:")
        print(f"- Overall coverage: {summary['overall_coverage_pct']:.1f}%")
        print(f"- Pairs with hints: {summary['pairs_with_hints']}/{summary['total_pairs']}")
        print(f"- Unique hint phrases: {spec_summary['total_unique_hints']}")
        print(f"- Verb-specific hints: {spec_summary['hints_in_one_verb']} ({spec_summary['hints_in_one_verb_pct']:.1f}%)")
        print(f"- Quality issues: {len(self.quality_issues)}")


def main():
    """Main entry point for the validation script."""
    import sys
    import os

    # Determine if running in WSL and convert paths accordingly
    if 'microsoft' in os.uname().release.lower() or sys.platform == 'linux':
        # WSL paths
        base_path = "/mnt/c/Users/aless/PycharmProjects/SmartNihongoLearner"
    else:
        # Windows paths
        base_path = r"C:\Users\aless\PycharmProjects\SmartNihongoLearner"

    # File paths
    collocations_path = os.path.join(base_path, "data-preparation", "input", "collocations_complete.json")
    hints_path = os.path.join(base_path, "public", "data", "collocation_hints.json")
    output_path = os.path.join(base_path, "data-preparation", "VALIDATION_REPORT.md")

    # Create validator
    validator = HintValidator(collocations_path, hints_path)

    # Generate report
    validator.generate_report(output_path)


if __name__ == "__main__":
    main()
