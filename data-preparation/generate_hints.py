#!/usr/bin/env python3
"""
Generate semantic hints for Japanese collocation pairs.
This script reads collocations_complete.json and generates contextual hints
for each verb/adjective based on their noun matches.
"""

import json
from datetime import datetime
from collections import defaultdict

# Semantic categories mapping based on English meanings
SEMANTIC_CATEGORIES = {
    # Beverages
    'beverages': ['water', 'coffee', 'tea', 'milk', 'juice', 'beer', 'wine', 'sake', 'drink', 'beverage'],

    # Reading materials
    'reading materials': ['book', 'magazine', 'newspaper', 'novel', 'text', 'document', 'article', 'letter', 'mail'],

    # Communication
    'communication': ['talk', 'speech', 'conversation', 'chat', 'question', 'answer', 'inquiry', 'enquiry',
                     'explanation', 'story', 'telephone', 'phone', 'call', 'email', 'message', 'discussion'],

    # Work and study
    'work and study': ['work', 'job', 'study', 'homework', 'research', 'labor', 'labour', 'task',
                       'assignment', 'project', 'report'],

    # Daily activities
    'daily activities': ['shopping', 'cooking', 'cleaning', 'laundry', 'preparation', 'errand'],

    # Exercise and training
    'exercise and training': ['exercise', 'training', 'practice', 'sports', 'workout', 'athletics'],

    # Clothing items
    'clothing items': ['clothes', 'shirt', 'shoes', 'pants', 'dress', 'coat', 'jacket', 'hat',
                      'socks', 'underwear', 'uniform', 'suit', 'tie', 'skirt'],

    # Food items
    'food items': ['bread', 'rice', 'meat', 'fish', 'vegetable', 'fruit', 'egg', 'food', 'meal',
                   'breakfast', 'lunch', 'dinner', 'snack'],

    # School subjects
    'school subjects': ['mathematics', 'math', 'history', 'science', 'english', 'japanese',
                       'geography', 'physics', 'chemistry', 'biology', 'subject'],

    # Transportation
    'transportation': ['car', 'bus', 'train', 'bicycle', 'bike', 'taxi', 'airplane', 'vehicle',
                      'subway', 'metro'],

    # Body parts
    'body parts': ['hand', 'head', 'foot', 'eye', 'ear', 'mouth', 'nose', 'hair', 'face',
                  'body', 'arm', 'leg', 'finger', 'tooth', 'teeth'],

    # Time expressions
    'time periods': ['morning', 'afternoon', 'evening', 'night', 'day', 'week', 'month', 'year',
                    'time', 'hour', 'minute', 'today', 'tomorrow', 'yesterday'],

    # Places
    'places': ['school', 'university', 'college', 'hospital', 'store', 'shop', 'restaurant',
              'library', 'park', 'station', 'office', 'building', 'house', 'home', 'room',
              'place', 'location', 'area'],

    # Entertainment
    'entertainment': ['movie', 'film', 'music', 'song', 'game', 'video', 'television', 'tv',
                     'radio', 'concert', 'show', 'performance'],

    # People and relationships
    'people and relationships': ['friend', 'teacher', 'student', 'family', 'parent', 'child',
                                'person', 'people', 'mother', 'father', 'brother', 'sister',
                                'colleague', 'classmate', 'neighbor', 'customer'],

    # Weather and nature
    'weather and nature': ['rain', 'snow', 'wind', 'weather', 'temperature', 'season', 'spring',
                          'summer', 'autumn', 'fall', 'winter', 'cloud', 'sun', 'sky'],

    # Emotions and feelings
    'emotions and feelings': ['feeling', 'emotion', 'happiness', 'sadness', 'anger', 'fear',
                             'worry', 'stress', 'joy', 'pleasure', 'pain'],

    # Money and finance
    'money and finance': ['money', 'yen', 'dollar', 'price', 'cost', 'salary', 'wage', 'payment',
                         'budget', 'expense', 'income'],

    # Information and knowledge
    'information and knowledge': ['information', 'knowledge', 'fact', 'data', 'news', 'opinion',
                                 'idea', 'thought', 'plan', 'schedule'],

    # Actions and events
    'actions and events': ['meeting', 'party', 'event', 'ceremony', 'festival', 'celebration',
                          'trip', 'travel', 'journey', 'vacation', 'holiday'],

    # Objects and tools
    'objects and tools': ['pen', 'pencil', 'paper', 'desk', 'chair', 'table', 'computer',
                         'smartphone', 'phone', 'bag', 'umbrella', 'key', 'watch', 'clock',
                         'camera', 'tool', 'equipment'],

    # Actions (verbs as nouns)
    'activities': ['activity', 'action', 'movement', 'motion'],

    # Medical and health
    'medical and health': ['medicine', 'hospital', 'doctor', 'illness', 'disease', 'injury',
                          'treatment', 'health', 'sick', 'pain', 'symptom'],

    # Abstract concepts
    'abstract concepts': ['thing', 'matter', 'situation', 'condition', 'state', 'problem',
                         'issue', 'difficulty', 'trouble', 'reason', 'cause', 'result',
                         'effect', 'purpose', 'goal', 'dream', 'hope', 'wish'],
}


def categorize_noun(english_meaning):
    """
    Categorize a noun based on its English meaning.
    Returns the most appropriate category or 'general' if no match.
    """
    if not english_meaning:
        return 'general'

    # Convert to lowercase for matching
    meaning_lower = english_meaning.lower()

    # Check each category
    for category, keywords in SEMANTIC_CATEGORIES.items():
        for keyword in keywords:
            if keyword in meaning_lower:
                return category

    return 'general'


def generate_hints(input_file, output_file):
    """
    Read collocations data and generate semantic hints.
    """
    print(f"Reading input file: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    hints = {}
    total_words = 0
    total_nouns_with_hints = 0

    # Process each word (verb/adjective)
    for word_key, word_data in data['words'].items():
        word_type = word_data.get('type', '')

        # Only process verbs and adjectives
        if word_type not in ['verb', 'adjective']:
            continue

        # Check if this word has noun matches
        matches = word_data.get('matches', {})
        nouns = matches.get('nouns', [])

        if not nouns:
            continue

        total_words += 1
        word_hints = {}

        # Categorize each noun and assign hints
        for noun in nouns:
            noun_word = noun['word']
            noun_english = noun.get('english', '')

            # Get category for this noun
            category = categorize_noun(noun_english)
            word_hints[noun_word] = category
            total_nouns_with_hints += 1

        hints[word_key] = word_hints

    # Create output structure
    output = {
        "version": "1.0.0",
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "total_words": total_words,
        "total_nouns_with_hints": total_nouns_with_hints,
        "hints": hints
    }

    # Write output file
    print(f"Writing output file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nGeneration complete!")
    print(f"Total verbs/adjectives processed: {total_words}")
    print(f"Total nouns with hints: {total_nouns_with_hints}")

    # Print some statistics
    category_counts = defaultdict(int)
    for word_hints in hints.values():
        for hint in word_hints.values():
            category_counts[hint] += 1

    print(f"\nHint categories used:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")


if __name__ == '__main__':
    input_file = 'C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocations_complete.json'
    output_file = 'C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocation_hints.json'

    generate_hints(input_file, output_file)
