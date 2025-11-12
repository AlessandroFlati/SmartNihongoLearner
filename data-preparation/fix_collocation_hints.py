#!/usr/bin/env python3
"""
Fix quality issues in collocation hints.

This script systematically corrects collocation hints to ensure they are:
1. Semantic categories rather than literal translations
2. Correctly categorized based on verb-noun relationships
3. Specific and useful for learning
"""

import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def load_json_file(filepath: str) -> Dict:
    """Load JSON file and return parsed data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filepath: str, data: Dict) -> None:
    """Save data to JSON file with proper formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_noun_meanings(collocations_data: Dict) -> Dict[str, Dict[str, str]]:
    """
    Extract noun meanings from collocations_complete.json.

    Returns:
        Dictionary mapping verb -> noun -> meaning
    """
    meanings = defaultdict(dict)

    # Handle structure: {version, generatedAt, totalPairs, totalWords, words: {...}}
    words_data = collocations_data.get('words', {})

    for verb, verb_data in words_data.items():
        if not isinstance(verb_data, dict):
            continue

        matches = verb_data.get('matches', {})
        if not isinstance(matches, dict):
            continue

        nouns_list = matches.get('nouns', [])
        if not isinstance(nouns_list, list):
            continue

        for noun_data in nouns_list:
            if not isinstance(noun_data, dict):
                continue

            noun = noun_data.get('word', '')
            meaning = noun_data.get('english', '')
            if noun and meaning:
                meanings[verb][noun] = meaning

    return meanings


def is_translation_not_category(hint: str) -> bool:
    """
    Check if hint looks like a translation rather than semantic category.

    Heuristics:
    - Very short (1-2 words without "and")
    - Starts with article "a/an/the"
    - Contains specific numbers
    - All lowercase single word
    """
    hint_lower = hint.lower()

    # Starts with article (likely translation)
    if hint_lower.startswith(('a ', 'an ', 'the ')):
        return True

    # Single short word without "and" (likely translation)
    if ' and ' not in hint and len(hint.split()) <= 2:
        # Check if it's a noun rather than a category
        # Categories typically have plural or descriptive words
        words = hint.split()
        if len(words) == 1 and not hint_lower.endswith(('s', 'ies', 'ion', 'ness', 'ment')):
            return True

    return False


