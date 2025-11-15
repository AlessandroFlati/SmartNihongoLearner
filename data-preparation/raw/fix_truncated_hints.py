"""Fix truncated hints in specialized_hints.json"""

import json
import re
from pathlib import Path

INPUT_FILE = Path('../output/specialized_hints.json')
OUTPUT_FILE = Path('../output/specialized_hints_fixed.json')

def fix_hint(hint):
    """Fix truncated hints that end with incomplete quotes."""
    # Pattern: ends with "means 'to something" (missing closing quote)
    if re.search(r"means\s+['\"]to\s+\w+$", hint):
        hint += "'"
    # Pattern: ends with "together means 'to something" (missing closing quote)
    elif re.search(r"together\s+means\s+['\"]to\s+\w+$", hint):
        hint += "'"
    # Pattern: ends with "becomes 'to something" (missing closing quote)
    elif re.search(r"becomes\s+['\"]to\s+\w+$", hint):
        hint += "'"
    # Pattern: ends with "means 'something" (missing closing quote)
    elif re.search(r"means\s+['\"][\w\s]+$", hint) and hint.count("'") % 2 == 1:
        hint += "'"
    # Pattern: ends with "together means 'something" (missing closing quote)
    elif re.search(r"together\s+means\s+['\"][\w\s]+$", hint) and hint.count("'") % 2 == 1:
        hint += "'"
    # General pattern: odd number of single quotes at the end
    elif hint.count("'") % 2 == 1 and not hint.endswith("'"):
        hint += "'"

    return hint

def main():
    print("Loading hints...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hints = data['hints']
    fixed_count = 0

    print("Fixing truncated hints...")
    for verb, noun_hints in hints.items():
        for noun, hint in noun_hints.items():
            fixed_hint = fix_hint(hint)
            if fixed_hint != hint:
                hints[verb][noun] = fixed_hint
                fixed_count += 1
                print(f"Fixed: {verb} + {noun}")
                print(f"  Before: {hint}")
                print(f"  After:  {fixed_hint}")

    print(f"\nFixed {fixed_count} hints")

    # Save fixed version
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
