#!/usr/bin/env python3
"""
Comprehensive hint quality fixer with detailed semantic analysis.
Eliminates ALL generic hints and creates specific, meaningful categories.
"""

import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Comprehensive verb-specific categorization rules
VERB_CATEGORIES = {
    'する': {
        'professional activities': ['work', 'job', 'business', 'research', 'study', 'part-time'],
        'daily routines': ['shopping', 'cleaning', 'laundry', 'cooking', 'housework'],
        'sports and exercise': ['exercise', 'sport', 'training', 'swim', 'judo', 'tennis', 'match'],
        'communication activities': ['talk', 'speech', 'conversation', 'contact', 'greeting', 'chat'],
        'planning tasks': ['plan', 'preparation', 'reservation', 'arrangement', 'preview', 'review'],
        'major life events': ['marriage', 'graduation', 'enrollment', 'admission', 'birth'],
        'business operations': ['import', 'export', 'trade', 'production', 'broadcast'],
        'social interactions': ['introduction', 'invitation', 'consultation', 'care'],
        'leisure activities': ['travel', 'tour', 'sightseeing', 'flower viewing'],
        'helpful services': ['translation', 'guidance', 'help', 'assistance'],
        'problems encountered': ['failure', 'mistake', 'quarrel', 'trouble', 'breakdown', 'fight'],
        'medical procedures': ['injection', 'hospitalization', 'discharge', 'surgery'],
        'study activities': ['review', 'practice', 'check', 'drill', 'preparation'],
        'competitive events': ['competition', 'match', 'game', 'contest', 'exam', 'test'],
        'mental processes': ['worry', 'relief', 'attention', 'care', 'peace of mind'],
        'formal actions': ['bow', 'thanks', 'excuse', 'rudeness', 'celebration'],
        'daily activities': ['walk', 'departure', 'attendance', 'opposition', 'sleep'],
    },
    '買う': {
        'clothing items': ['clothes', 'shirt', 'shoe', 'hat', 'coat', 'jacket', 'underwear', 'socks', 'gloves', 'sweater', 'suit', 'dress'],
        'food and groceries': ['vegetable', 'meat', 'fish', 'egg', 'bread', 'milk', 'rice', 'food', 'butter', 'jam'],
        'reading materials': ['book', 'magazine', 'newspaper', 'dictionary', 'notebook', 'map'],
        'expensive purchases': ['car', 'house', 'land', 'apartment', 'automobile', 'refrigerator'],
        'gifts and souvenirs': ['present', 'gift', 'souvenir', 'flower', 'doll', 'toy'],
        'tickets and passes': ['ticket', 'pass', 'postcard', 'stamp'],
        'personal care': ['medicine', 'cosmetic', 'soap', 'cigarette', 'tobacco'],
        'electronic devices': ['computer', 'camera', 'television', 'tape', 'film', 'record', 'fax'],
        'household items': ['furniture', 'dish', 'cup', 'bowl', 'knife', 'fork', 'spoon', 'stove'],
        'stationery items': ['pen', 'pencil', 'notebook', 'paper', 'envelope', 'calendar'],
        'beverages': ['alcohol', 'beer', 'wine', 'sake', 'tea', 'coffee'],
        'accessories': ['ring', 'watch', 'accessory', 'bag', 'suitcase', 'handkerchief'],
        'pet supplies': ['pet', 'animal'],
        'fabric materials': ['silk', 'thread', 'cloth'],
    },
    '来る': {
        'people arriving': ['person', 'friend', 'guest', 'visitor', 'customer', 'student'],
        'family visits': ['mother', 'father', 'parent', 'brother', 'sister', 'son', 'daughter', 'uncle', 'aunt'],
        'seasonal arrivals': ['season', 'spring', 'summer', 'autumn', 'winter', 'fall'],
        'time periods': ['tomorrow', 'today', 'week', 'month', 'year', 'morning', 'evening'],
        'scheduled events': ['birthday', 'exam', 'meeting', 'party', 'festival'],
        'arriving messages': ['letter', 'mail', 'email', 'message', 'call', 'phone'],
        'transport arrivals': ['bus', 'train', 'taxi', 'car', 'airplane', 'ship'],
        'weather arrivals': ['rain', 'snow', 'typhoon', 'storm', 'wind'],
        'officials arriving': ['police', 'doctor', 'teacher', 'official'],
        'time references': ['next', 'after', 'later', 'soon'],
    },
    'ある': {
        'abstract concepts': ['thing', 'matter', 'problem', 'reason', 'cause', 'way', 'meaning'],
        'nearby facilities': ['store', 'shop', 'bank', 'station', 'hospital', 'school', 'park'],
        'building features': ['house', 'room', 'entrance', 'window', 'door', 'floor', 'wall'],
        'available time': ['time', 'leisure', 'spare', 'margin', 'free time', 'break'],
        'financial resources': ['money', 'budget', 'fund', 'capital'],
        'opportunities present': ['chance', 'opportunity', 'possibility'],
        'scheduled events': ['meeting', 'party', 'class', 'lesson', 'appointment'],
        'physical objects': ['desk', 'chair', 'table', 'book', 'pen'],
        'existing plans': ['plan', 'schedule', 'appointment', 'arrangement'],
        'possessed qualities': ['experience', 'knowledge', 'skill', 'interest', 'confidence'],
        'relationships present': ['relation', 'connection', 'relationship', 'tie'],
        'emotional states': ['interest', 'confidence', 'hope', 'enjoyment'],
        'available documents': ['document', 'paper', 'report', 'file'],
        'established rules': ['rule', 'law', 'regulation', 'custom'],
        'locations': ['place', 'spot', 'position', 'side', 'direction'],
    },
    '行く': {
        'educational places': ['school', 'university', 'class', 'library', 'college'],
        'work destinations': ['company', 'office', 'work', 'factory', 'shop'],
        'shopping venues': ['store', 'shop', 'restaurant', 'market', 'department store'],
        'leisure spots': ['park', 'beach', 'mountain', 'sea', 'cinema', 'pool'],
        'travel locations': ['country', 'city', 'town', 'abroad', 'overseas'],
        'public services': ['hospital', 'bank', 'post', 'station', 'airport'],
        'social events': ['party', 'meeting', 'wedding', 'funeral', 'ceremony'],
        'home destinations': ['home', 'house', 'room', 'apartment'],
        'directional movement': ['outside', 'inside', 'upstairs', 'downstairs'],
    },
    '見る': {
        'visual media': ['television', 'movie', 'film', 'video', 'news', 'program'],
        'reading materials': ['book', 'newspaper', 'magazine', 'map', 'menu'],
        'natural views': ['sky', 'star', 'moon', 'mountain', 'sea', 'scenery'],
        'people observed': ['face', 'person', 'child', 'friend', 'baby'],
        'visual artwork': ['picture', 'photo', 'painting', 'art', 'exhibition'],
        'documents checked': ['document', 'paper', 'letter', 'email', 'report'],
        'dreams and visions': ['dream', 'future', 'vision'],
        'performances': ['play', 'show', 'concert', 'dance'],
    },
    '読む': {
        'books to read': ['book', 'novel', 'story', 'tale'],
        'news sources': ['newspaper', 'news', 'article', 'report'],
        'periodicals': ['magazine', 'journal', 'review'],
        'correspondence': ['letter', 'email', 'message', 'card'],
        'reference books': ['dictionary', 'encyclopedia', 'textbook'],
        'academic texts': ['paper', 'thesis', 'dissertation', 'essay'],
        'instructions': ['manual', 'guide', 'directions'],
    },
    '書く': {
        'correspondence': ['letter', 'email', 'message', 'card', 'postcard'],
        'academic writing': ['paper', 'report', 'essay', 'thesis', 'assignment'],
        'creative works': ['story', 'novel', 'poem', 'diary', 'journal'],
        'official forms': ['application', 'resume', 'form', 'document'],
        'quick notes': ['note', 'memo', 'list', 'reminder'],
        'text elements': ['character', 'kanji', 'word', 'name', 'address'],
    },
    '話す': {
        'languages spoken': ['japanese', 'english', 'language', 'chinese', 'french'],
        'discussion topics': ['story', 'news', 'topic', 'matter', 'subject'],
        'personal sharing': ['secret', 'truth', 'lie', 'opinion', 'feeling'],
        'verbal elements': ['word', 'phrase', 'sentence', 'expression'],
    },
    '聞く': {
        'audio content': ['music', 'song', 'radio', 'cd', 'concert'],
        'news and info': ['news', 'story', 'rumor', 'information', 'report'],
        'audible sounds': ['sound', 'voice', 'noise', 'bell'],
        'spoken words': ['talk', 'speech', 'lecture', 'explanation', 'conversation'],
        'requests heard': ['question', 'request', 'opinion', 'advice', 'suggestion'],
    },
    '食べる': {
        'main meals': ['breakfast', 'lunch', 'dinner', 'meal', 'supper'],
        'staple foods': ['rice', 'bread', 'noodle', 'pasta', 'soup'],
        'protein sources': ['meat', 'fish', 'egg', 'chicken', 'beef', 'pork'],
        'produce items': ['vegetable', 'fruit', 'salad', 'apple', 'orange'],
        'sweet treats': ['snack', 'candy', 'cake', 'chocolate', 'ice cream'],
        'Japanese dishes': ['sushi', 'tempura', 'ramen', 'udon', 'soba'],
    },
    '飲む': {
        'hot drinks': ['coffee', 'tea', 'cocoa', 'green tea'],
        'cold drinks': ['water', 'juice', 'soda', 'cola', 'milk'],
        'alcoholic drinks': ['alcohol', 'beer', 'wine', 'sake', 'whiskey'],
        'medicine liquids': ['medicine', 'syrup', 'supplement'],
    },
    '作る': {
        'meals prepared': ['food', 'dish', 'meal', 'cooking', 'cuisine'],
        'items created': ['product', 'machine', 'device', 'toy', 'furniture'],
        'plans drafted': ['document', 'plan', 'schedule', 'list', 'report'],
        'bonds formed': ['friend', 'relationship', 'connection', 'partnership'],
        'groups established': ['company', 'group', 'team', 'club', 'organization'],
        'art produced': ['art', 'music', 'song', 'poem', 'painting'],
    },
    '使う': {
        'tools employed': ['tool', 'pen', 'pencil', 'scissors', 'knife'],
        'tech utilized': ['computer', 'phone', 'internet', 'app', 'software'],
        'resources spent': ['money', 'time', 'energy', 'effort'],
        'words applied': ['word', 'language', 'expression', 'phrase'],
        'vehicles used': ['car', 'train', 'bus', 'bicycle', 'taxi'],
        'rooms accessed': ['room', 'bathroom', 'kitchen', 'toilet'],
    },
    '持つ': {
        'items carried': ['bag', 'umbrella', 'key', 'wallet', 'purse'],
        'documents held': ['passport', 'license', 'ticket', 'card', 'visa'],
        'qualities possessed': ['interest', 'opinion', 'confidence', 'dream', 'hope'],
        'duties borne': ['responsibility', 'job', 'duty', 'role'],
        'relations kept': ['child', 'family', 'friend', 'pet'],
    },
    '知る': {
        'people known': ['person', 'friend', 'teacher', 'neighbor'],
        'facts learned': ['fact', 'truth', 'news', 'information', 'detail'],
        'places familiar': ['place', 'address', 'location', 'area'],
        'methods understood': ['method', 'way', 'rule', 'technique'],
        'secrets discovered': ['secret', 'reason', 'cause', 'mystery'],
    },
    '思う': {
        'thoughts held': ['opinion', 'idea', 'belief', 'view', 'thought'],
    },
    '言う': {
        'words expressed': ['word', 'phrase', 'sentence', 'expression'],
        'info stated': ['name', 'address', 'number', 'date'],
        'views voiced': ['opinion', 'idea', 'thought', 'belief'],
        'courtesy phrases': ['greeting', 'thanks', 'apology', 'excuse'],
    },
    '出る': {
        'places exited': ['house', 'home', 'room', 'building', 'office'],
        'events attended': ['meeting', 'party', 'competition', 'contest', 'conference'],
        'results appearing': ['result', 'answer', 'conclusion', 'outcome'],
        'items released': ['book', 'magazine', 'newspaper', 'album'],
    },
    '入る': {
        'spaces entered': ['room', 'building', 'store', 'restaurant', 'house'],
        'groups joined': ['company', 'school', 'university', 'club', 'team'],
        'water entered': ['bath', 'shower', 'pool', 'hot spring'],
        'systems entered': ['hospital', 'prison', 'army'],
    },
}