# Comprehensive mapping of known problematic hints to correct semantic categories
HINT_FIXES = {
    # Criminals and wrongdoers
    'pickpocket': 'criminals and wrongdoers',
    'thief': 'criminals and wrongdoers',
    'burglar': 'criminals and wrongdoers',
    'robber': 'criminals and wrongdoers',

    # Media and broadcasting
    'announcer': 'media and broadcasting professionals',
    'reporter': 'media and broadcasting professionals',
    'newscaster': 'media and broadcasting professionals',

    # Ages and life stages
    '20 years old': 'ages and life stages',
    'twenty years old': 'ages and life stages',
    'age': 'ages and life stages',

    # Time and temporal relations
    'behind': 'time after events',
    'after': 'time after events',
    'afterwards': 'time after events',
    'before': 'time before events',
    'previously': 'time before events',
    'next': 'sequential ordering',

    # Natural phenomena
    'typhoon': 'natural disasters and phenomena',
    'hurricane': 'natural disasters and phenomena',
    'earthquake': 'natural disasters and phenomena',
    'storm': 'natural disasters and phenomena',
    'heat': 'physical conditions',
    'fire': 'emergencies and hazards',

    # Fields and specializations
    'field of study': 'fields of specialization',
    'specialization': 'fields of specialization',
    'expertise': 'fields of specialization',
    'specialty': 'fields of specialization',

    # Positions and directions
    'above': 'relative positions',
    'below': 'relative positions',
    'top': 'relative positions',
    'bottom': 'relative positions',
    'side': 'sides and directions',
    'beside': 'beside and alongside',
    'next to': 'beside and alongside',
    'crossing': 'intersections and crossings',
    'circumference': 'surroundings and vicinity',

    # Food and dining
    'feast': 'feasts and treats',
    'treat': 'feasts and treats',
    'banquet': 'feasts and treats',

    # Surfaces and orientations
    'back': 'backs and undersides',
    'underside': 'backs and undersides',
    'reverse': 'backs and undersides',
    'surface': 'surfaces and fronts',
    'front': 'surfaces and fronts',
    'face': 'surfaces and fronts',

    # Furniture and fixtures
    'reception desk': 'furniture and fixtures',
    'shelf': 'furniture and fixtures',
    'shelves': 'furniture and fixtures',
    'stand': 'furniture and fixtures',
    'table': 'furniture and fixtures',
    'desk': 'furniture and fixtures',
    'drawer': 'storage and containers',
    'pocket': 'storage and containers',
    'closet': 'storage and containers',

    # Substitution and alternatives
    'substitute': 'alternatives and replacements',
    'both': 'quantity and totality',

    # Audio equipment
    'stereo': 'audio and entertainment devices',

    # Physical attributes
    'moustache': 'facial features',

    # Measurements
    'metre': 'units of measurement',
    'meter': 'units of measurement',
    'gram': 'units of measurement',

    # Postal and mail
    'mailbox': 'postal services and mail',
    'post': 'postal services and mail',
    'postbox': 'postal services and mail',

    # Weather and forecasts
    'weather forecast': 'weather and forecasts',
    'forecast': 'weather and forecasts',

    # Lost items
    'lost item': 'lost items',
    'forgotten item': 'lost items',
    'lost property': 'lost items',

    # Water and utilities
    'water supply': 'water sources and utilities',
    'running water': 'water sources and utilities',
    'hot water': 'water sources and utilities',
    'tap water': 'water sources and utilities',

    # Gifts and presents
    'gift': 'gifts and presents',
    'present': 'gifts and presents',

    # Entertainment
    'movie': 'entertainment and media',
    'film': 'entertainment and media',

    # Nature and sky
    'sky': 'natural scenery',
    'moon': 'celestial bodies',

    # Bathing
    'bath': 'bathing and hygiene',

    # Daily items and materials
    'soap': 'cleaning and hygiene products',
    'thread': 'sewing and textile materials',
    'miso': 'cooking ingredients',
    'umbrella': 'personal accessories',
    'glove': 'clothing and accessories',
    'underwear': 'clothing and accessories',
    'overcoat': 'clothing and accessories',

    # Food items
    'flesh': 'food and ingredients',
    'meat': 'food and ingredients',
    'foodstuff': 'food and ingredients',

    # Animals
    'pet': 'domestic animals',

    # Appliances
    'refrigerator': 'household appliances',
    'elevator': 'building facilities',

    # Stationery and office
    'calendar': 'stationery and scheduling tools',
    'fax': 'office equipment',

    # Tobacco and smoking
    'tobacco': 'tobacco and smoking',

    # Luggage
    'suitcase': 'luggage and travel items',

    # Small items
    'handkerchief': 'personal accessories',

    # Materials
    'silk': 'fabrics and materials',
    'gasoline': 'fuels and energy sources',

    # Reading materials
    'cartoon': 'reading and media',
    'hiragana': 'writing systems',
    'katakana': 'writing systems',
    'kanji': 'writing systems',

    # Rest and breaks
    'rest': 'breaks and rest periods',
    'noon': 'times of day',

    # Utilities and services
    'electricity': 'utilities and services',
    'cooling': 'climate control',

    # Musical instruments
    'piano': 'musical instruments',

    # Body parts
    'body': 'body and physique',

    # Personal items
    'purse': 'personal belongings',
    'wallet': 'personal belongings',

    # Signals and alerts
    'bell': 'signals and alerts',

    # Footwear
    'sandal': 'footwear and shoes',
    'slipper': 'footwear and shoes',

    # Seating
    'seat': 'seating and furniture',

    # Transportation facilities
    'escalator': 'building facilities',

    # Elements
    'air': 'air and atmosphere',

    # Bathing facilities
    'shower': 'bathing and hygiene',

    # Musical instruments (extended)
    'guitar': 'musical instruments',

    # People categories
    'foreigner': 'people by nationality',

    # Body parts (extended)
    'throat': 'body parts',
}


