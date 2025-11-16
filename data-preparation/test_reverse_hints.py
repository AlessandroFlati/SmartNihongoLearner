#!/usr/bin/env python3
"""
Test script: Regenerate just 10 reverse collocation hints to review quality before full run.
"""

import json
import os
import time
from pathlib import Path
from anthropic import Anthropic

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

# Initialize Claude API
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def load_vocabulary():
    """Load vocabulary to get English translations"""
    vocab_path = Path("public/data/vocabulary.json")
    with open(vocab_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create lookup dict: japanese -> english
    vocab_dict = {}
    for word in data['vocabulary']:
        vocab_dict[word['japanese']] = word['english']

    return vocab_dict

def load_current_reverse_hints():
    """Load current reverse hints file"""
    hints_path = Path("public/data/reverse_hints.json")
    with open(hints_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_clear_reverse_hint(noun_japanese, noun_english, verb_japanese, verb_english):
    """
    Generate a clear, direct hint for a noun+verb/adjective collocation using Claude API.
    """
    prompt = f"""Create a clear, natural English hint for this Japanese collocation:

Noun: {noun_japanese} ({noun_english})
Verb/Adjective: {verb_japanese} ({verb_english})

The hint should describe what this noun+verb/adjective combination means in natural English.

Requirements:
- Be clear and direct (no cryptic descriptions)
- Use natural phrasing that makes the meaning obvious
- You can mention the verb/adjective in English for clarity
- Be specific about what the combination means
- Keep it short (under 10 words)

Examples of GOOD hints:
- 仕事 + する → "to do work/one's job"
- 勉強 + 続ける → "to continue studying"
- 仕事 + 多い → "to have a lot of work"
- 人 + いい → "to be a good/nice person"
- 天気 + 悪い → "bad weather; poor weather conditions"

Return ONLY the hint text, nothing else."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=50,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        hint = response.content[0].text.strip()
        # Remove quotes if present
        hint = hint.strip('"\'')
        return hint

    except Exception as e:
        print(f"Error generating hint for {noun_japanese}+{verb_japanese}: {e}")
        # Fallback: simple template
        return f"{noun_english} {verb_english}"

def test_sample_reverse_hints():
    """Test regeneration on sample collocation pairs from different nouns"""
    print("Loading vocabulary...")
    vocab = load_vocabulary()

    print("Loading current reverse hints...")
    hints_data = load_current_reverse_hints()

    print("\n" + "="*80)
    print("TESTING: Regenerating sample reverse collocation hints from different nouns")
    print("="*80 + "\n")

    results = []
    count = 0
    max_samples = 10
    max_per_noun = 1  # Only take 1 sample from each noun

    for noun_japanese, verb_hints in hints_data['hints'].items():
        if count >= max_samples:
            break

        noun_english = vocab.get(noun_japanese, noun_japanese)

        # Take just the first verb from this noun
        for verb_japanese, old_hint in list(verb_hints.items())[:max_per_noun]:
            if count >= max_samples:
                break

            verb_english = vocab.get(verb_japanese, verb_japanese)

            print(f"\n[{count+1}/{max_samples}] Processing sample {count+1}/{max_samples}")
            print(f"  Noun: {noun_english}")
            print(f"  Verb: {verb_english}")
            print(f"  OLD HINT: {old_hint}")

            # Generate new hint
            new_hint = generate_clear_reverse_hint(noun_japanese, noun_english, verb_japanese, verb_english)
            print(f"  NEW HINT: {new_hint}")

            results.append({
                'noun_japanese': noun_japanese,
                'noun_english': noun_english,
                'verb_japanese': verb_japanese,
                'verb_english': verb_english,
                'old_hint': old_hint,
                'new_hint': new_hint
            })

            count += 1
            time.sleep(0.35)  # Rate limiting

        if count >= max_samples:
            break

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY: Old vs New Reverse Hints")
    print("="*80 + "\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['noun_english']} + {result['verb_english']}")
        print(f"   OLD: {result['old_hint']}")
        print(f"   NEW: {result['new_hint']}")
        print()

    # Save to file for review
    output_path = Path("data-preparation/reverse_hint_test_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Test results saved to: {output_path}")
    print("\nReview these samples. If they look good, run the full script:")
    print("  python data-preparation/regenerate_reverse_hints.py")

if __name__ == "__main__":
    try:
        test_sample_reverse_hints()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
