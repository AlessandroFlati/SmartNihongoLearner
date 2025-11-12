#!/usr/bin/env python3
"""Quick script to check generated hints."""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load hints
with open(r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocation_hints_refined.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hints = data['hints']

# Check specific verbs
test_verbs = ['飲む', '食べる', '見る', '買う', '行く', 'いる', 'ある', 'する']

for verb in test_verbs:
    if verb in hints:
        print(f"\n{'='*60}")
        print(f"{verb} - {len(hints[verb])} nouns")
        print('='*60)

        # Group by hint
        hint_groups = {}
        for noun, hint in hints[verb].items():
            if hint not in hint_groups:
                hint_groups[hint] = []
            hint_groups[hint].append(noun)

        # Show each hint group
        for hint, nouns in sorted(hint_groups.items(), key=lambda x: len(x[1]), reverse=True):
            noun_sample = ', '.join(nouns[:10])
            if len(nouns) > 10:
                noun_sample += f', ... ({len(nouns)} total)'
            print(f"  '{hint}': {noun_sample}")

print("\n" + "="*60)
print("HINT STATISTICS")
print("="*60)
print(f"Version: {data['version']}")
print(f"Generated: {data['generated_date']}")
print(f"Total verbs: {data['total_words']}")
print(f"Total noun-hint pairs: {data['total_nouns_with_hints']}")
print(f"Verb-specific: {data['verb_specific']}")
