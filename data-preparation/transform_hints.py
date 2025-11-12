#!/usr/bin/env python3
"""
Transform hint structure from nested format to flat format.

Converts from:
{
  "verbs": {
    "verb": {
      "hints": [
        {"hint": "...", "all_nouns": [...]}
      ]
    }
  }
}

To:
{
  "version": "5.0.0",
  "hints": {
    "verb": {
      "noun": "hint text"
    }
  }
}
"""

import json
from datetime import datetime
from pathlib import Path


def transform_hints(input_file: str, output_file: str) -> None:
    """
    Transform hint structure from nested to flat format.

    Args:
        input_file: Path to the input JSON file with nested structure
        output_file: Path to save the transformed JSON file
    """
    # Load the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize the new structure
    transformed = {
        "version": "5.0.0",
        "generated_date": datetime.now().isoformat(),
        "hints": {}
    }

    # Counters for metadata
    total_words = 0
    total_nouns_with_hints = 0

    # Process each verb
    verbs_data = data.get("verbs", {})

    for verb, verb_data in verbs_data.items():
        transformed["hints"][verb] = {}

        # Process each hint for this verb
        hints = verb_data.get("hints", [])
        for hint_entry in hints:
            hint_text = hint_entry.get("hint", "")
            all_nouns = hint_entry.get("all_nouns", [])

            # Map each noun to the hint
            for noun in all_nouns:
                transformed["hints"][verb][noun] = hint_text
                total_nouns_with_hints += 1

        total_words += 1

    # Add metadata
    transformed["metadata"] = {
        "total_words": total_words,
        "total_nouns_with_hints": total_nouns_with_hints
    }

    # Save the transformed file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed, f, ensure_ascii=False, indent=2)

    print(f"Transformation complete!")
    print(f"  Verbs processed: {total_words}")
    print(f"  Total noun-hint mappings: {total_nouns_with_hints}")
    print(f"  Output file: {output_file}")

    # Verify the structure
    print("\nStructure verification:")
    print(f"  Top-level keys: {list(transformed.keys())}")
    print(f"  Sample verb keys (first 3): {list(transformed['hints'].keys())[:3]}")
    if transformed['hints']:
        first_verb = list(transformed['hints'].keys())[0]
        print(f"  Sample nouns under '{first_verb}': {list(transformed['hints'][first_verb].keys())[:3]}")
        print(f"  Sample hint: {transformed['hints'][first_verb][list(transformed['hints'][first_verb].keys())[0]]}")


if __name__ == "__main__":
    input_path = r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocation_hints_refined.json"
    output_path = r"C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\output\hints.json"

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    transform_hints(input_path, output_path)
