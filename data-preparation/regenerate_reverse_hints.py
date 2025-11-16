#!/usr/bin/env python3
"""
Regenerate reverse collocation hints with clear, direct descriptions using Claude API.
Reverse mode: noun + verb/adjective (e.g., 仕事 + する → "to do work")

Instead of cryptic rephrasing, use simple, natural format.
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

    Returns a string like: "to do work" or "easy work"
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

def regenerate_all_reverse_hints():
    """Regenerate all reverse collocation hints with clear descriptions"""
    # Open log file for writing
    log_path = Path("reverse_hint_regeneration_detailed.log")
    with open(log_path, 'w', encoding='utf-8') as log:
        def log_print(msg):
            """Print to both console and log file"""
            print(msg)
            log.write(msg + '\n')
            log.flush()

        log_print("Loading vocabulary...")
        vocab = load_vocabulary()

        log_print("Loading current reverse hints...")
        hints_data = load_current_reverse_hints()

        total_nouns = len(hints_data['hints'])
        # Count total pairs
        total_pairs = sum(len(verbs) for verbs in hints_data['hints'].values())

        log_print(f"\nRegenerating reverse hints for {total_nouns} nouns ({total_pairs} total pairs)...")
        log_print("This will take some time due to API rate limits.\n")

        new_hints = {}
        processed = 0
        errors = 0

        for noun_japanese, verb_hints in hints_data['hints'].items():
            noun_english = vocab.get(noun_japanese, noun_japanese)
            log.write(f"\n[{processed+1}/{total_nouns}] Processing: {noun_japanese} ({noun_english})\n")
            log.flush()
            print(f"[{processed+1}/{total_nouns}] Processing noun {processed+1}/{total_nouns}")

            new_hints[noun_japanese] = {}

            for verb_japanese, old_hint in verb_hints.items():
                verb_english = vocab.get(verb_japanese, verb_japanese)

                log.write(f"  - {verb_japanese} ({verb_english})\n")
                log.write(f"    OLD: {old_hint}\n")

                # Generate new hint
                new_hint = generate_clear_reverse_hint(noun_japanese, noun_english, verb_japanese, verb_english)
                new_hints[noun_japanese][verb_japanese] = new_hint

                log.write(f"    NEW: {new_hint}\n")
                log.flush()

                # Rate limiting: ~3 requests per second
                time.sleep(0.35)

            processed += 1

            # Save progress every 10 nouns
            if processed % 10 == 0:
                log_print(f"\n[OK] Progress checkpoint: {processed}/{total_nouns} nouns processed")
                save_hints_checkpoint(new_hints, processed, total_nouns, log)

        # Save final result
        log_print("\n\nSaving final reverse hints...")
        save_final_hints(new_hints, total_pairs, log)

        log_print(f"\n[OK] Complete! Regenerated {processed} nouns with {total_pairs} total pairs")
        log_print(f"  Errors: {errors}")

def save_hints_checkpoint(hints, processed, total, log=None):
    """Save intermediate checkpoint"""
    checkpoint_path = Path("public/data/reverse_hints_NEW_checkpoint.json")
    data = {
        "version": "10.0.0",
        "generator": "claude-api-clear-hints-reverse",
        "model": "claude-sonnet-4-5-20250929",
        "mode": "reverse",
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
    """Save final regenerated reverse hints"""
    from datetime import datetime

    output_path = Path("public/data/reverse_hints_NEW.json")

    data = {
        "version": "10.0.0",
        "generator": "claude-api-clear-hints-reverse",
        "model": "claude-sonnet-4-5-20250929",
        "mode": "reverse",
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPairs": total_pairs,
        "description": "Clear, direct hints for reverse collocation meanings (noun -> verb/adjective)",
        "hints": hints
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    msg1 = f"[OK] Final reverse hints saved to {output_path}"
    msg2 = "\nTo use the new hints, rename:"
    msg3 = f"  {output_path} -> public/data/reverse_hints.json"

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
        regenerate_all_reverse_hints()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved to checkpoint file.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
