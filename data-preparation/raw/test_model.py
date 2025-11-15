"""Test which Claude models are available with the current API key."""

import os
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path('../../.env'))
API_KEY = os.environ.get('ANTHROPIC_API_KEY')

if not API_KEY:
    print("ERROR: API key not found!")
    exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

# List of models to test
models_to_test = [
    'claude-sonnet-4-5-20250929',  # Sonnet 4.5 (latest)
    'claude-3-5-sonnet-20241022',
    'claude-3-5-sonnet-20240620',
    'claude-3-sonnet-20240229',
    'claude-3-opus-20240229',
    'claude-3-haiku-20240307',
]

print("Testing Claude models...")
print("=" * 60)

for model in models_to_test:
    try:
        print(f"\nTesting: {model}")
        message = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✓ SUCCESS: {model} is available!")
        print(f"  Response: {message.content[0].text}")
        break  # Found a working model
    except Exception as e:
        print(f"✗ FAILED: {str(e)[:100]}")

print("\n" + "=" * 60)
