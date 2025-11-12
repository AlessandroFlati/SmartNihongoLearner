"""
Generate Specialized Collocation Hints using Claude API

This script generates specific, conversational hints for each verb-noun collocation pair.
Each hint is tailored to the exact relationship between the verb and noun.

Example hints:
- のむ + 水 → "things you can drink"
- 盗む + お金 → "things that can be stolen"
- する + 仕事 → "activities you perform"
"""

import json
import os
import time
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path('../../.env'))

# Configuration
INPUT_FILE = Path('../input/collocations_complete.json')
OUTPUT_FILE = Path('../output/specialized_hints.json')
CHECKPOINT_FILE = Path('../output/hints_checkpoint.json')
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# API settings
MODEL = 'claude-sonnet-4-5-20250929'  # Claude Sonnet 4.5 (latest and most capable)
MAX_TOKENS = 100
BATCH_SIZE = 50  # Save checkpoint every 50 pairs
RATE_LIMIT_DELAY = 0.5  # 500ms between requests to respect rate limits

def load_collocations():
    """Load collocation data from JSON file."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['words']

def load_checkpoint():
    """Load existing checkpoint if it exists."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_checkpoint(hints):
    """Save checkpoint to avoid losing progress."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(hints, f, ensure_ascii=False, indent=2)
    print(f"Checkpoint saved: {len(hints)} verbs processed")

def generate_hint_prompt(verb_data, noun_data):
    """
    Generate a prompt for Claude to create a NOUN-SPECIFIC hint.

    The verb is KNOWN, the noun is the TARGET to guess.
    The hint describes characteristics of the NOUN, not the verb action.
    """
    verb = verb_data['word']
    verb_reading = verb_data['reading']
    verb_english = verb_data['english']

    noun = noun_data['word']
    noun_reading = noun_data['reading']
    noun_english = noun_data['english']

    return f"""You are creating hints for Japanese vocabulary learning.

CONTEXT: The learner knows the verb "{verb}" ({verb_english}). They need to guess which NOUN pairs with it.

Your hint should describe the NOUN "{noun}" ({noun_english}) AND hint at the nuanced meaning of this collocation.

CRITICAL RULES:
- DO NOT just describe the verb action (avoid "things you eat", "items you buy")
- DO describe the NOUN itself with characteristics that hint at the collocation meaning
- Remember: Japanese collocations often have nuanced meanings (e.g., 仕事する = "to work", not literally "do work")
- Include the collocation nuance in your hint
- 2-8 words maximum
- Creative and memorable

GOOD EXAMPLES (describing noun + collocation nuance):
- する + 仕事 → "employment; makes verb mean 'to work'"
- する + 電話 → "device; together means 'to call'"
- する + 勉強 → "learning; becomes 'to study'"
- 食べる + りんご → "Eden's fruit, crunchy and healthy"
- 食べる + パン → "daily bread, breakfast staple"
- 食べる + 一人前 → "single serving portion"
- 買う + 本 → "reading material with bound pages"
- 買う + 車 → "expensive motorized transportation"
- 話す + 英語 → "global business language"
- のむ + 薬 → "medicine taken orally"

BAD EXAMPLES (these just describe the verb):
- "things you eat" ✗
- "items you purchase" ✗
- "languages you speak" ✗
- "activities you perform" ✗

