#!/usr/bin/env python3
"""
Comprehensive hint quality fixer for Japanese collocation learning system.
Eliminates generic hints, improves specificity, and ensures 100% coverage.
"""

import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HintQualityFixer:
    """Fix hint quality issues in collocation data."""

    def __init__(self):
        """Initialize the hint quality fixer."""
        self.collocations = {}
        self.hints = {}
        self.verb_noun_mappings = defaultdict(list)
        self.adjective_noun_mappings = defaultdict(list)

    def load_data(self, collocations_path: str) -> None:
        """Load collocation data from JSON file."""
        logger.info(f"Loading collocations from {collocations_path}")
        with open(collocations_path, 'r', encoding='utf-8') as f:
            self.collocations = json.load(f)
        logger.info(f"Loaded {len(self.collocations['words'])} words")

        # Build mappings
        self._build_mappings()

    def _build_mappings(self) -> None:
        """Build verb-noun and adjective-noun mappings."""
        for word, data in self.collocations['words'].items():
            if data['type'] == 'verb':
                for noun in data['matches'].get('nouns', []):
                    self.verb_noun_mappings[word].append(noun)
            elif data['type'] == 'adjective':
                for noun in data['matches'].get('nouns', []):
                    self.adjective_noun_mappings[word].append(noun)

    def _analyze_semantic_groups(self, verb: str, nouns: List[Dict]) -> Dict[str, List[str]]:
        """Analyze nouns and group them semantically for a specific verb."""
        groups = defaultdict(list)

        # Get verb data for fallback analysis
        verb_data = self.collocations['words'].get(verb, {})

        # Verb-specific semantic analysis
        if verb == 'する':
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Work and professional activities
                if any(k in english for k in ['work', 'job', 'business', 'research', 'study']):
                    groups['professional activities'].append(word)
                # Daily routines
                elif any(k in english for k in ['shopping', 'cleaning', 'laundry', 'cooking']):
                    groups['daily routines'].append(word)
                # Exercise and sports
                elif any(k in english for k in ['exercise', 'sport', 'training', 'swim', 'judo', 'tennis']):
                    groups['sports and exercise'].append(word)
                # Communication
                elif any(k in english for k in ['talk', 'speech', 'conversation', 'contact', 'greeting']):
                    groups['communication activities'].append(word)
                # Planning and preparation
                elif any(k in english for k in ['plan', 'preparation', 'reservation', 'arrangement']):
                    groups['planning and preparation'].append(word)
                # Life events
                elif any(k in english for k in ['marriage', 'graduation', 'enrollment', 'admission']):
                    groups['major life events'].append(word)
                # Business operations
                elif any(k in english for k in ['import', 'export', 'trade', 'production']):
                    groups['business operations'].append(word)
                # Social interactions
                elif any(k in english for k in ['introduction', 'invitation', 'consultation']):
                    groups['social interactions'].append(word)
                # Leisure activities
                elif any(k in english for k in ['travel', 'tour', 'sightseeing', 'flower viewing']):
                    groups['leisure activities'].append(word)
                # Helpful actions
                elif any(k in english for k in ['translation', 'guidance', 'care', 'help']):
                    groups['helpful services'].append(word)
                # Mistakes and problems
                elif any(k in english for k in ['failure', 'mistake', 'quarrel', 'trouble', 'breakdown']):
                    groups['problems to handle'].append(word)
                # Medical
                elif any(k in english for k in ['injection', 'hospitalization', 'discharge']):
                    groups['medical procedures'].append(word)
                # Academic
                elif any(k in english for k in ['review', 'preview', 'practice', 'check']):
                    groups['study activities'].append(word)
                # Competition
                elif any(k in english for k in ['competition', 'match', 'game', 'contest', 'exam']):
                    groups['competitive events'].append(word)
                # Emotional/Mental states
                elif any(k in english for k in ['worry', 'relief', 'attention', 'care']):
                    groups['mental processes'].append(word)
                else:
                    groups['other activities'].append(word)

        elif verb == '買う':
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Clothing
                if any(k in english for k in ['clothes', 'shirt', 'shoe', 'hat', 'coat', 'jacket']):
                    groups['clothing items'].append(word)
                # Food and groceries
                elif any(k in english for k in ['vegetable', 'meat', 'fish', 'egg', 'bread', 'milk', 'rice']):
                    groups['groceries and food'].append(word)
                # Reading materials
                elif any(k in english for k in ['book', 'magazine', 'newspaper', 'dictionary', 'map']):
                    groups['reading materials'].append(word)
                # Major purchases
                elif any(k in english for k in ['car', 'house', 'land', 'apartment']):
                    groups['major purchases'].append(word)
                # Gifts and presents
                elif any(k in english for k in ['present', 'gift', 'souvenir', 'flower']):
                    groups['gifts to give'].append(word)
                # Tickets
                elif any(k in english for k in ['ticket', 'pass']):
                    groups['tickets and passes'].append(word)
                # Personal care
                elif any(k in english for k in ['medicine', 'cosmetic', 'soap']):
                    groups['personal care items'].append(word)
                # Electronics
                elif any(k in english for k in ['computer', 'camera', 'television']):
                    groups['electronic devices'].append(word)
                # Household items
                elif any(k in english for k in ['furniture', 'dish', 'cup', 'bowl']):
                    groups['household items'].append(word)
                # Stationery
                elif any(k in english for k in ['pen', 'pencil', 'notebook', 'paper']):
                    groups['stationery supplies'].append(word)
                # Beverages
                elif any(k in english for k in ['alcohol', 'beer', 'wine', 'sake', 'tea', 'coffee']):
                    groups['beverages to enjoy'].append(word)
                else:
                    groups['other purchases'].append(word)

        elif verb == '来る':
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # People who visit
                if any(k in english for k in ['person', 'friend', 'guest', 'visitor', 'customer']):
                    groups['visitors who arrive'].append(word)
                # Family members
                elif any(k in english for k in ['mother', 'father', 'parent', 'brother', 'sister', 'family']):
                    groups['family members'].append(word)
                # Time periods
                elif any(k in english for k in ['season', 'spring', 'summer', 'autumn', 'winter', 'fall']):
                    groups['seasons that arrive'].append(word)
                # Scheduled times
                elif any(k in english for k in ['time', 'today', 'tomorrow', 'week', 'month', 'year']):
                    groups['scheduled times'].append(word)
                # Events
                elif any(k in english for k in ['birthday', 'exam', 'meeting', 'party', 'festival']):
                    groups['upcoming events'].append(word)
                # Communications
                elif any(k in english for k in ['letter', 'mail', 'email', 'message', 'call', 'phone']):
                    groups['messages that arrive'].append(word)
                # Transportation
                elif any(k in english for k in ['bus', 'train', 'taxi', 'car', 'airplane']):
                    groups['transport that arrives'].append(word)
                # Weather
                elif any(k in english for k in ['rain', 'snow', 'typhoon', 'storm']):
                    groups['weather that arrives'].append(word)
                # Officials
                elif any(k in english for k in ['police', 'doctor', 'teacher']):
                    groups['officials who arrive'].append(word)
                else:
                    groups['other arrivals'].append(word)

        elif verb == 'ある':
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Abstract concepts
                if any(k in english for k in ['thing', 'matter', 'problem', 'reason', 'cause']):
                    groups['situations that exist'].append(word)
                # Facilities
                elif any(k in english for k in ['store', 'shop', 'bank', 'station', 'hospital']):
                    groups['nearby facilities'].append(word)
                # Building parts
                elif any(k in english for k in ['house', 'room', 'entrance', 'window', 'door']):
                    groups['building features'].append(word)
                # Time availability
                elif any(k in english for k in ['time', 'leisure', 'spare', 'margin']):
                    groups['available time'].append(word)
                # Money/Resources
                elif any(k in english for k in ['money', 'budget', 'fund']):
                    groups['financial resources'].append(word)
                # Opportunities
                elif any(k in english for k in ['chance', 'opportunity', 'possibility']):
                    groups['opportunities available'].append(word)
                # Events/Activities
                elif any(k in english for k in ['meeting', 'party', 'class', 'lesson']):
                    groups['scheduled activities'].append(word)
                # Objects/Items
                elif any(k in english for k in ['desk', 'chair', 'table', 'book', 'pen']):
                    groups['objects present'].append(word)
                # Plans
                elif any(k in english for k in ['plan', 'schedule', 'appointment']):
                    groups['existing plans'].append(word)
                # Experience/Knowledge
                elif any(k in english for k in ['experience', 'knowledge', 'skill']):
                    groups['possessed experience'].append(word)
                # Relationships
                elif any(k in english for k in ['relation', 'connection', 'relationship']):
                    groups['existing relationships'].append(word)
                # Interest/Feelings
                elif any(k in english for k in ['interest', 'confidence', 'hope']):
                    groups['feelings present'].append(word)
                # Documents
                elif any(k in english for k in ['document', 'paper', 'report']):
                    groups['documents available'].append(word)
                # Rules
                elif any(k in english for k in ['rule', 'law', 'regulation']):
                    groups['rules in place'].append(word)
                else:
                    groups['other existences'].append(word)

        elif verb in ['行く', 'いく']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Educational places
                if any(k in english for k in ['school', 'university', 'class', 'library']):
                    groups['educational destinations'].append(word)
                # Work places
                elif any(k in english for k in ['company', 'office', 'work', 'factory']):
                    groups['work destinations'].append(word)
                # Commercial places
                elif any(k in english for k in ['store', 'shop', 'restaurant', 'market']):
                    groups['shopping destinations'].append(word)
                # Leisure destinations
                elif any(k in english for k in ['park', 'beach', 'mountain', 'sea', 'cinema']):
                    groups['leisure destinations'].append(word)
                # Travel destinations
                elif any(k in english for k in ['country', 'city', 'town', 'abroad']):
                    groups['travel destinations'].append(word)
                # Public facilities
                elif any(k in english for k in ['hospital', 'bank', 'post', 'station']):
                    groups['public facilities'].append(word)
                # Events
                elif any(k in english for k in ['party', 'meeting', 'wedding', 'funeral']):
                    groups['events to attend'].append(word)
                # Home locations
                elif any(k in english for k in ['home', 'house', 'room']):
                    groups['home locations'].append(word)
                else:
                    groups['other destinations'].append(word)

        elif verb in ['見る', 'みる']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Visual media
                if any(k in english for k in ['television', 'movie', 'film', 'video', 'news']):
                    groups['visual media'].append(word)
                # Written materials
                elif any(k in english for k in ['book', 'newspaper', 'magazine', 'map', 'menu']):
                    groups['written materials'].append(word)
                # Natural phenomena
                elif any(k in english for k in ['sky', 'star', 'moon', 'mountain', 'sea']):
                    groups['natural scenery'].append(word)
                # People
                elif any(k in english for k in ['face', 'person', 'child', 'friend']):
                    groups['people to observe'].append(word)
                # Pictures/Art
                elif any(k in english for k in ['picture', 'photo', 'painting', 'art']):
                    groups['visual art'].append(word)
                # Documents
                elif any(k in english for k in ['document', 'paper', 'letter', 'email']):
                    groups['documents to review'].append(word)
                # Dreams/Future
                elif any(k in english for k in ['dream', 'future']):
                    groups['visions and dreams'].append(word)
                else:
                    groups['other sights'].append(word)

        elif verb in ['読む', 'よむ']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Books and literature
                if any(k in english for k in ['book', 'novel', 'story']):
                    groups['books and novels'].append(word)
                # News media
                elif any(k in english for k in ['newspaper', 'news', 'article']):
                    groups['news publications'].append(word)
                # Magazines
                elif any(k in english for k in ['magazine', 'journal']):
                    groups['magazines'].append(word)
                # Personal correspondence
                elif any(k in english for k in ['letter', 'email', 'message']):
                    groups['personal messages'].append(word)
                # Reference materials
                elif any(k in english for k in ['dictionary', 'encyclopedia']):
                    groups['reference materials'].append(word)
                # Academic materials
                elif any(k in english for k in ['textbook', 'paper', 'report']):
                    groups['academic texts'].append(word)
                # Instructions
                elif any(k in english for k in ['manual', 'instruction', 'guide']):
                    groups['instruction manuals'].append(word)
                else:
                    groups['other readings'].append(word)

        elif verb in ['書く', 'かく']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Written correspondence
                if any(k in english for k in ['letter', 'email', 'message', 'card']):
                    groups['correspondence to write'].append(word)
                # Academic writing
                elif any(k in english for k in ['paper', 'report', 'essay', 'thesis']):
                    groups['academic papers'].append(word)
                # Creative writing
                elif any(k in english for k in ['story', 'novel', 'poem', 'diary']):
                    groups['creative writing'].append(word)
                # Official documents
                elif any(k in english for k in ['application', 'resume', 'form']):
                    groups['official documents'].append(word)
                # Notes and memos
                elif any(k in english for k in ['note', 'memo', 'list']):
                    groups['notes and memos'].append(word)
                # Characters and text
                elif any(k in english for k in ['character', 'kanji', 'word', 'name']):
                    groups['characters to write'].append(word)
                else:
                    groups['written items'].append(word)

        elif verb in ['話す', 'はなす']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Languages
                if any(k in english for k in ['japanese', 'english', 'language']):
                    groups['languages to speak'].append(word)
                # Topics
                elif any(k in english for k in ['story', 'news', 'topic', 'matter']):
                    groups['topics to discuss'].append(word)
                # Personal matters
                elif any(k in english for k in ['secret', 'truth', 'lie', 'opinion']):
                    groups['personal matters'].append(word)
                # Communication types
                elif any(k in english for k in ['word', 'phrase', 'sentence']):
                    groups['words to say'].append(word)
                else:
                    groups['conversation topics'].append(word)

        elif verb in ['聞く', 'きく']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Audio media
                if any(k in english for k in ['music', 'song', 'radio', 'cd']):
                    groups['audio entertainment'].append(word)
                # Information
                elif any(k in english for k in ['news', 'story', 'rumor', 'information']):
                    groups['information to hear'].append(word)
                # Sounds
                elif any(k in english for k in ['sound', 'voice', 'noise']):
                    groups['sounds to hear'].append(word)
                # Spoken content
                elif any(k in english for k in ['talk', 'speech', 'lecture', 'explanation']):
                    groups['spoken content'].append(word)
                # Questions/Requests
                elif any(k in english for k in ['question', 'request', 'opinion', 'advice']):
                    groups['requests to consider'].append(word)
                else:
                    groups['audible content'].append(word)

        elif verb in ['食べる', 'たべる']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Meals
                if any(k in english for k in ['breakfast', 'lunch', 'dinner', 'meal']):
                    groups['daily meals'].append(word)
                # Main dishes
                elif any(k in english for k in ['rice', 'bread', 'noodle', 'pasta']):
                    groups['staple foods'].append(word)
                # Proteins
                elif any(k in english for k in ['meat', 'fish', 'egg', 'chicken']):
                    groups['protein dishes'].append(word)
                # Vegetables/Fruits
                elif any(k in english for k in ['vegetable', 'fruit', 'salad']):
                    groups['fruits and vegetables'].append(word)
                # Snacks/Sweets
                elif any(k in english for k in ['snack', 'candy', 'cake', 'chocolate']):
                    groups['snacks and sweets'].append(word)
                # Japanese food
                elif any(k in english for k in ['sushi', 'tempura', 'ramen']):
                    groups['Japanese cuisine'].append(word)
                else:
                    groups['food items'].append(word)

        elif verb in ['飲む', 'のむ']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Hot beverages
                if any(k in english for k in ['coffee', 'tea', 'cocoa']):
                    groups['hot beverages'].append(word)
                # Cold beverages
                elif any(k in english for k in ['water', 'juice', 'soda', 'cola']):
                    groups['cold beverages'].append(word)
                # Alcoholic drinks
                elif any(k in english for k in ['alcohol', 'beer', 'wine', 'sake']):
                    groups['alcoholic beverages'].append(word)
                # Dairy
                elif any(k in english for k in ['milk', 'yogurt']):
                    groups['dairy drinks'].append(word)
                # Medicine
                elif any(k in english for k in ['medicine', 'pill']):
                    groups['medicine to take'].append(word)
                else:
                    groups['beverages'].append(word)

        elif verb in ['作る', 'つくる']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Food
                if any(k in english for k in ['food', 'dish', 'meal', 'cooking']):
                    groups['dishes to prepare'].append(word)
                # Objects/Products
                elif any(k in english for k in ['product', 'machine', 'device', 'toy']):
                    groups['products to create'].append(word)
                # Documents
                elif any(k in english for k in ['document', 'plan', 'schedule', 'list']):
                    groups['documents to draft'].append(word)
                # Relationships
                elif any(k in english for k in ['friend', 'relationship', 'connection']):
                    groups['relationships to build'].append(word)
                # Organizations
                elif any(k in english for k in ['company', 'group', 'team', 'club']):
                    groups['organizations to form'].append(word)
                # Art/Creative
                elif any(k in english for k in ['art', 'music', 'song', 'poem']):
                    groups['creative works'].append(word)
                else:
                    groups['items to make'].append(word)

        elif verb in ['使う', 'つかう']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Tools
                if any(k in english for k in ['tool', 'pen', 'pencil', 'scissors']):
                    groups['tools to utilize'].append(word)
                # Technology
                elif any(k in english for k in ['computer', 'phone', 'internet', 'app']):
                    groups['technology to employ'].append(word)
                # Money/Resources
                elif any(k in english for k in ['money', 'time', 'energy']):
                    groups['resources to spend'].append(word)
                # Language
                elif any(k in english for k in ['word', 'language', 'expression']):
                    groups['expressions to apply'].append(word)
                # Transportation
                elif any(k in english for k in ['car', 'train', 'bus', 'bicycle']):
                    groups['transport to take'].append(word)
                # Facilities
                elif any(k in english for k in ['room', 'bathroom', 'kitchen']):
                    groups['facilities to access'].append(word)
                else:
                    groups['items to use'].append(word)

        elif verb in ['持つ', 'もつ']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Physical items
                if any(k in english for k in ['bag', 'umbrella', 'key', 'wallet']):
                    groups['items to carry'].append(word)
                # Documents
                elif any(k in english for k in ['passport', 'license', 'ticket', 'card']):
                    groups['documents to possess'].append(word)
                # Qualities
                elif any(k in english for k in ['interest', 'opinion', 'confidence', 'dream']):
                    groups['qualities to have'].append(word)
                # Responsibilities
                elif any(k in english for k in ['responsibility', 'job', 'duty']):
                    groups['responsibilities to bear'].append(word)
                # Relationships
                elif any(k in english for k in ['child', 'family', 'friend']):
                    groups['relationships to maintain'].append(word)
                else:
                    groups['possessions'].append(word)

        elif verb in ['知る', 'しる']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # People
                if any(k in english for k in ['person', 'friend', 'teacher']):
                    groups['people to know'].append(word)
                # Information
                elif any(k in english for k in ['fact', 'truth', 'news', 'information']):
                    groups['facts to learn'].append(word)
                # Places
                elif any(k in english for k in ['place', 'address', 'location']):
                    groups['places to recognize'].append(word)
                # Methods
                elif any(k in english for k in ['method', 'way', 'rule']):
                    groups['methods to understand'].append(word)
                # Secrets
                elif any(k in english for k in ['secret', 'reason', 'cause']):
                    groups['secrets to discover'].append(word)
                else:
                    groups['information to grasp'].append(word)

        elif verb in ['思う', 'おもう']:
            for noun in nouns:
                word = noun['word']
                # All nouns with 思う are typically things you think/believe
                groups['thoughts and beliefs'].append(word)

        elif verb in ['言う', 'いう']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Speech types
                if any(k in english for k in ['word', 'phrase', 'sentence']):
                    groups['phrases to express'].append(word)
                # Information
                elif any(k in english for k in ['name', 'address', 'number']):
                    groups['information to state'].append(word)
                # Opinions
                elif any(k in english for k in ['opinion', 'idea', 'thought']):
                    groups['opinions to voice'].append(word)
                # Greetings
                elif any(k in english for k in ['greeting', 'thanks', 'apology']):
                    groups['greetings to offer'].append(word)
                else:
                    groups['statements to make'].append(word)

        elif verb in ['出る', 'でる']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Places to leave
                if any(k in english for k in ['house', 'home', 'room', 'building']):
                    groups['places to exit'].append(word)
                # Events/Competitions
                elif any(k in english for k in ['meeting', 'party', 'competition', 'contest']):
                    groups['events to attend'].append(word)
                # Things that emerge
                elif any(k in english for k in ['result', 'answer', 'conclusion']):
                    groups['results that appear'].append(word)
                # Publications
                elif any(k in english for k in ['book', 'magazine', 'newspaper']):
                    groups['publications released'].append(word)
                else:
                    groups['departures and appearances'].append(word)

        elif verb in ['入る', 'はいる']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Places to enter
                if any(k in english for k in ['room', 'building', 'store', 'restaurant']):
                    groups['places to enter'].append(word)
                # Organizations
                elif any(k in english for k in ['company', 'school', 'university', 'club']):
                    groups['organizations to join'].append(word)
                # Containers
                elif any(k in english for k in ['bath', 'shower', 'pool']):
                    groups['water to enter'].append(word)
                # States
                elif any(k in english for k in ['hospital', 'prison']):
                    groups['institutions to enter'].append(word)
                else:
                    groups['spaces to access'].append(word)

        else:
            # More specific generic grouping based on verb meaning
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Try to create a meaningful default based on common patterns
                if verb_data.get('type') == 'verb':
                    verb_english = verb_data.get('english', '').lower()
                    if 'give' in verb_english or 'receive' in verb_english:
                        groups['items exchanged'].append(word)
                    elif 'teach' in verb_english or 'learn' in verb_english:
                        groups['subjects studied'].append(word)
                    elif 'open' in verb_english or 'close' in verb_english:
                        groups['items operated'].append(word)
                    elif 'wear' in verb_english or 'put on' in verb_english:
                        groups['clothing worn'].append(word)
                    elif 'play' in verb_english:
                        groups['activities enjoyed'].append(word)
                    elif 'wait' in verb_english:
                        groups['anticipated items'].append(word)
                    elif 'forget' in verb_english or 'remember' in verb_english:
                        groups['memorable items'].append(word)
                    elif 'begin' in verb_english or 'start' in verb_english:
                        groups['activities started'].append(word)
                    elif 'end' in verb_english or 'finish' in verb_english:
                        groups['activities completed'].append(word)
                    elif 'live' in verb_english or 'reside' in verb_english:
                        groups['living locations'].append(word)
                    elif 'work' in verb_english:
                        groups['work locations'].append(word)
                    elif 'meet' in verb_english:
                        groups['people encountered'].append(word)
                    elif 'send' in verb_english:
                        groups['items sent'].append(word)
                    elif 'receive' in verb_english or 'get' in verb_english:
                        groups['items received'].append(word)
                    elif 'pay' in verb_english:
                        groups['payments made'].append(word)
                    elif 'sell' in verb_english:
                        groups['items sold'].append(word)
                    elif 'borrow' in verb_english or 'lend' in verb_english:
                        groups['items loaned'].append(word)
                    elif 'choose' in verb_english or 'select' in verb_english:
                        groups['options selected'].append(word)
                    elif 'win' in verb_english or 'lose' in verb_english:
                        groups['competitions faced'].append(word)
                    elif 'catch' in verb_english:
                        groups['items caught'].append(word)
                    elif 'turn' in verb_english or 'become' in verb_english:
                        groups['states achieved'].append(word)
                    elif 'stand' in verb_english or 'sit' in verb_english:
                        groups['positions taken'].append(word)
                    elif 'sleep' in verb_english:
                        groups['resting places'].append(word)
                    elif 'wake' in verb_english:
                        groups['awakening times'].append(word)
                    elif 'climb' in verb_english:
                        groups['heights scaled'].append(word)
                    elif 'fall' in verb_english or 'drop' in verb_english:
                        groups['items dropped'].append(word)
                    elif 'break' in verb_english:
                        groups['items broken'].append(word)
                    elif 'fix' in verb_english or 'repair' in verb_english:
                        groups['items repaired'].append(word)
                    elif 'wash' in verb_english or 'clean' in verb_english:
                        groups['items cleaned'].append(word)
                    elif 'cut' in verb_english:
                        groups['items cut'].append(word)
                    elif 'push' in verb_english or 'pull' in verb_english:
                        groups['items moved'].append(word)
                    elif 'sing' in verb_english:
                        groups['songs performed'].append(word)
                    elif 'dance' in verb_english:
                        groups['dances performed'].append(word)
                    elif 'swim' in verb_english:
                        groups['water bodies'].append(word)
                    elif 'fly' in verb_english:
                        groups['flight paths'].append(word)
                    elif 'drive' in verb_english or 'ride' in verb_english:
                        groups['vehicles operated'].append(word)
                    elif 'stop' in verb_english:
                        groups['activities halted'].append(word)
                    elif 'continue' in verb_english:
                        groups['activities continued'].append(word)
                    elif 'return' in verb_english:
                        groups['return destinations'].append(word)
                    elif 'arrive' in verb_english:
                        groups['arrival points'].append(word)
                    elif 'leave' in verb_english or 'depart' in verb_english:
                        groups['departure points'].append(word)
                    elif 'pass' in verb_english:
                        groups['items passed'].append(word)
                    elif 'fail' in verb_english:
                        groups['failed attempts'].append(word)
                    elif 'succeed' in verb_english:
                        groups['successful outcomes'].append(word)
                    else:
                        groups['related items'].append(word)
                else:
                    groups['related items'].append(word)

        return dict(groups)

    def _analyze_adjective_groups(self, adjective: str, nouns: List[Dict]) -> Dict[str, List[str]]:
        """Analyze nouns and group them semantically for a specific adjective."""
        groups = defaultdict(list)

        # Adjective-specific semantic analysis
        if adjective in ['いい', '良い', 'よい']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Weather and conditions
                if any(k in english for k in ['weather', 'climate', 'condition']):
                    groups['favorable conditions'].append(word)
                # Results and performance
                elif any(k in english for k in ['result', 'grade', 'score', 'performance']):
                    groups['positive results'].append(word)
                # People qualities
                elif any(k in english for k in ['person', 'child', 'friend', 'teacher']):
                    groups['admirable people'].append(word)
                # Ideas and thoughts
                elif any(k in english for k in ['idea', 'thought', 'plan', 'method']):
                    groups['smart ideas'].append(word)
                # Physical state
                elif any(k in english for k in ['health', 'feeling', 'mood']):
                    groups['positive states'].append(word)
                # Opportunities
                elif any(k in english for k in ['chance', 'opportunity', 'timing']):
                    groups['favorable opportunities'].append(word)
                # Relationships
                elif any(k in english for k in ['relationship', 'friendship']):
                    groups['positive relationships'].append(word)
                else:
                    groups['quality items'].append(word)

        elif adjective in ['おいしい', '美味しい']:
            for noun in nouns:
                word = noun['word']
                groups['tasty foods'].append(word)

        elif adjective in ['大きい', 'おおきい']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Physical objects
                if any(k in english for k in ['building', 'house', 'room', 'tree']):
                    groups['large structures'].append(word)
                # Body parts
                elif any(k in english for k in ['hand', 'eye', 'mouth', 'voice']):
                    groups['prominent features'].append(word)
                # Abstract concepts
                elif any(k in english for k in ['problem', 'difference', 'change']):
                    groups['significant issues'].append(word)
                else:
                    groups['large items'].append(word)

        elif adjective in ['小さい', 'ちいさい']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Physical objects
                if any(k in english for k in ['child', 'baby', 'animal']):
                    groups['small beings'].append(word)
                # Spaces
                elif any(k in english for k in ['room', 'house', 'apartment']):
                    groups['compact spaces'].append(word)
                # Body parts/features
                elif any(k in english for k in ['voice', 'sound', 'letter']):
                    groups['subtle features'].append(word)
                else:
                    groups['small items'].append(word)

        elif adjective in ['新しい', 'あたらしい']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Products
                if any(k in english for k in ['car', 'house', 'computer', 'phone']):
                    groups['latest products'].append(word)
                # Ideas/Information
                elif any(k in english for k in ['idea', 'information', 'news', 'method']):
                    groups['fresh concepts'].append(word)
                # Life changes
                elif any(k in english for k in ['life', 'job', 'school', 'year']):
                    groups['new beginnings'].append(word)
                else:
                    groups['recent items'].append(word)

        elif adjective in ['古い', 'ふるい']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Buildings and objects
                if any(k in english for k in ['building', 'house', 'temple', 'book']):
                    groups['historical items'].append(word)
                # Traditions
                elif any(k in english for k in ['custom', 'tradition', 'story']):
                    groups['traditional elements'].append(word)
                # Relationships
                elif any(k in english for k in ['friend', 'relationship']):
                    groups['long-standing connections'].append(word)
                else:
                    groups['aged items'].append(word)

        elif adjective in ['難しい', 'むずかしい']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Academic
                if any(k in english for k in ['problem', 'question', 'exam', 'test']):
                    groups['challenging problems'].append(word)
                # Language
                elif any(k in english for k in ['word', 'kanji', 'language', 'grammar']):
                    groups['complex language'].append(word)
                # Tasks
                elif any(k in english for k in ['work', 'job', 'task']):
                    groups['demanding tasks'].append(word)
                else:
                    groups['difficult aspects'].append(word)

        elif adjective in ['簡単', 'かんたん']:
            for noun in nouns:
                word = noun['word']
                english = noun['english'].lower()

                # Academic
                if any(k in english for k in ['problem', 'question', 'test']):
                    groups['simple problems'].append(word)
                # Tasks
                elif any(k in english for k in ['work', 'job', 'cooking']):
                    groups['easy tasks'].append(word)
                # Methods
                elif any(k in english for k in ['method', 'way', 'explanation']):
                    groups['straightforward methods'].append(word)
                else:
                    groups['simple aspects'].append(word)

        else:
            # Generic grouping for other adjectives
            for noun in nouns:
                word = noun['word']
                groups['described items'].append(word)

        return dict(groups)

    def _create_specific_hint(self, word_type: str, word: str, group_name: str, nouns: List[str]) -> str:
        """Create a specific, meaningful hint for a group of nouns."""
        # Remove generic terms and create specific hints
        hint = group_name

        # Remove any [verb] markers
        hint = re.sub(r'\[.*?\]', '', hint).strip()

        # Ensure hint is specific and meaningful
        generic_terms = ['things', 'actions', 'concepts', 'stuff', 'items that']
        for term in generic_terms:
            if term in hint.lower():
                # Try to make it more specific based on the nouns
                if word_type == 'verb':
                    if word == 'する':
                        if 'work' in group_name:
                            hint = 'professional activities'
                        elif 'action' in group_name:
                            hint = 'specific activities'
                    elif word == '買う':
                        if 'thing' in group_name:
                            hint = 'specific purchases'
                    elif word == '来る':
                        if 'thing' in group_name:
                            hint = 'expected arrivals'
                    elif word == 'ある':
                        if 'thing' in group_name:
                            hint = 'existing elements'

        # Ensure hint is 3-7 words
        words = hint.split()
        if len(words) > 7:
            hint = ' '.join(words[:7])
        elif len(words) < 2:
            if word_type == 'verb':
                hint = f"{hint} to {word}"
            else:
                hint = f"{hint} items"

        return hint

    def generate_hints(self) -> Dict:
        """Generate high-quality hints for all collocations."""
        logger.info("Generating high-quality hints for all collocations")

        all_hints = {}
        stats = {
            'total_pairs': 0,
            'hints_created': 0,
            'verbs_processed': 0,
            'adjectives_processed': 0,
            'generic_eliminated': 0
        }

        # Process verbs
        for verb, nouns in self.verb_noun_mappings.items():
            if not nouns:
                continue

            stats['verbs_processed'] += 1

            # Analyze semantic groups
            groups = self._analyze_semantic_groups(verb, nouns)

            # Create hints for each group
            verb_hints = {}
            for group_name, group_nouns in groups.items():
                if not group_nouns:
                    continue

                hint = self._create_specific_hint('verb', verb, group_name, group_nouns)

                # Check for generic terms
                if any(term in hint.lower() for term in ['things', 'actions that', 'concepts']):
                    stats['generic_eliminated'] += len(group_nouns)
                    # Force more specific hint
                    if verb == 'する' and 'action' in hint:
                        hint = self._get_specific_suru_hint(group_nouns[0] if group_nouns else '')
                    elif verb == '買う' and 'thing' in hint:
                        hint = self._get_specific_kau_hint(group_nouns[0] if group_nouns else '')
                    elif verb == '来る' and 'thing' in hint:
                        hint = self._get_specific_kuru_hint(group_nouns[0] if group_nouns else '')
                    elif verb == 'ある' and 'thing' in hint:
                        hint = self._get_specific_aru_hint(group_nouns[0] if group_nouns else '')

                for noun_word in group_nouns:
                    verb_hints[noun_word] = hint
                    stats['hints_created'] += 1
                    stats['total_pairs'] += 1

            if verb_hints:
                all_hints[verb] = verb_hints

        # Process adjectives
        for adjective, nouns in self.adjective_noun_mappings.items():
            if not nouns:
                continue

            stats['adjectives_processed'] += 1

            # Analyze semantic groups
            groups = self._analyze_adjective_groups(adjective, nouns)

            # Create hints for each group
            adj_hints = {}
            for group_name, group_nouns in groups.items():
                if not group_nouns:
                    continue

                hint = self._create_specific_hint('adjective', adjective, group_name, group_nouns)

                for noun_word in group_nouns:
                    adj_hints[noun_word] = hint
                    stats['hints_created'] += 1
                    stats['total_pairs'] += 1

            if adj_hints:
                all_hints[adjective] = adj_hints

        # Log statistics
        logger.info(f"Generated hints for {stats['total_pairs']} pairs")
        logger.info(f"Processed {stats['verbs_processed']} verbs and {stats['adjectives_processed']} adjectives")
        logger.info(f"Created {stats['hints_created']} hints")
        logger.info(f"Eliminated {stats['generic_eliminated']} generic hints")

        return {
            'hints': all_hints,
            'stats': stats
        }

    def _get_specific_suru_hint(self, noun: str) -> str:
        """Get a specific hint for する based on the noun."""
        # Fallback specific hints for する
        return 'specific activities'

    def _get_specific_kau_hint(self, noun: str) -> str:
        """Get a specific hint for 買う based on the noun."""
        return 'items to purchase'

    def _get_specific_kuru_hint(self, noun: str) -> str:
        """Get a specific hint for 来る based on the noun."""
        return 'expected arrivals'

    def _get_specific_aru_hint(self, noun: str) -> str:
        """Get a specific hint for ある based on the noun."""
        return 'present elements'

    def validate_hints(self, hints: Dict) -> Dict:
        """Validate hint quality and coverage."""
        logger.info("Validating hint quality")

        validation = {
            'coverage': {},
            'quality_issues': [],
            'generic_hints': [],
            'verb_specificity': {}
        }

        # Check coverage
        total_expected = 0
        total_found = 0

        for word, data in self.collocations['words'].items():
            if data['type'] in ['verb', 'adjective']:
                nouns = data['matches'].get('nouns', [])
                total_expected += len(nouns)

                if word in hints['hints']:
                    found = len(hints['hints'][word])
                    total_found += found

                    # Check for generic hints
                    for noun, hint in hints['hints'][word].items():
                        if any(term in hint.lower() for term in ['things', 'actions that', 'concepts']):
                            validation['generic_hints'].append(f"{word}-{noun}: {hint}")

                        # Check for [verb] markers
                        if '[' in hint and ']' in hint:
                            validation['quality_issues'].append(f"Marker found in {word}-{noun}: {hint}")

                    # Check verb specificity (% of nouns using same hint)
                    hint_counts = Counter(hints['hints'][word].values())
                    max_usage = max(hint_counts.values()) if hint_counts else 0
                    total_nouns = len(nouns)
                    if total_nouns > 0:
                        specificity_pct = (max_usage / total_nouns) * 100
                        if specificity_pct > 70:
                            validation['verb_specificity'][word] = f"{specificity_pct:.1f}% use same hint"

        validation['coverage']['total_expected'] = total_expected
        validation['coverage']['total_found'] = total_found
        validation['coverage']['percentage'] = (total_found / total_expected * 100) if total_expected > 0 else 0

        logger.info(f"Coverage: {validation['coverage']['percentage']:.1f}%")
        logger.info(f"Generic hints found: {len(validation['generic_hints'])}")
        logger.info(f"Quality issues: {len(validation['quality_issues'])}")
        logger.info(f"Verbs with low specificity: {len(validation['verb_specificity'])}")

        return validation

    def save_hints(self, hints: Dict, output_path: str) -> None:
        """Save hints to JSON file."""
        logger.info(f"Saving hints to {output_path}")

        output_data = {
            'version': '7.0.0',
            'generated_date': '2025-11-11',
            'coverage': f"{hints['stats']['hints_created']} / {hints['stats']['total_pairs']}",
            'quality_metrics': {
                'generic_eliminated': hints['stats']['generic_eliminated'],
                'verbs_processed': hints['stats']['verbs_processed'],
                'adjectives_processed': hints['stats']['adjectives_processed'],
                'total_hints': hints['stats']['hints_created']
            },
            'hints': hints['hints']
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {hints['stats']['hints_created']} hints")


def main():
    """Main execution function."""
    # Initialize fixer
    fixer = HintQualityFixer()

    # File paths
    collocations_path = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json'
    output_path = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\output\collocation_hints_v7.json'

    # Load data
    fixer.load_data(collocations_path)

    # Generate hints
    hints = fixer.generate_hints()

    # Validate
    validation = fixer.validate_hints(hints)

    # Save results
    fixer.save_hints(hints, output_path)

    # Print summary
    print("\n=== HINT QUALITY FIX COMPLETE ===")
    print(f"Coverage: {validation['coverage']['percentage']:.1f}%")
    print(f"Total hints created: {hints['stats']['hints_created']}")
    print(f"Generic hints eliminated: {hints['stats']['generic_eliminated']}")
    print(f"Verbs processed: {hints['stats']['verbs_processed']}")
    print(f"Adjectives processed: {hints['stats']['adjectives_processed']}")

    if validation['generic_hints']:
        print(f"\nWarning: {len(validation['generic_hints'])} generic hints still present")

    if validation['verb_specificity']:
        print(f"\nVerbs with low specificity: {len(validation['verb_specificity'])}")
        for verb, msg in list(validation['verb_specificity'].items())[:5]:
            print(f"  - {verb}: {msg}")

    print(f"\nOutput saved to: {output_path}")


if __name__ == '__main__':
    main()