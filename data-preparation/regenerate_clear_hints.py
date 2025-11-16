#!/usr/bin/env python3
"""
Regenerate collocation hints with clear, direct descriptions using Claude API.
Instead of cryptic rephrasing, use simple format: "to [verb] [specific object]"

Example transformations:
- OLD: "spoken words; together means 'to listen'"
- NEW: "to hear/listen to a conversation"

- OLD: "employment or task; together means 'to work'"
- NEW: "to do work/one's job"
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

    Returns a string like: "to hear/listen to a conversation"
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

def regenerate_all_hints():
    """Regenerate all collocation hints with clear descriptions"""
    # Open log file for writing
    log_path = Path("hint_regeneration_detailed.log")
    with open(log_path, 'w', encoding='utf-8') as log:
        def log_print(msg):
            """Print to both console and log file"""
            print(msg)
            log.write(msg + '\n')
            log.flush()

        log_print("Loading vocabulary...")
        vocab = load_vocabulary()

        log_print("Loading current hints...")
        hints_data = load_current_hints()

        total_verbs = len(hints_data['hints'])
        total_pairs = hints_data.get('totalPairs', 0)

        log_print(f"\nRegenerating hints for {total_verbs} verbs/adjectives ({total_pairs} total pairs)...")
        log_print("This will take some time due to API rate limits.\n")

        new_hints = {}
        processed = 0
        errors = 0

        for verb_japanese, noun_hints in hints_data['hints'].items():
            verb_english = vocab.get(verb_japanese, verb_japanese)
            log.write(f"\n[{processed+1}/{total_verbs}] Processing: {verb_japanese} ({verb_english})\n")
            log.flush()
            print(f"[{processed+1}/{total_verbs}] Processing verb/adj {processed+1}/{total_verbs}")

            new_hints[verb_japanese] = {}

            for noun_japanese, old_hint in noun_hints.items():
                noun_english = vocab.get(noun_japanese, noun_japanese)

                log.write(f"  - {noun_japanese} ({noun_english})\n")
                log.write(f"    OLD: {old_hint}\n")

                # Generate new hint
                new_hint = generate_clear_hint(verb_japanese, verb_english, noun_japanese, noun_english)
                new_hints[verb_japanese][noun_japanese] = new_hint

                log.write(f"    NEW: {new_hint}\n")
                log.flush()

                # Rate limiting: ~3 requests per second
                time.sleep(0.35)

            processed += 1

            # Save progress every 10 verbs
            if processed % 10 == 0:
                log_print(f"\n[OK] Progress checkpoint: {processed}/{total_verbs} verbs processed")
                save_hints_checkpoint(new_hints, processed, total_verbs, log)

        # Save final result
        log_print("\n\nSaving final hints...")
        save_final_hints(new_hints, total_pairs, log)

        log_print(f"\n[OK] Complete! Regenerated {processed} verbs with {total_pairs} total pairs")
        log_print(f"  Errors: {errors}")

def save_hints_checkpoint(hints, processed, total, log=None):
    """Save intermediate checkpoint"""
    checkpoint_path = Path("public/data/collocation_hints_NEW_checkpoint.json")
    data = {
        "version": "10.0.0",
        "generator": "claude-api-clear-hints",
        "model": "claude-sonnet-4-5-20250929",
        "status": f"In progress: {processed}/{total}",
        "hints": hints
    }

    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    msg = f"  Checkpoint saved to {checkpoint_path}"
    print(msg)
    if log:
        log.write(msg + '\n')
        log.flush()

def save_final_hints(hints, total_pairs, log=None):
    """Save final regenerated hints"""
    from datetime import datetime

    output_path = Path("public/data/collocation_hints_NEW.json")

    data = {
        "version": "10.0.0",
        "generator": "claude-api-clear-hints",
        "model": "claude-sonnet-4-5-20250929",
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPairs": total_pairs,
        "description": "Clear, direct hints for collocation meanings",
        "hints": hints
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    msg1 = f"[OK] Final hints saved to {output_path}"
    msg2 = "\nTo use the new hints, rename:"
    msg3 = f"  {output_path} -> public/data/collocation_hints.json"

    print(msg1)
    print(msg2)
    print(msg3)
    if log:
        log.write(msg1 + '\n')
        log.write(msg2 + '\n')
        log.write(msg3 + '\n')
        log.flush()

if __name__ == "__main__":
    try:
        regenerate_all_hints()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved to checkpoint file.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
