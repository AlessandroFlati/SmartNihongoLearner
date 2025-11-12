"""
Generate Reverse Collocation Hints using Claude API

This script generates hints for reverse game modes (noun → verb/adjective).
When the learner knows the NOUN and needs to guess the VERB/ADJECTIVE.

Example hints:
- 水 + のむ → "action with liquids using your mouth"
- お金 + 盗む → "criminal action to obtain it"
- 仕事 + する → "action of performing work"
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
VOCAB_FILE = Path('../input/vocabulary.json')
OUTPUT_FILE = Path('../output/reverse_hints.json')
CHECKPOINT_FILE = Path('../output/reverse_hints_checkpoint.json')
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# API settings
MODEL = 'claude-sonnet-4-5-20250929'  # Claude Sonnet 4.5
MAX_TOKENS = 100
BATCH_SIZE = 50  # Save checkpoint every 50 pairs
RATE_LIMIT_DELAY = 0.5  # 500ms between requests

def load_collocations():
    """Load collocation data from JSON file."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['words']

def load_vocabulary():
    """Load vocabulary data from JSON file."""
    with open(VOCAB_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Create a dictionary keyed by japanese word
    vocab_dict = {}
    for entry in data['vocabulary']:
        vocab_dict[entry['japanese']] = entry
    return vocab_dict

def build_reverse_index(collocations, vocabulary):
    """
    Build reverse index: noun → list of (verb/adjective, score)
    """
    reverse_index = {}

    for word, word_data in collocations.items():
        word_type = word_data.get('type')
        if word_type not in ['verb', 'adjective']:
            continue

        matches = word_data.get('matches', {}).get('nouns', [])

        for match in matches:
            noun = match['word']
            score = match.get('score', 0)

            if noun not in reverse_index:
                # Get noun data from vocabulary
                noun_vocab = vocabulary.get(noun, {})
                reverse_index[noun] = {
                    'reading': noun_vocab.get('reading', ''),
                    'english': noun_vocab.get('english', ''),
                    'verbs': [],
                    'adjectives': []
                }

            match_type = 'verbs' if word_type == 'verb' else 'adjectives'
            reverse_index[noun][match_type].append({
                'word': word,
                'reading': word_data.get('reading', ''),
                'english': word_data.get('english', ''),
                'score': score
            })

    # Sort by score (descending)
    for noun_data in reverse_index.values():
        noun_data['verbs'].sort(key=lambda x: x['score'], reverse=True)
        noun_data['adjectives'].sort(key=lambda x: x['score'], reverse=True)

    return reverse_index

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
    print(f"Checkpoint saved: {len(hints)} nouns processed")

def generate_hint_prompt(noun_data, verb_adj_data, word_type):
    """
    Generate a prompt for Claude to create a VERB/ADJECTIVE-SPECIFIC hint.

    The noun is KNOWN, the verb/adjective is the TARGET to guess.
    The hint describes characteristics of the VERB/ADJECTIVE action/quality.
    """
    noun = noun_data['word']
    noun_reading = noun_data['reading']
    noun_english = noun_data['english']

    target = verb_adj_data['word']
    target_reading = verb_adj_data['reading']
    target_english = verb_adj_data['english']

    target_name = "verb" if word_type == 'verb' else 'adjective'

    return f"""You are creating hints for Japanese vocabulary learning.

CONTEXT: The learner knows the noun "{noun}" ({noun_english}). They need to guess which {target_name.upper()} pairs with it.

Your hint should describe the {target_name.upper()} "{target}" ({target_english}) AND hint at the nuanced meaning of this collocation.

CRITICAL RULES:
- DO describe the {target_name} action/quality with characteristics specific to this collocation
- Remember: Japanese collocations often have nuanced meanings
- Include what makes this {target_name} specifically relevant to this noun
- 2-8 words maximum
- Creative and memorable

GOOD EXAMPLES FOR VERBS (describing action + collocation nuance):
- 水 + のむ → "liquid consumption action"
- お金 + 盗む → "illicit taking action"
- 電話 + する → "communication action with device"
- 仕事 + する → "performing employment duties"
- 本 + 読む → "processing written text"

GOOD EXAMPLES FOR ADJECTIVES (describing quality + collocation nuance):
- 部屋 + 広い → "having spacious dimensions"
- 値段 + 高い → "costly in monetary terms"
- 人 + 優しい → "showing kindness character"

BAD EXAMPLES (too generic):
- "action you do" ✗
- "quality it has" ✗
- "something related" ✗

Now create a hint for:
Noun: {noun} ({noun_reading}) - {noun_english}
{target_name.capitalize()}: {target} ({target_reading}) - {target_english}

Provide ONLY the hint phrase (2-8 words), nothing else."""

def generate_hint_with_claude(client, noun_data, verb_adj_data, word_type):
    """Generate a single hint using Claude API."""
    prompt = generate_hint_prompt(noun_data, verb_adj_data, word_type)

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        hint = message.content[0].text.strip()

        # Remove quotes if present
        hint = hint.strip('"').strip("'")

        return hint

    except Exception as e:
        print(f"Error generating hint: {e}")
        return f"{word_type} related to {noun_data['english']}"

def main():
    if not API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return

    print("Loading collocation data...")
    collocations = load_collocations()

    print("Loading vocabulary data...")
    vocabulary = load_vocabulary()

    print("Building reverse index...")
    reverse_index = build_reverse_index(collocations, vocabulary)

    print(f"Found {len(reverse_index)} nouns with reverse collocations")

    # Load existing checkpoint
    hints = load_checkpoint()
    print(f"Loaded checkpoint: {len(hints)} nouns already processed")

    # Initialize Claude client
    client = anthropic.Anthropic(api_key=API_KEY)

    # Generate hints for each noun
    total_nouns = len(reverse_index)
    processed = len(hints)

    for idx, (noun, noun_data) in enumerate(reverse_index.items(), 1):
        if noun in hints:
            continue

        print(f"\n[{idx}/{total_nouns}] Processing noun: {noun}")

        hints[noun] = {}

        # Process verbs
        for verb_data in noun_data['verbs']:
            verb = verb_data['word']
            print(f"  Generating hint for verb: {verb}")

            hint = generate_hint_with_claude(client, {
                'word': noun,
                'reading': noun_data['reading'],
                'english': noun_data['english']
            }, verb_data, 'verb')

            hints[noun][verb] = hint
            time.sleep(RATE_LIMIT_DELAY)

        # Process adjectives
        for adj_data in noun_data['adjectives']:
            adj = adj_data['word']
            print(f"  Generating hint for adjective: {adj}")

            hint = generate_hint_with_claude(client, {
                'word': noun,
                'reading': noun_data['reading'],
                'english': noun_data['english']
            }, adj_data, 'adjective')

            hints[noun][adj] = hint
            time.sleep(RATE_LIMIT_DELAY)

        processed += 1

        # Save checkpoint periodically
        if processed % BATCH_SIZE == 0:
            save_checkpoint(hints)

    # Save final output
    output_data = {
        'version': '1.0.0',
        'generated_date': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'mode': 'reverse',  # noun → verb/adjective
        'hints': hints
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Complete! Generated hints for {len(hints)} nouns")
    print(f"Output saved to: {OUTPUT_FILE}")

    # Clean up checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
        print("Checkpoint file removed")

if __name__ == '__main__':
    main()
