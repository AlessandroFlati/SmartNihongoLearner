#!/usr/bin/env python3
"""Refine collocation hints by analyzing actual noun collocations.

This script analyzes the actual collocations and creates specific, meaningful hints
that are tailored to each verb/adjective's actual usage patterns.
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
COLLOCATIONS_FILE = Path(__file__).parent.parent / "input" / "collocations_complete.json"
OLD_HINTS_FILE = Path(__file__).parent.parent / "input" / "collocation_hints.json"
OUTPUT_FILE = Path(__file__).parent.parent / "input" / "collocation_hints_refined.json"
CHECKPOINT_FILE = Path(__file__).parent / "hints_refined_checkpoint.json"
BATCH_SIZE = 5  # Process 5 words at a time (more context needed)

def load_checkpoint():
    """Load processing checkpoint."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'processed_words': [], 'hints': {}}

def save_checkpoint(checkpoint):
    """Save processing checkpoint."""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)

def refine_hints_for_word(client, word_data, old_hints):
    """Refine contextual hints for a word's collocations using Claude API.

    Args:
        client: Anthropic client
        word_data: Dictionary with word, reading, english, type, and noun matches
        old_hints: Previously generated hints for comparison

    Returns:
        Dictionary mapping noun words to refined hint text
    """
    word_jp = word_data['word']
    word_reading = word_data['reading']
    word_english = word_data['english']
    word_type = word_data['type']
    noun_matches = word_data.get('matches', {}).get('nouns', [])

    if not noun_matches:
        return {}

    # Prepare noun list with old hints
    noun_list = []
    old_word_hints = old_hints.get(word_jp, {})

    for match in noun_matches:
        noun_word = match['word']
        old_hint = old_word_hints.get(noun_word, "NOT CATEGORIZED")
        noun_list.append({
            'word': noun_word,
            'reading': match['reading'],
            'english': match['english'],
            'score': match['score'],
            'old_hint': old_hint
        })

    # Create detailed prompt for Claude
    prompt = f"""You are refining contextual hints for a Japanese vocabulary learning game.

The {word_type}: **{word_jp}** ({word_reading}) - "{word_english}"

Has these ACTUAL noun collocations:
{json.dumps(noun_list, ensure_ascii=False, indent=2)}

TASK: Create SPECIFIC, MEANINGFUL hints that:
1. Are tailored specifically to this {word_type} and its actual usage
2. Group semantically similar nouns together with the SAME hint
3. Make logical sense for the noun + {word_type} combination
4. Help learners think of the right words without being too generic
5. Fix obvious errors from the old hints (e.g., "教育" should NOT be "beverages")

EXAMPLES OF GOOD HINTS:

**する (to do):**
- 仕事, 勉強 → "work and learning activities"
- 話, 質問 → "conversation and communication"
- 買い物, 料理, 掃除 → "household tasks"
- 運動, 練習 → "physical training"
- 結婚 → "life events"

**のむ (to drink):**
- 水, お茶, コーヒー → "beverages"
- ビール, お酒, ワイン → "alcoholic drinks"
- 薬 → "medicine"

**読む (to read):**
- 本, 新聞, 雑誌 → "reading materials"
- 手紙 → "correspondence"

**着る (to wear):**
- 服, シャツ, コート → "clothing items"

IMPORTANT GUIDELINES:
- Hints should be 2-5 words in English
- Group similar nouns with the SAME hint text
- Be SPECIFIC to the actual usage context
- Avoid generic hints like "general" or "objects"
- Consider what makes sense for THIS specific {word_type}
- Look at the English meanings to understand semantic groups

Return ONLY a JSON object mapping each noun word (Japanese) to its refined hint.

Example format:
{{
  "水": "beverages",
  "コーヒー": "beverages",
  "お茶": "beverages",
  "本": "reading materials",
  "映画": "entertainment media"
}}

Return ONLY the JSON object, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract JSON from response
        response_text = response.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            # Find the first { and last }
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]

        # Try to parse JSON
        hints = json.loads(response_text)

        return hints

    except Exception as e:
        print(f"Error refining hints for {word_jp}: {e}")
        print(f"Response: {response_text[:200] if 'response_text' in locals() else 'No response'}")
        return {}

def main():
    """Main function to refine hints in batches."""
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return

    # Initialize client
    client = Anthropic(api_key=api_key)

    # Load checkpoint
    checkpoint = load_checkpoint()
    processed_words = set(checkpoint.get('processed_words', []))
    all_hints = checkpoint.get('hints', {})

    # Load collocation data
    print("Loading collocation data...")
    with open(COLLOCATIONS_FILE, 'r', encoding='utf-8') as f:
        collocation_data = json.load(f)

    # Load old hints
    print("Loading old hints...")
    with open(OLD_HINTS_FILE, 'r', encoding='utf-8') as f:
        old_hints_data = json.load(f)
    old_hints = old_hints_data.get('hints', {})

    # Get words to process (verbs and adjectives with noun matches)
    words_to_process = []
    for word_jp, word_data in collocation_data['words'].items():
        if word_data['type'] in ['verb', 'adjective']:
            noun_matches = word_data.get('matches', {}).get('nouns', [])
            if noun_matches and word_jp not in processed_words:
                words_to_process.append({
                    'word': word_jp,
                    'reading': word_data['reading'],
                    'english': word_data['english'],
                    'type': word_data['type'],
                    'matches': word_data['matches']
                })

    total_words = len(words_to_process)
    print(f"\nTotal words to process: {total_words}")
    print(f"Already processed: {len(processed_words)}")
    print(f"Remaining: {total_words}")

    if total_words == 0:
        print("\nAll words already processed!")
    else:
        # Process in batches
        batch_count = 0
        for i in range(0, total_words, BATCH_SIZE):
            batch = words_to_process[i:i + BATCH_SIZE]
            batch_count += 1

            print(f"\n{'='*60}")
            print(f"BATCH {batch_count}: Processing {len(batch)} words")
            print(f"Progress: {i + len(batch)}/{total_words} words")
            print(f"{'='*60}\n")

            for idx, word_data in enumerate(batch, 1):
                word_jp = word_data['word']
                print(f"[{idx}/{len(batch)}] Refining hints for: {word_jp} ({word_data['reading']}) - {word_data['english']}")
                print(f"  Noun collocations: {len(word_data['matches']['nouns'])}")

                # Refine hints
                hints = refine_hints_for_word(client, word_data, old_hints)

                if hints:
                    # Store hints for this word's collocations
                    all_hints[word_jp] = hints
                    processed_words.add(word_jp)

                    print(f"  ✓ Generated {len(hints)} refined hints")
                else:
                    print(f"  ✗ Failed to refine hints")

                # Save checkpoint after each word
                checkpoint['processed_words'] = list(processed_words)
                checkpoint['hints'] = all_hints
                save_checkpoint(checkpoint)

            print(f"\nBatch {batch_count} complete!")
            print(f"Total progress: {len(processed_words)}/{len(old_hints)} words")

            # Ask user to continue
            if i + BATCH_SIZE < total_words:
                response = input("\nPress Enter to continue to next batch, or 'q' to quit: ").strip().lower()
                if response == 'q':
                    print("\nStopping. Progress saved.")
                    print(f"Checkpoint: {CHECKPOINT_FILE}")
                    return

    # All done - save final output
    print(f"\n{'='*60}")
    print("ALL BATCHES COMPLETE!")
    print(f"{'='*60}\n")

    # Count total nouns
    total_nouns = sum(len(hints) for hints in all_hints.values())

    # Create output structure
    output = {
        'version': '1.1.0',
        'generated_date': '2025-11-11',
        'total_words': len(all_hints),
        'total_nouns_with_hints': total_nouns,
        'hints': all_hints
    }

    # Save final output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ Refined hints saved to: {OUTPUT_FILE}")
    print(f"✓ Total words with hints: {len(all_hints)}")
    print(f"✓ Total nouns with hints: {total_nouns}")
    print(f"\nCheckpoint file can be deleted: {CHECKPOINT_FILE}")

if __name__ == "__main__":
    main()
