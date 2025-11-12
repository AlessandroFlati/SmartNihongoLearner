#!/usr/bin/env python3
"""Generate contextual hints for collocation pairs using Claude API.

This script creates helpful hints for each verb/adjective + noun combination
to guide learners without giving away direct answers.
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic

# Configuration
INPUT_FILE = Path(__file__).parent.parent / "input" / "collocations_complete.json"
OUTPUT_FILE = Path(__file__).parent.parent / "input" / "collocation_hints.json"
CHECKPOINT_FILE = Path(__file__).parent / "hints_checkpoint.json"
BATCH_SIZE = 10  # Process 10 words at a time
MAX_RETRIES = 3

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

def generate_hints_for_word(client, word_data):
    """Generate contextual hints for a word's collocations using Claude API.

    Args:
        client: Anthropic client
        word_data: Dictionary with word, reading, english, type, and noun matches

    Returns:
        Dictionary mapping noun words to hint text
    """
    word_jp = word_data['word']
    word_reading = word_data['reading']
    word_english = word_data['english']
    word_type = word_data['type']
    noun_matches = word_data.get('matches', {}).get('nouns', [])

    if not noun_matches:
        return {}

    # Prepare noun list for prompt
    noun_list = []
    for match in noun_matches:
        noun_list.append({
            'word': match['word'],
            'reading': match['reading'],
            'english': match['english'],
            'score': match['score']
        })

    # Create prompt for Claude
    prompt = f"""You are helping create contextual hints for a Japanese vocabulary learning game.

Given a {word_type}: {word_jp} ({word_reading}) - {word_english}

And its valid noun collocations:
{json.dumps(noun_list, ensure_ascii=False, indent=2)}

Generate contextual hints for learners. Each hint should:
1. Be a category or semantic group (e.g., "beverages", "furniture", "emotions")
2. Guide the learner WITHOUT revealing specific words
3. Be 2-5 words long
4. Be in English
5. Help learners think of the right category

Group similar nouns together and provide ONE hint per group.
If a noun doesn't fit any group, give it an individual hint.

Return ONLY a JSON object mapping each noun word (Japanese) to its hint text.

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
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract JSON from response
        response_text = response.content[0].text.strip()

        # Try to parse JSON
        hints = json.loads(response_text)

        return hints

    except Exception as e:
        print(f"Error generating hints for {word_jp}: {e}")
        return {}

def main():
    """Main function to generate hints in batches."""
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
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get words to process (verbs and adjectives with noun matches)
    words_to_process = []
    for word_jp, word_data in data['words'].items():
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
        print(f"Hints saved in: {OUTPUT_FILE}")
        return

    # Process in batches
    batch_count = 0
    for i in range(0, total_words, BATCH_SIZE):
        batch = words_to_process[i:i + BATCH_SIZE]
        batch_count += 1

        print(f"\n{'='*60}")
        print(f"BATCH {batch_count}: Processing {len(batch)} words")
        print(f"Progress: {i}/{total_words} words")
        print(f"{'='*60}\n")

        for idx, word_data in enumerate(batch, 1):
            word_jp = word_data['word']
            print(f"[{idx}/{len(batch)}] Generating hints for: {word_jp} ({word_data['reading']}) - {word_data['english']}")

            # Generate hints
            hints = generate_hints_for_word(client, word_data)

            if hints:
                # Store hints for this word's collocations
                if word_jp not in all_hints:
                    all_hints[word_jp] = {}

                all_hints[word_jp] = hints
                processed_words.add(word_jp)

                print(f"  ✓ Generated {len(hints)} hints")
            else:
                print(f"  ✗ Failed to generate hints")

            # Save checkpoint after each word
            checkpoint['processed_words'] = list(processed_words)
            checkpoint['hints'] = all_hints
            save_checkpoint(checkpoint)

        print(f"\nBatch {batch_count} complete!")
        print(f"Total progress: {len(processed_words)}/{len(processed_words) + total_words - i - len(batch)} words")

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

    # Create output structure
    output = {
        'version': '1.0.0',
        'generated_date': str(Path(__file__).stat().st_mtime),
        'total_words': len(all_hints),
        'hints': all_hints
    }

    # Save final output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ Hints saved to: {OUTPUT_FILE}")
    print(f"✓ Total words with hints: {len(all_hints)}")
    print(f"\nCheckpoint file can be deleted: {CHECKPOINT_FILE}")

if __name__ == "__main__":
    main()
