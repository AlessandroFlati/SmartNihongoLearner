# Collocation Hint Generation

This script generates contextual hints for collocation pairs to help learners in the "I'm Stuck" feature.

## Setup

1. **Set your Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

2. **Install required package:**
   ```bash
   pip install anthropic
   ```

## Running the Script

```bash
python data-preparation/raw/generate_collocation_hints.py
```

## Process

- **Batch Size**: 10 words per batch
- **Progress**: Saved after each word in `hints_checkpoint.json`
- **Output**: `data-preparation/input/collocation_hints.json`
- **Model**: Claude Sonnet 4

## How It Works

For each verb/adjective, the script:

1. Sends all noun collocations to Claude
2. Asks Claude to group them into semantic categories
3. Returns hints like:
   - "beverages" for 水, コーヒー, お茶
   - "reading materials" for 本, 雑誌
   - "entertainment media" for 映画, テレビ

4. Saves hints mapped to each noun

## Hint Format

```json
{
  "version": "1.0.0",
  "generated_date": "2025-11-11",
  "total_words": 390,
  "hints": {
    "のむ": {
      "水": "beverages",
      "コーヒー": "beverages",
      "薬": "medicine and health",
      "お酒": "alcoholic drinks"
    },
    "使う": {
      "パソコン": "electronic devices",
      "ペン": "writing tools",
      "箸": "eating utensils"
    }
  }
}
```

## Between Batches

The script will pause after each batch and ask:
```
Press Enter to continue to next batch, or 'q' to quit:
```

This allows you to:
- Monitor progress
- Stop and resume later
- Check quality of generated hints

## Resume from Checkpoint

If stopped, just run the script again. It will automatically resume from the last checkpoint.

## Estimated Time

- ~390 words to process (verbs + adjectives with collocations)
- ~10 seconds per word
- ~39 batches total
- **Total time: ~65 minutes** if run continuously

## Cost Estimate

- Model: Claude Sonnet 4
- ~500 tokens per request (input + output)
- ~390 requests
- **Estimated cost: ~$2-3 USD**
