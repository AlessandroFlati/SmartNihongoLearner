"""Test the new noun-specific hint generation prompt."""

import os
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path('../../.env'))
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

client = anthropic.Anthropic(api_key=API_KEY)

# Test cases
test_cases = [
    ("する", "suru", "to do", "仕事", "shigoto", "work; job"),
    ("食べる", "taberu", "to eat", "りんご", "ringo", "apple"),
    ("食べる", "taberu", "to eat", "パン", "pan", "bread"),
    ("買う", "kau", "to buy", "本", "hon", "book"),
    ("話す", "hanasu", "to speak", "英語", "eigo", "English language"),
]

for verb, v_read, v_eng, noun, n_read, n_eng in test_cases:
    prompt = f"""You are creating hints for Japanese vocabulary learning.

CONTEXT: The learner knows the verb "{verb}" ({v_eng}). They need to guess which NOUN pairs with it.

Your hint should describe the NOUN "{noun}" ({n_eng}) in a way that helps identify it.

CRITICAL RULES:
- DO NOT describe the verb action (avoid "things you eat", "items you buy", etc.)
- DO describe the NOUN itself (characteristics, cultural references, attributes)
- Be specific to THIS particular noun, not a category
- 2-8 words maximum
- Creative and memorable

GOOD EXAMPLES (verb is known, describing the noun):
- 食べる + りんご → "the forbidden fruit of Eden"
- 食べる + マンゴー → "tropical yellow stone fruit"
- 食べる + 梨 → "also a body shape descriptor"
- 買う + 本 → "bound pages of reading material"
- 話す + 英語 → "global lingua franca"

BAD EXAMPLES (these just describe the verb):
- "things you eat" ✗
- "items you purchase" ✗
- "languages you speak" ✗

Your hint for {noun} ({n_eng}) when paired with {verb}:"""

    print(f"\n{verb} + {noun}:")
    print(f"Noun meaning: {n_eng}")

    try:
        message = client.messages.create(
            model='claude-sonnet-4-5-20250929',
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )

        hint = message.content[0].text.strip().strip('"\'.,;:!?')
        print(f"Generated hint: '{hint}'")

    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("Test complete!")