def fix_verb_specific_categories(verb: str, hint: str, noun: str) -> str:
    """
    Fix hints based on verb-noun relationship context.

    Args:
        verb: The verb (ある, いる, なる)
        hint: Current hint text
        noun: The noun being categorized

    Returns:
        Fixed hint category
    """
    hint_lower = hint.lower()

    # Fix ある (to exist/to have) misclassifications
    if verb == 'ある':
        # Use exact noun matching to avoid false positives
        if noun == '横':
            return 'beside and alongside'
        if noun == '裏':
            return 'backs and undersides'
        if noun in ['水道', '湯']:
            return 'water sources and utilities'
        if 'family' in hint_lower and noun in ['上', '下', '中']:
            return 'relative positions'
        if 'people' in hint_lower and noun == '側':
            return 'sides and directions'
        if 'people' in hint_lower and noun == 'ご馳走':
            return 'feasts and treats'
        if 'rest' in hint_lower and noun == '横':
            return 'beside and alongside'
        if 'ideas' in hint_lower and noun == '裏':
            return 'backs and undersides'
        if 'touch' in hint_lower and noun == '表':
            return 'surfaces and fronts'
        if 'stationery' in hint_lower and noun in ['受付', '棚', '台', 'テーブル']:
            return 'furniture and fixtures'
        if 'reading' in hint_lower and noun == 'ポスト':
            return 'postal services and mail'
        if 'reading' in hint_lower and noun == '天気予報':
            return 'weather and forecasts'
        if 'reading' in hint_lower and noun == '忘れ物':
            return 'lost items'
        if 'beverages' in hint_lower and noun in ['水道', '湯']:
            return 'water sources and utilities'
        if 'abilities' in hint_lower and noun == '贈り物':
            return 'gifts and presents'
        if 'places' in hint_lower and noun == '専門':
            return 'fields of specialization'

    # Fix いる (to be/to exist for animate) misclassifications
    if verb == 'いる':
        # Break down generic "people" into more specific categories
        if hint_lower == 'people':
            # Need more context - this should be analyzed with noun meaning
            if noun in ['子供', '子', '赤ちゃん', '赤ん坊', 'お子さん', '赤ちゃん']:
                return 'children and young people'
            elif noun in ['両親', '親', '父', '母', '兄', '弟', '姉', '妹', '家族', '息子', '娘']:
                return 'family members'
            elif noun in ['友達', '友人', '仲間', '知人']:
                return 'friends and acquaintances'
            elif noun in ['先生', '医者', '看護師', '社長', '店員', '警察', '教師']:
                return 'professionals and workers'
            elif noun in ['すり', '泥棒', '犯人']:
                return 'criminals and suspects'
            elif noun in ['客', 'お客', 'お客さん', 'お客様']:
                return 'guests and customers'
            elif noun in ['学生', '生徒', '大学生']:
                return 'students and learners'
            elif noun in ['男', '女', '男の子', '女の子']:
                return 'people by gender'
            elif noun in ['一人', '二人', '三人', '大勢', 'みんな']:
                return 'people by quantity'

    # Handle generic "people" hints for other verbs where it's appropriate
    # For many verbs, "people" is actually correct (e.g., 来る + 人, 死ぬ + 人, etc.)
    # Only refine when we have specific nouns that need subcategorization
    if hint_lower == 'people':
        if noun in ['子供', '子', '赤ちゃん', '赤ん坊', 'お子さん']:
            return 'children and young people'
        elif noun in ['弟', '兄', '姉', '妹', '両親', '親', '父', '母', '家族', '息子', '娘']:
            return 'family members'
        elif noun in ['大勢', 'みんな', '何人']:
            return 'people by quantity'

    # Fix なる (to become) misclassifications
    if verb == 'なる':
        # Specific mappings for なる
        if noun in ['大人', 'お金持ち']:
            return 'social and economic statuses'
        if hint_lower == 'people':
            if noun in ['大人', 'お金持ち']:
                return 'social and economic statuses'
            elif noun in ['先生', '校長', '医者', '看護婦', '部長', '公務員', '課長']:
                return 'professional roles and careers'
            elif noun in ['友達', '留学生']:
                return 'social relationships'
        if hint_lower in ['announcer', 'reporter'] or 'announcer' in hint_lower:
            return 'media and broadcasting careers'
        if '20' in hint or 'twenty' in hint_lower or ('age' in hint_lower and noun == '二十歳'):
            return 'ages and life stages'
        if 'places' in hint_lower and noun == '一番':
            return 'rankings and positions'

    return hint


