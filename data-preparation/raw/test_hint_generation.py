"""Test a single hint generation to see what error occurs."""

import os
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path('../../.env'))
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

client = anthropic.Anthropic(api_key=API_KEY)

# Test data
verb_data = {
    'word': 'する',
    'reading': 'suru',
    'english': 'to do; to carry out; to perform'
}

noun_data = {
    'word': '仕事',
    'reading': 'shigoto',
    'english': 'work; job',
}

prompt = f"""You are helping Japanese learners understand natural collocations (word pairings).

Given this verb-noun collocation pair:
- Verb: {verb_data['word']} ({verb_data['reading']}) = {verb_data['english']}
- Noun: {noun_data['word']} ({noun_data['reading']}) = {noun_data['english']}

Generate a SHORT, conversational hint (2-5 words) that describes this specific relationship.

Examples of good hints:
- のむ + 水 → "things you drink"
- 盗む + お金 → "things that can be stolen"
- する + 仕事 → "activities you perform"

The hint should:
1. Be specific to THIS verb-noun pair (not generic)
2. Use natural, conversational English
3. Be 2-5 words maximum
4. Help learners understand why this verb and noun go together

Your hint (2-5 words only, no explanation):"""

print("Testing hint generation...")
print(f"Verb: {verb_data['word']} ({verb_data['reading']})")
print(f"Noun: {noun_data['word']} ({noun_data['reading']})")
print()

try:
    message = client.messages.create(
        model='claude-3-opus-20240229',
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

    hint = message.content[0].text.strip()
    hint = hint.strip('"\'.,;:!?')

    print(f"SUCCESS!")
    print(f"Generated hint: '{hint}'")
    print()
    print(f"Full response:")
    print(message.content[0].text)

except Exception as e:
    print(f"ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