# Adjective-specific categorization rules
ADJECTIVE_CATEGORIES = {
    'いい': {
        'favorable conditions': ['weather', 'climate', 'condition', 'situation'],
        'positive outcomes': ['result', 'grade', 'score', 'performance', 'achievement'],
        'good people': ['person', 'child', 'friend', 'teacher', 'student'],
        'smart solutions': ['idea', 'thought', 'plan', 'method', 'way'],
        'positive feelings': ['health', 'feeling', 'mood', 'atmosphere'],
        'good timing': ['chance', 'opportunity', 'timing', 'moment'],
        'quality relationships': ['relationship', 'friendship', 'partnership'],
    },
    'おいしい': {
        'tasty dishes': ['food', 'meal', 'dish', 'cuisine', 'cooking'],
    },
    '大きい': {
        'large structures': ['building', 'house', 'room', 'tree', 'mountain'],
        'prominent features': ['hand', 'eye', 'mouth', 'voice', 'sound'],
        'major issues': ['problem', 'difference', 'change', 'impact'],
    },
    '小さい': {
        'little ones': ['child', 'baby', 'animal', 'insect'],
        'compact spaces': ['room', 'house', 'apartment', 'office'],
        'quiet sounds': ['voice', 'sound', 'noise'],
    },
    '新しい': {
        'latest products': ['car', 'house', 'computer', 'phone', 'model'],
        'fresh ideas': ['idea', 'information', 'news', 'method', 'approach'],
        'new beginnings': ['life', 'job', 'school', 'year', 'start'],
    },
    '古い': {
        'historic items': ['building', 'house', 'temple', 'book', 'document'],
        'traditions kept': ['custom', 'tradition', 'story', 'legend'],
        'longtime connections': ['friend', 'relationship', 'memory'],
    },
    '難しい': {
        'tough problems': ['problem', 'question', 'exam', 'test', 'puzzle'],
        'complex language': ['word', 'kanji', 'language', 'grammar', 'expression'],
        'challenging work': ['work', 'job', 'task', 'project'],
    },
    '簡単': {
        'easy problems': ['problem', 'question', 'test', 'task'],
        'simple tasks': ['work', 'job', 'cooking', 'operation'],
        'clear methods': ['method', 'way', 'explanation', 'process'],
    },
}