def apply_known_fixes(hint: str) -> str:
    """Apply known hint fixes from the mapping."""
    hint_lower = hint.lower()

    # Direct match
    if hint_lower in HINT_FIXES:
        return HINT_FIXES[hint_lower]

    # Partial matches
    for wrong, correct in HINT_FIXES.items():
        if wrong in hint_lower:
            return correct

    return hint


def fix_collocation_hints(
    hints_data: Dict,
    meanings_data: Dict
) -> Tuple[Dict, Dict[str, int]]:
    """
    Fix all quality issues in collocation hints.

    Args:
        hints_data: The collocation_hints_refined.json data
        meanings_data: The collocations_complete.json data

    Returns:
        Tuple of (fixed_data, stats_dict)
    """
    stats = defaultdict(int)
    noun_meanings = get_noun_meanings(meanings_data)

    # Handle structure: {version, generated_date, refined, total_words, total_nouns_with_hints, hints: {...}}
    hints_dict = hints_data.get('hints', {})

    for verb, noun_to_hint in hints_dict.items():
        if not isinstance(noun_to_hint, dict):
            continue

        for noun, original_hint in noun_to_hint.items():
            if not isinstance(original_hint, str) or not original_hint:
                continue

            # Track original for comparison
            modified = False
            new_hint = original_hint

            # Step 1: Apply known fixes from mapping
            fixed_hint = apply_known_fixes(original_hint)
            if fixed_hint != original_hint:
                new_hint = fixed_hint
                modified = True
                stats['known_fixes'] += 1

            # Step 2: Check if it's a translation rather than category
            if is_translation_not_category(new_hint):
                stats['translations_found'] += 1

            # Step 3: Apply verb-specific fixes
            verb_specific = fix_verb_specific_categories(verb, new_hint, noun)
            if verb_specific != new_hint:
                new_hint = verb_specific
                modified = True
                stats['verb_specific_fixes'] += 1

            # Step 4: Generic "people" category refinement
            if new_hint.lower() == 'people' and verb == 'いる':
                specific = fix_verb_specific_categories(verb, new_hint, noun)
                if specific != new_hint:
                    new_hint = specific
                    modified = True
                    stats['people_refined'] += 1

            # Update if modified
            if modified:
                noun_to_hint[noun] = new_hint
                stats['total_fixes'] += 1

    return hints_data, dict(stats)


def main():
    """Main execution function."""
    print("Loading collocation files...")

    hints_file = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocation_hints_refined.json'
    complete_file = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json'

    hints_data = load_json_file(hints_file)
    meanings_data = load_json_file(complete_file)

    hints_dict = hints_data.get('hints', {})
    words_dict = meanings_data.get('words', {})

    print(f"Loaded {len(hints_dict)} verbs from hints file")
    print(f"Loaded {len(words_dict)} verbs from complete file")

    print("\nFixing collocation hints...")
    fixed_data, stats = fix_collocation_hints(hints_data, meanings_data)

    print("\nSaving fixed data...")
    save_json_file(hints_file, fixed_data)

    print("\n" + "="*60)
    print("FIX SUMMARY")
    print("="*60)
    print(f"Total fixes applied: {stats.get('total_fixes', 0)}")
    print(f"Known fixes from mapping: {stats.get('known_fixes', 0)}")
    print(f"Verb-specific fixes: {stats.get('verb_specific_fixes', 0)}")
    print(f"'People' category refined: {stats.get('people_refined', 0)}")
    print(f"Translations detected: {stats.get('translations_found', 0)}")
    print("="*60)

    print("\nFixed file saved successfully!")


if __name__ == '__main__':
    main()
