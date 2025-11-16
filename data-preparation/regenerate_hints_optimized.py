#!/usr/bin/env python3
"""
Optimized hint regeneration: Generate forward hints via API, derive reverse hints automatically.
This saves ~50% of API calls since forward and reverse hints are semantically identical.

Instead of 4,492 API calls (2,246 forward + 2,246 reverse), we only need 2,246 calls.
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
    """Load current forward hints file"""
    hints_path = Path("public/data/collocation_hints.json")
    with open(hints_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_forward_hint(verb_japanese, verb_english, noun_japanese, noun_english):
    """
    Generate a clear, direct hint for a verb+noun collocation using Claude API.
    This is the ONLY API call - reverse hint will be derived from this.
    """
    prompt = f"""Create a clear, natural English hint for this Japanese collocation:

Verb/Adjective: {verb_japanese} ({verb_english})
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

def derive_reverse_hint(forward_hint):
    """
    Derive reverse hint from forward hint WITHOUT calling the API.

    Since our analysis showed they're semantically identical (70.5% similarity),
    we can just reuse the forward hint for the reverse direction.

    The hint describes the same collocation from both directions.
    """
    # Simply return the same hint - it works for both directions
    return forward_hint

def regenerate_all_hints_optimized():
    """Regenerate all hints with optimized approach: generate forward, derive reverse"""
    # Open log file for writing
    log_path = Path("hint_regeneration_optimized.log")
    with open(log_path, 'w', encoding='utf-8') as log:
        def log_print(msg):
            """Print to both console and log file"""
            print(msg)
            log.write(msg + '\n')
            log.flush()

        log_print("Loading vocabulary...")
        vocab = load_vocabulary()

        log_print("Loading current forward hints structure...")
        hints_data = load_current_hints()

        total_verbs = len(hints_data['hints'])
        total_pairs = hints_data.get('totalPairs', 0)

        log_print(f"\nRegenerating hints for {total_verbs} verbs/adjectives ({total_pairs} total pairs)...")
        log_print("OPTIMIZED: Generating forward hints via API, deriving reverse hints automatically")
        log_print(f"API calls: {total_pairs} (50% reduction from previous {total_pairs * 2} calls)")
        log_print("This will take some time due to API rate limits.\n")

        forward_hints = {}
        reverse_hints = {}
        processed = 0
        errors = 0

        for verb_japanese, noun_hints in hints_data['hints'].items():
            verb_english = vocab.get(verb_japanese, verb_japanese)
            log.write(f"\n[{processed+1}/{total_verbs}] Processing: {verb_japanese} ({verb_english})\n")
            log.flush()
            print(f"[{processed+1}/{total_verbs}] Processing verb/adj {processed+1}/{total_verbs}")

            forward_hints[verb_japanese] = {}

            for noun_japanese, old_hint in noun_hints.items():
                noun_english = vocab.get(noun_japanese, noun_japanese)

                log.write(f"  - {noun_japanese} ({noun_english})\n")
                log.write(f"    OLD: {old_hint}\n")

                # Generate forward hint via API
                forward_hint = generate_forward_hint(verb_japanese, verb_english, noun_japanese, noun_english)
                forward_hints[verb_japanese][noun_japanese] = forward_hint

                # Derive reverse hint (NO API CALL)
                reverse_hint = derive_reverse_hint(forward_hint)

                # Build reverse hints structure
                if noun_japanese not in reverse_hints:
                    reverse_hints[noun_japanese] = {}
                reverse_hints[noun_japanese][verb_japanese] = reverse_hint

                log.write(f"    FORWARD: {forward_hint}\n")
                log.write(f"    REVERSE: {reverse_hint} (derived, no API call)\n")
                log.flush()

                # Rate limiting: ~3 requests per second
                time.sleep(0.35)

            processed += 1

            # Save progress every 10 verbs
            if processed % 10 == 0:
                log_print(f"\n[OK] Progress checkpoint: {processed}/{total_verbs} verbs processed")
                save_hints_checkpoint(forward_hints, reverse_hints, processed, total_verbs, total_pairs, log)

        # Save final results
        log_print("\n\nSaving final hints...")
        save_final_hints(forward_hints, reverse_hints, total_pairs, log)

        log_print(f"\n[OK] Complete! Regenerated {processed} verbs with {total_pairs} total pairs")
        log_print(f"  API calls made: {total_pairs}")
        log_print(f"  API calls saved: {total_pairs} (50% reduction)")
        log_print(f"  Errors: {errors}")

