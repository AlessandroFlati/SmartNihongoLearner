#!/usr/bin/env python3
"""
Test optimized hint regeneration on 10 samples.
Shows how reverse hints are derived from forward hints without API calls.
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
    print("Warning: python-dotenv not installed.")

# Initialize Claude API
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def load_vocabulary():
    """Load vocabulary to get English translations"""
    vocab_path = Path("public/data/vocabulary.json")
    with open(vocab_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    vocab_dict = {}
    for word in data['vocabulary']:
        vocab_dict[word['japanese']] = word['english']
    return vocab_dict

def load_current_hints():
    """Load current forward hints file"""
    hints_path = Path("public/data/collocation_hints.json")
    with open(hints_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_forward_hint(verb_japanese, verb_english, noun_japanese, noun_english):
    """Generate forward hint via API"""
    prompt = f"""Create a clear, natural English hint for this Japanese collocation:

Verb/Adjective: {verb_japanese} ({verb_english})
Noun: {noun_japanese} ({noun_english})

Requirements:
- Be clear and direct
- Use format: "to [verb] [specific object]" or similar natural phrasing
- Keep it short (under 10 words)

Return ONLY the hint text, nothing else."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=50,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        hint = response.content[0].text.strip().strip('"\'')
        return hint
    except Exception as e:
        print(f"Error: {e}")
        return f"to {verb_english} {noun_english}"

def derive_reverse_hint(forward_hint):
    """Derive reverse hint from forward WITHOUT API call"""
    # Since hints are semantically identical, just reuse the forward hint
    return forward_hint

def test_optimized_regeneration():
    """Test on 10 samples to show the optimization"""
    print("Loading vocabulary...")
    vocab = load_vocabulary()

    print("Loading current hints...")
    hints_data = load_current_hints()

    print("\n" + "="*80)
    print("TESTING OPTIMIZED HINT REGENERATION")
    print("="*80)
    print("\nGenerating forward hints via API, deriving reverse hints automatically")
    print("This saves 50% of API calls!\n")

    results = []
    count = 0
    max_samples = 10
    api_calls = 0

    for verb_japanese, noun_hints in hints_data['hints'].items():
        if count >= max_samples:
            break

        verb_english = vocab.get(verb_japanese, verb_japanese)

        # Take first noun from this verb
        for noun_japanese, old_forward_hint in list(noun_hints.items())[:1]:
            if count >= max_samples:
                break

            noun_english = vocab.get(noun_japanese, noun_japanese)

            print(f"\n[{count+1}/{max_samples}] Processing sample {count+1}/{max_samples}")
            print(f"  Noun: {noun_english}")
            print(f"  Verb: {verb_english}")

            # Generate forward hint (API CALL)
            forward_hint = generate_forward_hint(verb_japanese, verb_english, noun_japanese, noun_english)
            api_calls += 1
            print(f"  FORWARD (API):   {forward_hint}")

            # Derive reverse hint (NO API CALL)
            reverse_hint = derive_reverse_hint(forward_hint)
            print(f"  REVERSE (derived): {reverse_hint}")

            results.append({
                'noun_japanese': noun_japanese,
                'noun_english': noun_english,
                'verb_japanese': verb_japanese,
                'verb_english': verb_english,
                'old_forward_hint': old_forward_hint,
                'new_forward_hint': forward_hint,
                'new_reverse_hint': reverse_hint
            })

            count += 1
            time.sleep(0.35)  # Rate limiting

        if count >= max_samples:
            break

    # Summary
    print("\n" + "="*80)
    print("OPTIMIZATION SUMMARY")
    print("="*80)
    print(f"\nTotal samples: {count}")
    print(f"API calls made: {api_calls}")
    print(f"Hints generated: {count * 2} (forward + reverse)")
    print(f"API savings: {count} calls (50% reduction)")
    print(f"\nCost comparison for full regeneration (2,246 pairs):")
    print(f"  Old approach: 4,492 API calls")
    print(f"  New approach: 2,246 API calls")
    print(f"  Savings: 2,246 API calls (50% reduction)")

    # Save results
    output_path = Path("data-preparation/optimized_hint_test_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Test results saved to: {output_path}")
    print("\nIf results look good, run the full optimized script:")
    print("  python data-preparation/regenerate_hints_optimized.py")

if __name__ == "__main__":
    try:
        test_optimized_regeneration()
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
