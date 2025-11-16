#!/usr/bin/env python3
"""
Test script: Regenerate just 10 collocation hints to review quality before full run.
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

def load_current_hints():
    """Load current hints file"""
    hints_path = Path("public/data/collocation_hints.json")
    with open(hints_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_clear_hint(verb_japanese, verb_english, noun_japanese, noun_english):
    """
    Generate a clear, direct hint for a verb+noun collocation using Claude API.
    """
    prompt = f"""Create a clear, natural English hint for this Japanese collocation:

Verb: {verb_japanese} ({verb_english})
Noun: {noun_japanese} ({noun_english})

The hint should describe what this verb+noun combination means in natural English.

Requirements:
- Be clear and direct (no cryptic descriptions)
- Use format: "to [verb] [specific object]" or similar natural phrasing
- You can mention the verb in English for clarity
- Be specific about what the combination means
- Keep it short (under 10 words)

Examples of GOOD hints:
- 話 + 聞く → "to hear/listen to a conversation"
- 仕事 + する → "to do work/one's job"
- 音楽 + 聞く → "to listen to music"
- 質問 + する → "to ask a question"
- 手紙 + 書く → "to write a letter"

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
        print(f"Error generating hint for {verb_japanese}+{noun_japanese}: {e}")
        # Fallback: simple template
        return f"to {verb_english} {noun_english}"

def test_sample_hints():
    """Test regeneration on sample collocation pairs from different verbs"""
    print("Loading vocabulary...")
    vocab = load_vocabulary()

    print("Loading current hints...")
    hints_data = load_current_hints()

    print("\n" + "="*80)
    print("TESTING: Regenerating sample collocation hints from different verbs")
    print("="*80 + "\n")

    results = []
    count = 0
    max_samples = 10
    max_per_verb = 1  # Only take 1 sample from each verb

    for verb_japanese, noun_hints in hints_data['hints'].items():
        if count >= max_samples:
            break

        verb_english = vocab.get(verb_japanese, verb_japanese)

        # Take just the first noun from this verb
        for noun_japanese, old_hint in list(noun_hints.items())[:max_per_verb]:
            if count >= max_samples:
                break

            noun_english = vocab.get(noun_japanese, noun_japanese)

            print(f"\n[{count+1}/{max_samples}] {verb_japanese} + {noun_japanese}")
            print(f"  Verb: {verb_japanese} ({verb_english})")
            print(f"  Noun: {noun_japanese} ({noun_english})")
            print(f"  OLD HINT: {old_hint}")

            # Generate new hint
            new_hint = generate_clear_hint(verb_japanese, verb_english, noun_japanese, noun_english)
            print(f"  NEW HINT: {new_hint}")

            results.append({
                'verb_japanese': verb_japanese,
                'verb_english': verb_english,
                'noun_japanese': noun_japanese,
                'noun_english': noun_english,
                'old_hint': old_hint,
                'new_hint': new_hint
            })

            count += 1
            time.sleep(0.35)  # Rate limiting

        if count >= max_samples:
            break

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY: Old vs New Hints")
    print("="*80 + "\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['verb_japanese']}+{result['noun_japanese']}")
        print(f"   OLD: {result['old_hint']}")
        print(f"   NEW: {result['new_hint']}")
        print()

    # Save to file for review
    output_path = Path("data-preparation/hint_test_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Test results saved to: {output_path}")
    print("\nReview these samples. If they look good, run the full script:")
    print("  python data-preparation/regenerate_clear_hints.py")

if __name__ == "__main__":
    try:
        test_sample_hints()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