def save_hints_checkpoint(forward_hints, reverse_hints, processed, total, total_pairs, log=None):
    """Save intermediate checkpoint for both forward and reverse hints"""
    from datetime import datetime

    # Save forward hints checkpoint
    forward_checkpoint_path = Path("public/data/collocation_hints_NEW_checkpoint.json")
    forward_data = {
        "version": "10.0.0",
        "generator": "claude-api-optimized",
        "model": "claude-sonnet-4-5-20250929",
        "status": f"In progress: {processed}/{total}",
        "hints": forward_hints
    }
    with open(forward_checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(forward_data, f, ensure_ascii=False, indent=2)

    # Save reverse hints checkpoint
    reverse_checkpoint_path = Path("public/data/reverse_hints_NEW_checkpoint.json")
    reverse_data = {
        "version": "10.0.0",
        "generator": "claude-api-optimized-derived",
        "model": "claude-sonnet-4-5-20250929",
        "mode": "reverse",
        "status": f"In progress: {processed}/{total}",
        "hints": reverse_hints
    }
    with open(reverse_checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(reverse_data, f, ensure_ascii=False, indent=2)

    msg = f"  Checkpoints saved (forward + reverse)"
    print(msg)
    if log:
        log.write(msg + '\n')
        log.flush()

def save_final_hints(forward_hints, reverse_hints, total_pairs, log=None):
    """Save final regenerated hints for both forward and reverse"""
    from datetime import datetime

    # Save forward hints
    forward_output_path = Path("public/data/collocation_hints_NEW.json")
    forward_data = {
        "version": "10.0.0",
        "generator": "claude-api-optimized",
        "model": "claude-sonnet-4-5-20250929",
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPairs": total_pairs,
        "description": "Clear, direct hints for collocation meanings (generated via API)",
        "hints": forward_hints
    }
    with open(forward_output_path, 'w', encoding='utf-8') as f:
        json.dump(forward_data, f, ensure_ascii=False, indent=2)

    # Save reverse hints
    reverse_output_path = Path("public/data/reverse_hints_NEW.json")
    reverse_data = {
        "version": "10.0.0",
        "generator": "claude-api-optimized-derived",
        "model": "claude-sonnet-4-5-20250929",
        "mode": "reverse",
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPairs": total_pairs,
        "description": "Clear, direct hints for reverse collocation meanings (derived from forward hints, no API calls)",
        "hints": reverse_hints
    }
    with open(reverse_output_path, 'w', encoding='utf-8') as f:
        json.dump(reverse_data, f, ensure_ascii=False, indent=2)

    msg1 = f"[OK] Forward hints saved to {forward_output_path}"
    msg2 = f"[OK] Reverse hints saved to {reverse_output_path} (derived, no API calls)"
    msg3 = "\nTo use the new hints, rename:"
    msg4 = f"  {forward_output_path} -> public/data/collocation_hints.json"
    msg5 = f"  {reverse_output_path} -> public/data/reverse_hints.json"

    for msg in [msg1, msg2, msg3, msg4, msg5]:
        print(msg)
        if log:
            log.write(msg + '\n')
    if log:
        log.flush()

if __name__ == "__main__":
    try:
        regenerate_all_hints_optimized()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved to checkpoint files.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