class ComprehensiveHintFixer:
    """Fix hint quality with comprehensive semantic analysis."""

    def __init__(self):
        """Initialize the fixer."""
        self.collocations = {}
        self.hints = {}
        self.stats = defaultdict(int)

    def load_data(self, path: str) -> None:
        """Load collocation data."""
        logger.info(f"Loading data from {path}")
        with open(path, 'r', encoding='utf-8') as f:
            self.collocations = json.load(f)
        logger.info(f"Loaded {len(self.collocations['words'])} words")

    def _find_best_category(self, word_type: str, word: str, noun: Dict,
                           categories: Dict[str, List[str]]) -> str:
        """Find the best category for a noun based on its English meaning."""
        noun_english = noun['english'].lower()
        noun_word = noun['word']

        # Check each category's keywords
        best_match = None
        best_score = 0

        for category, keywords in categories.items():
            score = 0
            for keyword in keywords:
                if keyword in noun_english:
                    # Exact word match scores higher
                    if f' {keyword} ' in f' {noun_english} ' or noun_english.startswith(f'{keyword} ') or noun_english.endswith(f' {keyword}'):
                        score += 3
                    else:
                        score += 1

            if score > best_score:
                best_score = score
                best_match = category

        # If no match found, determine a fallback based on word type
        if not best_match:
            if word_type == 'verb':
                # Try to infer from the noun's general category
                if any(k in noun_english for k in ['person', 'people', 'man', 'woman', 'child']):
                    best_match = 'people involved'
                elif any(k in noun_english for k in ['place', 'location', 'area', 'spot']):
                    best_match = 'places involved'
                elif any(k in noun_english for k in ['time', 'day', 'month', 'year', 'hour']):
                    best_match = 'time periods'
                elif any(k in noun_english for k in ['thing', 'object', 'item']):
                    best_match = 'items involved'
                else:
                    # Use verb-specific fallback
                    if word == 'する':
                        best_match = 'activities performed'
                    elif word == '買う':
                        best_match = 'items purchased'
                    elif word == '来る':
                        best_match = 'arrivals expected'
                    elif word == 'ある':
                        best_match = 'elements present'
                    elif word == '行く':
                        best_match = 'destinations visited'
                    else:
                        best_match = 'related elements'
            else:  # adjective
                best_match = 'described items'

        return best_match

    def generate_hints(self) -> Dict:
        """Generate comprehensive hints for all collocations."""
        logger.info("Generating comprehensive hints")

        all_hints = {}

        # Process each word
        for word, data in self.collocations['words'].items():
            word_type = data['type']

            if word_type not in ['verb', 'adjective']:
                continue

            word_hints = {}

            # Get the appropriate categories for this word
            if word_type == 'verb':
                categories = VERB_CATEGORIES.get(word, {})
                self.stats['verbs_processed'] += 1
            else:
                # Check various forms of the adjective
                categories = None
                for adj_form in [word, word.replace('い', ''), word + 'い']:
                    if adj_form in ADJECTIVE_CATEGORIES:
                        categories = ADJECTIVE_CATEGORIES[adj_form]
                        break
                if not categories:
                    categories = {}
                self.stats['adjectives_processed'] += 1

            # Process each noun
            for noun in data['matches'].get('nouns', []):
                noun_word = noun['word']

                # Find the best category for this noun
                category = self._find_best_category(word_type, word, noun, categories)

                # Clean up the category name (remove underscores, make it readable)
                hint = category.replace('_', ' ')

                # Remove any [verb] markers
                hint = re.sub(r'\[.*?\]', '', hint).strip()

                # Ensure hint doesn't contain generic terms
                generic_terms = ['things', 'actions', 'concepts', 'stuff']
                for term in generic_terms:
                    if term in hint.lower():
                        self.stats['generic_eliminated'] += 1
                        # Replace with more specific hint
                        if word_type == 'verb':
                            hint = category.replace('things', 'items').replace('actions', 'activities')
                        else:
                            hint = category.replace('things', 'items')

                word_hints[noun_word] = hint
                self.stats['hints_created'] += 1

            if word_hints:
                all_hints[word] = word_hints

        logger.info(f"Generated {self.stats['hints_created']} hints")
        return all_hints

    def validate_coverage(self, hints: Dict) -> Dict:
        """Validate hint coverage and quality."""
        logger.info("Validating hint coverage")

        validation = {
            'coverage': {},
            'quality_issues': [],
            'generic_hints': [],
            'verb_specificity': {}
        }

        total_expected = 0
        total_found = 0

        for word, data in self.collocations['words'].items():
            if data['type'] in ['verb', 'adjective']:
                nouns = data['matches'].get('nouns', [])
                total_expected += len(nouns)

                if word in hints:
                    found = len(hints[word])
                    total_found += found

                    # Check for quality issues
                    hint_counts = Counter(hints[word].values())

                    for noun, hint in hints[word].items():
                        # Check for generic terms
                        if any(term in hint.lower() for term in ['things', 'actions', 'concepts', 'related items']):
                            validation['generic_hints'].append(f"{word}-{noun}: {hint}")

                        # Check for markers
                        if '[' in hint and ']' in hint:
                            validation['quality_issues'].append(f"Marker in {word}-{noun}: {hint}")

                    # Check specificity
                    if nouns:
                        max_usage = max(hint_counts.values()) if hint_counts else 0
                        specificity_pct = (max_usage / len(nouns)) * 100
                        if specificity_pct > 70:
                            most_common_hint = hint_counts.most_common(1)[0][0]
                            validation['verb_specificity'][word] = f"{specificity_pct:.1f}% use '{most_common_hint}'"

        validation['coverage']['total_expected'] = total_expected
        validation['coverage']['total_found'] = total_found
        validation['coverage']['percentage'] = (total_found / total_expected * 100) if total_expected > 0 else 0

        return validation

    def save_hints(self, hints: Dict, output_path: str) -> None:
        """Save hints to file."""
        logger.info(f"Saving hints to {output_path}")

        # Get validation stats
        validation = self.validate_coverage(hints)

        output_data = {
            'version': '8.0.0',
            'generated_date': '2025-11-11',
            'coverage': f"{validation['coverage']['percentage']:.1f}%",
            'statistics': {
                'total_pairs': self.stats['hints_created'],
                'verbs_processed': self.stats['verbs_processed'],
                'adjectives_processed': self.stats['adjectives_processed'],
                'generic_eliminated': self.stats['generic_eliminated'],
                'coverage_percentage': validation['coverage']['percentage'],
                'generic_remaining': len(validation['generic_hints']),
                'quality_issues': len(validation['quality_issues'])
            },
            'hints': hints
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info("Hints saved successfully")
        return validation


def main():
    """Main execution."""
    fixer = ComprehensiveHintFixer()

    # File paths
    input_path = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json'
    output_path = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\output\collocation_hints_v8.json'

    # Load data
    fixer.load_data(input_path)

    # Generate hints
    hints = fixer.generate_hints()

    # Save and validate
    validation = fixer.save_hints(hints, output_path)

    # Print report
    print("\n" + "="*60)
    print("COMPREHENSIVE HINT GENERATION COMPLETE")
    print("="*60)
    print(f"Coverage: {validation['coverage']['percentage']:.1f}%")
    print(f"Total pairs: {fixer.stats['hints_created']}")
    print(f"Verbs processed: {fixer.stats['verbs_processed']}")
    print(f"Adjectives processed: {fixer.stats['adjectives_processed']}")
    print(f"Generic hints eliminated: {fixer.stats['generic_eliminated']}")

    if validation['generic_hints']:
        print(f"\n⚠ Warning: {len(validation['generic_hints'])} hints still contain generic terms")
        print("Examples:")
        for example in validation['generic_hints'][:5]:
            print(f"  - {example}")

    if validation['verb_specificity']:
        print(f"\n📊 Verbs needing more variety ({len(validation['verb_specificity'])} total):")
        for verb, msg in list(validation['verb_specificity'].items())[:5]:
            print(f"  - {verb}: {msg}")

    # Sample of improved hints for key verbs
    print("\n📝 Sample hints for problematic verbs:")
    for verb in ['する', '買う', '来る', 'ある', '行く']:
        if verb in hints:
            unique_hints = list(set(hints[verb].values()))[:5]
            print(f"\n{verb}:")
            for hint in unique_hints:
                example_nouns = [n for n, h in hints[verb].items() if h == hint][:3]
                print(f"  - '{hint}': {', '.join(example_nouns)}")

    print(f"\n✅ Output saved to: {output_path}")


if __name__ == '__main__':
    main()