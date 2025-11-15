"""
Fix malformed quotes in hint JSON files
Converts patterns like \"to travel' to \"to travel\"
"""

import json
import re
from pathlib import Path

# File paths
HINTS_FILE = Path('../../public/data/collocation_hints.json')
REVERSE_HINTS_FILE = Path('../../public/data/reverse_hints.json')

def fix_quotes(text):
    """
    Fix malformed quote patterns:
    - \"text' -> \"text\"
    - means 'text", -> means 'text'",  (missing closing single quote)
    """
    # Pattern 1: \" followed by text then ' (should be \")
    text = re.sub(r'\\"([^"\\]*?)\'', r'\\"\1\\"', text)

    # Pattern 2: means 'text", where closing ' is missing before "
    text = re.sub(r"means '([^'\"]+)\"", r"means '\1'\"", text)

    return text

def fix_json_file(file_path):
    """Fix quotes in a JSON hints file"""
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    print(f"Fixing {file_path}...")

    # Read raw content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix quotes
    fixed_content = fix_quotes(content)

    # Verify it's still valid JSON
    try:
        json.loads(fixed_content)
        print(f"✓ Valid JSON after fixes")
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON after fixes: {e}")
        return

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    # Count fixes
    pattern1_fixes = len(re.findall(r'\\"([^"]*?)\'', content))
    pattern2_fixes = len(re.findall(r"means '([^'\"]+)\"", content))
    total_fixes = pattern1_fixes + pattern2_fixes
    print(f"Fixed {total_fixes} malformed quotes (pattern1: {pattern1_fixes}, pattern2: {pattern2_fixes})")

# Fix both files
fix_json_file(HINTS_FILE)
print()
fix_json_file(REVERSE_HINTS_FILE)