Your hint for {noun} ({noun_english}) when paired with {verb} ({verb_english}):"""

def generate_hint(client, verb_data, noun_data):
    """
    Generate a specialized hint for a single verb-noun pair using Claude API.
    """
    prompt = generate_hint_prompt(verb_data, noun_data)

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        hint = message.content[0].text.strip()

        # Clean up the hint (remove only outer quotes and leading/trailing punctuation)
        # Remove outer quotes if present
        if (hint.startswith('"') and hint.endswith('"')) or (hint.startswith("'") and hint.endswith("'")):
            hint = hint[1:-1]

        # Remove trailing punctuation only (but preserve quotes within the text)
        hint = hint.rstrip('.,;:!?')

        # Validate length (2-8 words)
        word_count = len(hint.split())
        if word_count > 8:
            print(f"Warning: Hint too long ({word_count} words): {hint}")
            # Truncate at 8 words
            hint = ' '.join(hint.split()[:8])

        return hint

    except Exception as e:
        print(f"Error generating hint for {verb_data['word']} + {noun_data['word']}: {e}")
        return "related items"  # Fallback

def main():
    """Main execution function."""
    print("=" * 80)
    print("SPECIALIZED HINT GENERATION")
    print("=" * 80)
    print()

    # Check for API key
    if not API_KEY:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Initialize Claude client
    client = anthropic.Anthropic(api_key=API_KEY)

    # Load data
    print("Loading collocation data...")
    collocations = load_collocations()
    print(f"Loaded {len(collocations)} verbs/adjectives")
    print()

    # Load checkpoint if exists
    hints = load_checkpoint()
    if hints:
        print(f"Resuming from checkpoint: {len(hints)} verbs already processed")
        print()

    # Calculate total pairs (skip entries without matches)
    total_pairs = 0
    for data in collocations.values():
        if 'matches' in data and 'nouns' in data['matches']:
            total_pairs += len(data['matches']['nouns'])

    processed_pairs = sum(len(noun_hints) for noun_hints in hints.values())
    print(f"Total pairs to process: {total_pairs}")
    print(f"Already processed: {processed_pairs}")
    print(f"Remaining: {total_pairs - processed_pairs}")
    print()

    # Estimate cost
    estimated_cost = (total_pairs - processed_pairs) * 0.003  # ~$0.003 per request with Sonnet 4.5
    print(f"Estimated cost: ${estimated_cost:.2f}")
    print()
    print("Starting generation...")
    print("-" * 80)

    start_time = time.time()
    batch_counter = 0

    # Process each verb
    for verb, verb_data in collocations.items():
        # Skip if already processed
        if verb in hints:
            continue

        # Skip if no noun matches
        if 'matches' not in verb_data or 'nouns' not in verb_data['matches']:
            continue

        hints[verb] = {}

        # Process each noun for this verb
        for noun_data in verb_data['matches']['nouns']:
            noun = noun_data['word']

            # Generate hint using Claude
            hint = generate_hint(client, verb_data, noun_data)
            hints[verb][noun] = hint

            batch_counter += 1
            processed_pairs += 1

            # Progress indicator
            if batch_counter % 10 == 0:
                elapsed = time.time() - start_time
                rate = batch_counter / elapsed
                remaining = total_pairs - processed_pairs
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60

                print(f"Progress: {processed_pairs}/{total_pairs} pairs "
                      f"({processed_pairs/total_pairs*100:.1f}%) | "
                      f"Rate: {rate:.1f} pairs/sec | "
                      f"ETA: {eta_minutes:.1f} minutes")

            # Save checkpoint every BATCH_SIZE pairs
            if batch_counter % BATCH_SIZE == 0:
                save_checkpoint(hints)

            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)

        # Save checkpoint after each verb
        save_checkpoint(hints)

    # Final save
    print()
    print("-" * 80)
    print("Generation complete!")
    print()

    # Create final output file
    output_data = {
        "version": "9.0.0",
        "generator": "claude-api-specialized",
        "model": MODEL,
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "totalPairs": total_pairs,
        "hints": hints
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved to: {OUTPUT_FILE}")
    print()

    # Statistics
    elapsed = time.time() - start_time
    print("Statistics:")
    print(f"  Total pairs processed: {total_pairs}")
    print(f"  Time elapsed: {elapsed/60:.1f} minutes")
    print(f"  Average rate: {total_pairs/elapsed:.1f} pairs/second")
    print(f"  Verbs processed: {len(hints)}")
    print()

    # Clean up checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("✓ Checkpoint file removed")

if __name__ == '__main__':
    main()
