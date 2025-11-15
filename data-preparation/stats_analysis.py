#!/usr/bin/env python3
"""Quick statistical analysis of generic hint usage."""

import json
from collections import Counter

# Load hints
with open(r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\public\data\collocation_hints.json", 'r', encoding='utf-8') as f:
    data = json.load(f)
    hints_data = data['hints']

# Track all hints used
all_hints = []
generic_patterns = ['related', 'involved', 'present', 'elements', 'items', 'aspects', 'types']

for verb, nouns in hints_data.items():
    for noun, hint in nouns.items():
        all_hints.append(hint)

# Count most common hints
hint_counter = Counter(all_hints)

print("=" * 80)
print("MOST COMMON HINTS ACROSS ALL VERBS/ADJECTIVES")
print("=" * 80)
print(f"Total hints: {len(all_hints)}")
print(f"Unique hints: {len(hint_counter)}")
print(f"\nTop 30 most common hints:\n")

for hint, count in hint_counter.most_common(30):
    pct = (count / len(all_hints)) * 100
    is_generic = any(pattern in hint.lower() for pattern in generic_patterns)
    marker = " [GENERIC]" if is_generic else ""
    print(f"{count:4d} ({pct:5.2f}%) - {hint}{marker}")

# Count generic vs non-generic
generic_count = sum(1 for hint in all_hints if any(pattern in hint.lower() for pattern in generic_patterns))
non_generic_count = len(all_hints) - generic_count

print(f"\n{'-' * 80}")
print(f"Generic hints: {generic_count} ({generic_count/len(all_hints)*100:.1f}%)")
print(f"Non-generic hints: {non_generic_count} ({non_generic_count/len(all_hints)*100:.1f}%)")
print("=" * 80)
