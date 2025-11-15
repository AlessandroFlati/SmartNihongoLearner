#!/usr/bin/env python3
"""
Regenerate Verb-Specific Collocation Hints

This script generates highly specific collocation hints that describe the relationship
between each verb and its noun collocations. Instead of generic categories, it creates
hints that reflect HOW that specific verb relates to its objects.

Version: 4.0.0
Author: Claude Code
Date: 2025-11-11
"""

import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime
import os
import sys

# Fix Windows console encoding for Japanese characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class VerbSpecificHintGenerator:
    """
    Generates verb-specific collocation hints by analyzing semantic relationships
    between verbs and their noun collocations.

    Each verb gets unique hints that describe the nature of its relationship
    with the nouns it commonly pairs with.
    """

    def __init__(self, collocations_path: str):
        """
        Initialize the hint generator.

        Args:
            collocations_path: Path to collocations_complete.json file
        """
        self.collocations_path = collocations_path
        self.collocations_data = None
        self.verb_hints = {}
        self.hint_usage_stats = defaultdict(int)

    def load_collocations(self) -> None:
        """Load the collocations data from JSON file."""
        print(f"Loading collocations from: {self.collocations_path}")
        with open(self.collocations_path, 'r', encoding='utf-8') as f:
            self.collocations_data = json.load(f)
        print(f"Loaded {len(self.collocations_data['words'])} words")

    def _get_verb_specific_hints(self, verb: str, verb_data: Dict) -> Dict[str, List[Tuple[str, str]]]:
        """
        Generate verb-specific hints for a single verb.

        Returns a dictionary mapping hint phrases to lists of (noun, english) tuples.

        Args:
            verb: The verb word (e.g., "する", "のむ")
            verb_data: The verb's data from collocations

        Returns:
            Dictionary of {hint_phrase: [(noun, english), ...]}
        """
        verb_reading = verb_data.get('reading', '')
        verb_english = verb_data.get('english', '')
        nouns = verb_data.get('matches', {}).get('nouns', [])

        # This is where the magic happens - verb-specific hint generation
        hint_groups = self._create_semantic_groups(verb, verb_reading, verb_english, nouns)

        return hint_groups

    def _create_semantic_groups(self, verb: str, verb_reading: str, verb_english: str,
                                nouns: List[Dict]) -> Dict[str, List[Tuple[str, str]]]:
        """
        Create semantic groups specific to this verb's meaning and usage.

        This method contains the core logic for generating verb-specific hints.
        """
        hint_groups = defaultdict(list)

        # Extract noun information
        noun_list = [(n['word'], n.get('english', '').lower()) for n in nouns]

        # VERB-SPECIFIC HINT GENERATION
        # Each verb gets custom logic based on its meaning

        if verb == 'する':
            self._hints_suru(noun_list, hint_groups)
        elif verb == 'のむ' or verb == '飲む':
            self._hints_nomu(noun_list, hint_groups)
        elif verb == '食べる' or verb == 'たべる':
            self._hints_taberu(noun_list, hint_groups)
        elif verb == '行く' or verb == 'いく':
            self._hints_iku(noun_list, hint_groups)
        elif verb == 'いる' or verb == '居る':
            self._hints_iru(noun_list, hint_groups)
        elif verb == 'ある' or verb == '有る':
            self._hints_aru(noun_list, hint_groups)
        elif verb == '見る' or verb == 'みる':
            self._hints_miru(noun_list, hint_groups)
        elif verb == '買う' or verb == 'かう':
            self._hints_kau(noun_list, hint_groups)
        elif verb == '読む' or verb == 'よむ':
            self._hints_yomu(noun_list, hint_groups)
        elif verb == '書く' or verb == 'かく':
            self._hints_kaku(noun_list, hint_groups)
        elif verb == '聞く' or verb == 'きく':
            self._hints_kiku(noun_list, hint_groups)
        elif verb == '話す' or verb == 'はなす':
            self._hints_hanasu(noun_list, hint_groups)
        elif verb == '来る' or verb == 'くる':
            self._hints_kuru(noun_list, hint_groups)
        elif verb == '出る' or verb == 'でる':
            self._hints_deru(noun_list, hint_groups)
        elif verb == '入る' or verb == 'はいる':
            self._hints_hairu(noun_list, hint_groups)
        elif verb == '会う' or verb == 'あう':
            self._hints_au(noun_list, hint_groups)
        elif verb == '作る' or verb == 'つくる':
            self._hints_tsukuru(noun_list, hint_groups)
        elif verb == '使う' or verb == 'つかう':
            self._hints_tsukau(noun_list, hint_groups)
        elif verb == '持つ' or verb == 'もつ':
            self._hints_motsu(noun_list, hint_groups)
        elif verb == '思う' or verb == 'おもう':
            self._hints_omou(noun_list, hint_groups)
        elif verb == '知る' or verb == 'しる':
            self._hints_shiru(noun_list, hint_groups)
        elif verb == '待つ' or verb == 'まつ':
            self._hints_matsu(noun_list, hint_groups)
        elif verb == '立つ' or verb == 'たつ':
            self._hints_tatsu(noun_list, hint_groups)
        elif verb == '歩く' or verb == 'あるく':
            self._hints_aruku(noun_list, hint_groups)
        elif verb == '走る' or verb == 'はしる':
            self._hints_hashiru(noun_list, hint_groups)
        elif verb == '乗る' or verb == 'のる':
            self._hints_noru(noun_list, hint_groups)
        elif verb == '降りる' or verb == 'おりる':
            self._hints_oriru(noun_list, hint_groups)
        elif verb == '着る' or verb == 'きる':
            self._hints_kiru(noun_list, hint_groups)
        elif verb == '脱ぐ' or verb == 'ぬぐ':
            self._hints_nugu(noun_list, hint_groups)
        elif verb == '開ける' or verb == 'あける':
            self._hints_akeru(noun_list, hint_groups)
        elif verb == '閉める' or verb == 'しめる':
            self._hints_shimeru(noun_list, hint_groups)
        elif verb == '教える' or verb == 'おしえる':
            self._hints_oshieru(noun_list, hint_groups)
        elif verb == '習う' or verb == 'ならう':
            self._hints_narau(noun_list, hint_groups)
        elif verb == '借りる' or verb == 'かりる':
            self._hints_kariru(noun_list, hint_groups)
        elif verb == '貸す' or verb == 'かす':
            self._hints_kasu(noun_list, hint_groups)
        elif verb == '返す' or verb == 'かえす':
            self._hints_kaesu(noun_list, hint_groups)
        elif verb == '送る' or verb == 'おくる':
            self._hints_okuru(noun_list, hint_groups)
        elif verb == '受ける' or verb == 'うける':
            self._hints_ukeru(noun_list, hint_groups)
        elif verb == '始める' or verb == 'はじめる':
            self._hints_hajimeru(noun_list, hint_groups)
        elif verb == '終わる' or verb == 'おわる':
            self._hints_owaru(noun_list, hint_groups)
        elif verb == '止まる' or verb == 'とまる':
            self._hints_tomaru(noun_list, hint_groups)
        elif verb == '泊まる' or verb == 'とまる':
            self._hints_tomaru_stay(noun_list, hint_groups)
        elif verb == '住む' or verb == 'すむ':
            self._hints_sumu(noun_list, hint_groups)
        elif verb == '働く' or verb == 'はたらく':
            self._hints_hataraku(noun_list, hint_groups)
        elif verb == '休む' or verb == 'やすむ':
            self._hints_yasumu(noun_list, hint_groups)
        elif verb == '寝る' or verb == 'ねる':
            self._hints_neru(noun_list, hint_groups)
        elif verb == '起きる' or verb == 'おきる':
            self._hints_okiru(noun_list, hint_groups)
        elif verb == '座る' or verb == 'すわる':
            self._hints_suwaru(noun_list, hint_groups)
        elif verb == '立てる' or verb == 'たてる':
            self._hints_tateru(noun_list, hint_groups)
        elif verb == '置く' or verb == 'おく':
            self._hints_oku(noun_list, hint_groups)
        elif verb == '取る' or verb == 'とる':
            self._hints_toru(noun_list, hint_groups)
        elif verb == '渡す' or verb == 'わたす':
            self._hints_watasu(noun_list, hint_groups)
        elif verb == 'もらう':
            self._hints_morau(noun_list, hint_groups)
        elif verb == 'あげる':
            self._hints_ageru(noun_list, hint_groups)
        elif verb == 'くれる':
            self._hints_kureru(noun_list, hint_groups)
        else:
            # Generic fallback for verbs not specifically handled
            self._hints_generic(verb, verb_english, noun_list, hint_groups)

        return dict(hint_groups)

    # VERB-SPECIFIC HINT METHODS
    # Each method creates hints specific to how that verb relates to its objects

    def _hints_suru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for する (to do)."""
        for noun, english in nouns:
            if any(word in english for word in ['work', 'job', 'task', 'business', 'assignment', 'labor', 'labour']):
                groups['work and study'].append((noun, english))
            elif any(word in english for word in ['study', 'learning', 'research', 'investigation']):
                groups['work and study'].append((noun, english))
            elif any(word in english for word in ['cooking', 'cleaning', 'laundry', 'wash']):
                groups['household chores'].append((noun, english))
            elif any(word in english for word in ['exercise', 'sport', 'tennis', 'judo', 'swimming', 'practice', 'training']):
                groups['physical activities'].append((noun, english))
            elif any(word in english for word in ['talk', 'question', 'conversation', 'explanation', 'chat', 'consultation', 'greeting', 'introduction']):
                groups['communication acts'].append((noun, english))
            elif any(word in english for word in ['preparation', 'ready', 'arrange']):
                groups['preparations'].append((noun, english))
            elif any(word in english for word in ['marriage', 'wedding', 'graduation', 'admission', 'entrance', 'hospitalization', 'discharge']):
                groups['life milestones'].append((noun, english))
            elif any(word in english for word in ['shopping', 'errand', 'trip', 'travel', 'walk', 'stroll']):
                groups['errands and outings'].append((noun, english))
            elif any(word in english for word in ['plan', 'schedule', 'reservation', 'booking', 'meeting', 'conference']):
                groups['planning activities'].append((noun, english))
            elif any(word in english for word in ['test', 'exam', 'examination', 'match', 'game', 'competition', 'contest']):
                groups['competitions and tests'].append((noun, english))
            elif any(word in english for word in ['experience', 'attempt', 'try', 'failure', 'mistake']):
                groups['experiences'].append((noun, english))
            elif any(word in english for word in ['worry', 'concern', 'relief', 'attention', 'care', 'focus']):
                groups['mental states'].append((noun, english))
            elif any(word in english for word in ['invitation', 'hospitality', 'treat', 'courtesy', 'politeness', 'thanks', 'gratitude', 'celebration']):
                groups['social courtesies'].append((noun, english))
            elif any(word in english for word in ['use', 'usage', 'utilization', 'check', 'inspection']):
                groups['using and checking'].append((noun, english))
            elif any(word in english for word in ['import', 'export', 'trade', 'production', 'broadcast']):
                groups['business operations'].append((noun, english))
            elif any(word in english for word in ['fight', 'quarrel', 'argument', 'opposition', 'objection']):
                groups['conflicts'].append((noun, english))
            else:
                groups['various activities'].append((noun, english))

    def _hints_nomu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for のむ (to drink)."""
        for noun, english in nouns:
            if any(word in english for word in ['water', 'tea', 'coffee', 'juice', 'milk']):
                groups['common beverages'].append((noun, english))
            elif any(word in english for word in ['medicine', 'pill', 'tablet', 'drug', 'vitamin']):
                groups['medicine you swallow'].append((noun, english))
            elif any(word in english for word in ['alcohol', 'sake', 'beer', 'wine', 'liquor', 'drink']):
                groups['alcoholic drinks'].append((noun, english))
            elif any(word in english for word in ['soup', 'broth']):
                groups['liquid foods'].append((noun, english))
            else:
                groups['things you drink'].append((noun, english))

    def _hints_taberu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 食べる (to eat)."""
        for noun, english in nouns:
            if any(word in english for word in ['bread', 'rice', 'noodle', 'meal']):
                groups['staple foods'].append((noun, english))
            elif any(word in english for word in ['fish', 'meat', 'vegetable', 'egg']):
                groups['main ingredients'].append((noun, english))
            elif any(word in english for word in ['fruit', 'apple', 'banana', 'sweet', 'cake', 'candy', 'dessert']):
                groups['fruits and sweets'].append((noun, english))
            elif any(word in english for word in ['breakfast', 'lunch', 'dinner', 'supper']):
                groups['daily meals'].append((noun, english))
            elif any(word in english for word in ['sushi', 'tempura', 'ramen', 'udon', 'soba']):
                groups['japanese dishes'].append((noun, english))
            else:
                groups['foods you eat'].append((noun, english))

    def _hints_iku(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 行く (to go)."""
        for noun, english in nouns:
            if any(word in english for word in ['school', 'university', 'college', 'library', 'class']):
                groups['study destinations'].append((noun, english))
            elif any(word in english for word in ['company', 'office', 'bank', 'post', 'shop', 'store']):
                groups['work and errands'].append((noun, english))
            elif any(word in english for word in ['sea', 'beach', 'mountain', 'park', 'garden']):
                groups['leisure spots'].append((noun, english))
            elif any(word in english for word in ['hospital', 'doctor', 'clinic', 'pharmacy']):
                groups['health facilities'].append((noun, english))
            elif any(word in english for word in ['station', 'airport', 'bus', 'train']):
                groups['transportation hubs'].append((noun, english))
            elif any(word in english for word in ['restaurant', 'cafe', 'bar']):
                groups['eating places'].append((noun, english))
            elif any(word in english for word in ['home', 'house', 'room', 'place']):
                groups['home and rooms'].append((noun, english))
            elif any(word in english for word in ['country', 'abroad', 'foreign', 'overseas', 'america', 'japan']):
                groups['countries and abroad'].append((noun, english))
            elif any(word in english for word in ['movie', 'theater', 'cinema', 'concert']):
                groups['entertainment venues'].append((noun, english))
            elif any(word in english for word in ['bathroom', 'toilet', 'restroom']):
                groups['facilities to use'].append((noun, english))
            else:
                groups['places you visit'].append((noun, english))

    def _hints_iru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for いる (to be/exist - animate)."""
        for noun, english in nouns:
            if any(word in english for word in ['mother', 'father', 'parent', 'child', 'son', 'daughter', 'brother', 'sister', 'family', 'grandfather', 'grandmother']):
                groups['family members'].append((noun, english))
            elif any(word in english for word in ['teacher', 'student', 'pupil', 'professor']):
                groups['people at school'].append((noun, english))
            elif any(word in english for word in ['president', 'manager', 'director', 'boss', 'employee', 'staff']):
                groups['company positions'].append((noun, english))
            elif any(word in english for word in ['friend', 'lover', 'boyfriend', 'girlfriend', 'companion']):
                groups['close relationships'].append((noun, english))
            elif any(word in english for word in ['doctor', 'nurse', 'patient']):
                groups['medical people'].append((noun, english))
            elif any(word in english for word in ['home', 'house', 'room', 'school', 'company', 'place']):
                groups['where people are'].append((noun, english))
            elif any(word in english for word in ['man', 'woman', 'boy', 'girl', 'person', 'people', 'baby', 'adult']):
                groups['types of people'].append((noun, english))
            elif any(word in english for word in ['cat', 'dog', 'animal', 'bird', 'pet']):
                groups['animals and pets'].append((noun, english))
            else:
                groups['living beings'].append((noun, english))

    def _hints_aru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for ある (to exist - inanimate)."""
        for noun, english in nouns:
            if any(word in english for word in ['time', 'leisure', 'free', 'spare']):
                groups['available time'].append((noun, english))
            elif any(word in english for word in ['reason', 'cause', 'excuse']):
                groups['causes and reasons'].append((noun, english))
            elif any(word in english for word in ['problem', 'question', 'trouble', 'difficulty', 'issue']):
                groups['issues to solve'].append((noun, english))
            elif any(word in english for word in ['shop', 'store', 'bank', 'post', 'restaurant', 'hospital', 'school']):
                groups['useful places'].append((noun, english))
            elif any(word in english for word in ['desk', 'chair', 'table', 'bed', 'book', 'pen', 'paper']):
                groups['objects in rooms'].append((noun, english))
            elif any(word in english for word in ['interest', 'hobby', 'concern']):
                groups['interests and hobbies'].append((noun, english))
            elif any(word in english for word in ['money', 'yen', 'dollar', 'cash']):
                groups['money you have'].append((noun, english))
            elif any(word in english for word in ['appointment', 'plan', 'schedule', 'meeting']):
                groups['plans and appointments'].append((noun, english))
            elif any(word in english for word in ['meaning', 'significance', 'value', 'importance']):
                groups['meaning and value'].append((noun, english))
            elif any(word in english for word in ['difference', 'distinction', 'gap']):
                groups['differences'].append((noun, english))
            elif any(word in english for word in ['relationship', 'connection', 'relation']):
                groups['connections'].append((noun, english))
            else:
                groups['things that exist'].append((noun, english))

    def _hints_miru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 見る (to see/watch)."""
        for noun, english in nouns:
            if any(word in english for word in ['tv', 'television', 'movie', 'film', 'program', 'show', 'video']):
                groups['entertainment to watch'].append((noun, english))
            elif any(word in english for word in ['sea', 'ocean', 'mountain', 'sky', 'star', 'moon', 'scenery', 'view']):
                groups['natural scenery'].append((noun, english))
            elif any(word in english for word in ['match', 'game', 'sport', 'competition']):
                groups['live events'].append((noun, english))
            elif any(word in english for word in ['book', 'newspaper', 'magazine', 'letter', 'document']):
                groups['things to read'].append((noun, english))
            elif any(word in english for word in ['dream', 'nightmare']):
                groups['dreams you have'].append((noun, english))
            elif any(word in english for word in ['doctor', 'dentist']):
                groups['medical checkups'].append((noun, english))
            elif any(word in english for word in ['picture', 'photo', 'image', 'painting']):
                groups['visual art'].append((noun, english))
            else:
                groups['things you observe'].append((noun, english))

    def _hints_kau(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 買う (to buy)."""
        for noun, english in nouns:
            if any(word in english for word in ['clothes', 'shirt', 'shoes', 'hat', 'jacket', 'dress', 'pants']):
                groups['clothing items'].append((noun, english))
            elif any(word in english for word in ['book', 'magazine', 'newspaper', 'dictionary']):
                groups['reading materials'].append((noun, english))
            elif any(word in english for word in ['food', 'vegetable', 'meat', 'fish', 'fruit', 'bread', 'rice']):
                groups['groceries'].append((noun, english))
            elif any(word in english for word in ['car', 'house', 'apartment', 'land']):
                groups['expensive purchases'].append((noun, english))
            elif any(word in english for word in ['present', 'gift', 'flower', 'souvenir']):
                groups['gifts for others'].append((noun, english))
            elif any(word in english for word in ['ticket', 'stamp']):
                groups['tickets and stamps'].append((noun, english))
            elif any(word in english for word in ['camera', 'computer', 'phone', 'watch']):
                groups['electronics and gadgets'].append((noun, english))
            else:
                groups['things to purchase'].append((noun, english))

    def _hints_yomu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 読む (to read)."""
        for noun, english in nouns:
            if any(word in english for word in ['book', 'novel', 'story', 'textbook']):
                groups['books to read'].append((noun, english))
            elif any(word in english for word in ['newspaper', 'article', 'news']):
                groups['news and articles'].append((noun, english))
            elif any(word in english for word in ['magazine', 'comic', 'manga']):
                groups['magazines and comics'].append((noun, english))
            elif any(word in english for word in ['letter', 'mail', 'email', 'message']):
                groups['correspondence'].append((noun, english))
            elif any(word in english for word in ['document', 'report', 'paper']):
                groups['documents and reports'].append((noun, english))
            elif any(word in english for word in ['poem', 'poetry']):
                groups['poetry'].append((noun, english))
            else:
                groups['written materials'].append((noun, english))

    def _hints_kaku(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 書く (to write)."""
        for noun, english in nouns:
            if any(word in english for word in ['letter', 'mail', 'email', 'card', 'postcard']):
                groups['correspondence'].append((noun, english))
            elif any(word in english for word in ['name', 'address', 'phone', 'number']):
                groups['personal information'].append((noun, english))
            elif any(word in english for word in ['report', 'paper', 'thesis', 'essay']):
                groups['academic writing'].append((noun, english))
            elif any(word in english for word in ['diary', 'journal', 'blog']):
                groups['personal journals'].append((noun, english))
            elif any(word in english for word in ['novel', 'story', 'book', 'poem']):
                groups['creative writing'].append((noun, english))
            elif any(word in english for word in ['character', 'kanji', 'hiragana', 'katakana']):
                groups['characters to write'].append((noun, english))
            else:
                groups['things you write'].append((noun, english))

    def _hints_kiku(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 聞く (to listen/hear/ask)."""
        for noun, english in nouns:
            if any(word in english for word in ['music', 'song', 'melody']):
                groups['music to enjoy'].append((noun, english))
            elif any(word in english for word in ['radio', 'podcast', 'broadcast']):
                groups['audio programs'].append((noun, english))
            elif any(word in english for word in ['story', 'tale', 'talk', 'speech']):
                groups['spoken stories'].append((noun, english))
            elif any(word in english for word in ['news', 'information', 'report']):
                groups['news and info'].append((noun, english))
            elif any(word in english for word in ['question', 'inquiry']):
                groups['questions you ask'].append((noun, english))
            elif any(word in english for word in ['voice', 'sound', 'noise']):
                groups['sounds you hear'].append((noun, english))
            elif any(word in english for word in ['opinion', 'advice', 'suggestion']):
                groups['advice and opinions'].append((noun, english))
            elif any(word in english for word in ['teacher', 'parent', 'friend', 'person']):
                groups['people you ask'].append((noun, english))
            else:
                groups['things you hear'].append((noun, english))

    def _hints_hanasu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 話す (to speak/talk)."""
        for noun, english in nouns:
            if any(word in english for word in ['japanese', 'english', 'chinese', 'language', 'french', 'spanish']):
                groups['languages you speak'].append((noun, english))
            elif any(word in english for word in ['story', 'tale', 'experience']):
                groups['stories you tell'].append((noun, english))
            elif any(word in english for word in ['truth', 'lie', 'secret']):
                groups['what you reveal'].append((noun, english))
            elif any(word in english for word in ['teacher', 'friend', 'parent', 'person', 'doctor']):
                groups['people you talk to'].append((noun, english))
            elif any(word in english for word in ['phone', 'telephone']):
                groups['phone conversations'].append((noun, english))
            else:
                groups['topics you discuss'].append((noun, english))

    def _hints_kuru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 来る (to come)."""
        for noun, english in nouns:
            if any(word in english for word in ['home', 'house', 'room', 'place']):
                groups['destinations arriving'].append((noun, english))
            elif any(word in english for word in ['school', 'company', 'office']):
                groups['work and study'].append((noun, english))
            elif any(word in english for word in ['japan', 'country', 'city', 'town']):
                groups['places and countries'].append((noun, english))
            elif any(word in english for word in ['friend', 'person', 'guest', 'visitor']):
                groups['people arriving'].append((noun, english))
            elif any(word in english for word in ['spring', 'summer', 'winter', 'fall', 'season']):
                groups['seasons arriving'].append((noun, english))
            elif any(word in english for word in ['time', 'moment', 'day']):
                groups['time arriving'].append((noun, english))
            else:
                groups['things approaching'].append((noun, english))

    def _hints_deru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 出る (to exit/leave/appear)."""
        for noun, english in nouns:
            if any(word in english for word in ['home', 'house', 'room', 'building']):
                groups['places you exit'].append((noun, english))
            elif any(word in english for word in ['university', 'school', 'college']):
                groups['graduating from'].append((noun, english))
            elif any(word in english for word in ['station', 'exit', 'entrance']):
                groups['exit points'].append((noun, english))
            elif any(word in english for word in ['outside', 'outdoors']):
                groups['going outdoors'].append((noun, english))
            elif any(word in english for word in ['test', 'exam', 'question']):
                groups['appearing on tests'].append((noun, english))
            elif any(word in english for word in ['tv', 'show', 'program', 'movie']):
                groups['appearing in media'].append((noun, english))
            else:
                groups['emerging from'].append((noun, english))

    def _hints_hairu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 入る (to enter)."""
        for noun, english in nouns:
            if any(word in english for word in ['room', 'house', 'home', 'building']):
                groups['rooms to enter'].append((noun, english))
            elif any(word in english for word in ['university', 'school', 'college', 'company']):
                groups['enrolling in'].append((noun, english))
            elif any(word in english for word in ['bath', 'shower', 'hot spring', 'onsen']):
                groups['bathing'].append((noun, english))
            elif any(word in english for word in ['hospital', 'clinic']):
                groups['hospitalization'].append((noun, english))
            elif any(word in english for word in ['shop', 'store', 'restaurant', 'cafe']):
                groups['establishments'].append((noun, english))
            else:
                groups['entering places'].append((noun, english))

    def _hints_au(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 会う (to meet)."""
        for noun, english in nouns:
            if any(word in english for word in ['friend', 'companion', 'acquaintance']):
                groups['friends you meet'].append((noun, english))
            elif any(word in english for word in ['family', 'mother', 'father', 'parent', 'brother', 'sister']):
                groups['family gatherings'].append((noun, english))
            elif any(word in english for word in ['teacher', 'professor', 'doctor']):
                groups['professionals'].append((noun, english))
            elif any(word in english for word in ['lover', 'boyfriend', 'girlfriend']):
                groups['romantic meetings'].append((noun, english))
            elif any(word in english for word in ['person', 'people', 'someone']):
                groups['various people'].append((noun, english))
            elif any(word in english for word in ['accident', 'trouble', 'problem']):
                groups['encountering problems'].append((noun, english))
            else:
                groups['encounters'].append((noun, english))

    def _hints_tsukuru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 作る (to make/create)."""
        for noun, english in nouns:
            if any(word in english for word in ['food', 'dish', 'meal', 'cooking', 'cuisine', 'rice', 'bread']):
                groups['dishes to cook'].append((noun, english))
            elif any(word in english for word in ['friend', 'companion', 'relationship']):
                groups['relationships formed'].append((noun, english))
            elif any(word in english for word in ['plan', 'schedule', 'program']):
                groups['plans you create'].append((noun, english))
            elif any(word in english for word in ['art', 'work', 'piece', 'product']):
                groups['creative works'].append((noun, english))
            elif any(word in english for word in ['company', 'organization', 'group', 'club']):
                groups['organizations founded'].append((noun, english))
            elif any(word in english for word in ['time', 'opportunity', 'chance']):
                groups['making time'].append((noun, english))
            else:
                groups['things you create'].append((noun, english))

    def _hints_tsukau(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 使う (to use)."""
        for noun, english in nouns:
            if any(word in english for word in ['computer', 'phone', 'camera', 'machine', 'device']):
                groups['electronic devices'].append((noun, english))
            elif any(word in english for word in ['japanese', 'english', 'language', 'word']):
                groups['languages in use'].append((noun, english))
            elif any(word in english for word in ['money', 'yen', 'dollar', 'cash']):
                groups['spending money'].append((noun, english))
            elif any(word in english for word in ['time', 'hour', 'minute']):
                groups['spending time'].append((noun, english))
            elif any(word in english for word in ['chopstick', 'fork', 'knife', 'tool']):
                groups['utensils and tools'].append((noun, english))
            elif any(word in english for word in ['head', 'brain', 'mind']):
                groups['using your mind'].append((noun, english))
            else:
                groups['things you utilize'].append((noun, english))

    def _hints_motsu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 持つ (to hold/have)."""
        for noun, english in nouns:
            if any(word in english for word in ['bag', 'umbrella', 'luggage', 'package']):
                groups['items you carry'].append((noun, english))
            elif any(word in english for word in ['money', 'cash', 'card', 'ticket']):
                groups['valuables kept'].append((noun, english))
            elif any(word in english for word in ['phone', 'camera', 'pen', 'book']):
                groups['everyday items'].append((noun, english))
            elif any(word in english for word in ['interest', 'concern', 'feeling', 'opinion']):
                groups['feelings you have'].append((noun, english))
            elif any(word in english for word in ['ability', 'power', 'strength', 'skill']):
                groups['abilities possessed'].append((noun, english))
            elif any(word in english for word in ['problem', 'trouble', 'worry']):
                groups['problems you face'].append((noun, english))
            else:
                groups['things you possess'].append((noun, english))

    def _hints_omou(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 思う (to think)."""
        for noun, english in nouns:
            if any(word in english for word in ['thing', 'matter', 'fact', 'idea', 'thought']):
                groups['thoughts you have'].append((noun, english))
            elif any(word in english for word in ['friend', 'person', 'family', 'lover']):
                groups['people you think about'].append((noun, english))
            elif any(word in english for word in ['future', 'past', 'tomorrow', 'yesterday']):
                groups['time periods'].append((noun, english))
            elif any(word in english for word in ['reason', 'cause', 'why']):
                groups['reasons pondered'].append((noun, english))
            else:
                groups['subjects of thought'].append((noun, english))

    def _hints_shiru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 知る (to know)."""
        for noun, english in nouns:
            if any(word in english for word in ['person', 'people', 'friend', 'name']):
                groups['people you know'].append((noun, english))
            elif any(word in english for word in ['fact', 'truth', 'information', 'news', 'story']):
                groups['facts you learn'].append((noun, english))
            elif any(word in english for word in ['address', 'phone', 'number', 'place', 'location']):
                groups['information known'].append((noun, english))
            elif any(word in english for word in ['way', 'method', 'how']):
                groups['methods understood'].append((noun, english))
            elif any(word in english for word in ['word', 'meaning', 'language']):
                groups['vocabulary known'].append((noun, english))
            else:
                groups['knowledge possessed'].append((noun, english))

    def _hints_matsu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 待つ (to wait)."""
        for noun, english in nouns:
            if any(word in english for word in ['friend', 'person', 'people', 'lover', 'family']):
                groups['people you wait for'].append((noun, english))
            elif any(word in english for word in ['bus', 'train', 'taxi', 'elevator']):
                groups['transportation'].append((noun, english))
            elif any(word in english for word in ['time', 'moment', 'day', 'chance', 'opportunity']):
                groups['waiting for timing'].append((noun, english))
            elif any(word in english for word in ['result', 'answer', 'reply', 'response']):
                groups['awaiting results'].append((noun, english))
            else:
                groups['things awaited'].append((noun, english))

    def _hints_tatsu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 立つ (to stand)."""
        for noun, english in nouns:
            if any(word in english for word in ['place', 'spot', 'position']):
                groups['where you stand'].append((noun, english))
            elif any(word in english for word in ['front', 'before', 'ahead']):
                groups['standing before'].append((noun, english))
            elif any(word in english for word in ['line', 'queue', 'row']):
                groups['standing in line'].append((noun, english))
            else:
                groups['standing positions'].append((noun, english))

    def _hints_aruku(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 歩く (to walk)."""
        for noun, english in nouns:
            if any(word in english for word in ['road', 'street', 'path', 'way']):
                groups['paths you walk'].append((noun, english))
            elif any(word in english for word in ['town', 'city', 'park', 'place']):
                groups['areas to explore'].append((noun, english))
            elif any(word in english for word in ['minute', 'hour', 'time']):
                groups['walking duration'].append((noun, english))
            else:
                groups['walking routes'].append((noun, english))

    def _hints_hashiru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 走る (to run)."""
        for noun, english in nouns:
            if any(word in english for word in ['road', 'street', 'track', 'path']):
                groups['running surfaces'].append((noun, english))
            elif any(word in english for word in ['car', 'train', 'vehicle']):
                groups['vehicles moving'].append((noun, english))
            elif any(word in english for word in ['park', 'field', 'ground']):
                groups['running locations'].append((noun, english))
            elif any(word in english for word in ['marathon', 'race', 'competition']):
                groups['running events'].append((noun, english))
            else:
                groups['running contexts'].append((noun, english))

    def _hints_noru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 乗る (to ride/board)."""
        for noun, english in nouns:
            if any(word in english for word in ['train', 'subway', 'rail']):
                groups['trains and rails'].append((noun, english))
            elif any(word in english for word in ['bus', 'taxi', 'car', 'vehicle']):
                groups['road vehicles'].append((noun, english))
            elif any(word in english for word in ['airplane', 'plane', 'flight']):
                groups['air travel'].append((noun, english))
            elif any(word in english for word in ['ship', 'boat', 'ferry']):
                groups['water transport'].append((noun, english))
            elif any(word in english for word in ['bicycle', 'bike', 'motorcycle']):
                groups['two-wheeled rides'].append((noun, english))
            elif any(word in english for word in ['horse', 'animal']):
                groups['animals to ride'].append((noun, english))
            else:
                groups['things you board'].append((noun, english))

    def _hints_oriru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 降りる (to get off/descend)."""
        for noun, english in nouns:
            if any(word in english for word in ['train', 'subway', 'bus', 'taxi', 'car']):
                groups['exiting vehicles'].append((noun, english))
            elif any(word in english for word in ['station', 'stop']):
                groups['exit points'].append((noun, english))
            elif any(word in english for word in ['mountain', 'stairs', 'hill']):
                groups['descending from'].append((noun, english))
            else:
                groups['disembarking from'].append((noun, english))

    def _hints_kiru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 着る (to wear)."""
        for noun, english in nouns:
            if any(word in english for word in ['clothes', 'clothing', 'shirt', 'jacket', 'coat', 'dress', 'suit']):
                groups['upper body wear'].append((noun, english))
            elif any(word in english for word in ['kimono', 'yukata']):
                groups['traditional clothing'].append((noun, english))
            elif any(word in english for word in ['uniform', 'suit']):
                groups['formal attire'].append((noun, english))
            else:
                groups['garments worn'].append((noun, english))

    def _hints_nugu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 脱ぐ (to take off)."""
        for noun, english in nouns:
            if any(word in english for word in ['clothes', 'shirt', 'jacket', 'coat']):
                groups['clothing removed'].append((noun, english))
            elif any(word in english for word in ['shoes', 'socks', 'boots']):
                groups['footwear removed'].append((noun, english))
            elif any(word in english for word in ['hat', 'cap', 'glasses']):
                groups['accessories removed'].append((noun, english))
            else:
                groups['items taken off'].append((noun, english))

    def _hints_akeru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 開ける (to open)."""
        for noun, english in nouns:
            if any(word in english for word in ['door', 'gate', 'entrance']):
                groups['doors and gates'].append((noun, english))
            elif any(word in english for word in ['window']):
                groups['windows'].append((noun, english))
            elif any(word in english for word in ['box', 'package', 'container', 'bag']):
                groups['containers'].append((noun, english))
            elif any(word in english for word in ['eye', 'eyes']):
                groups['your eyes'].append((noun, english))
            elif any(word in english for word in ['mouth']):
                groups['your mouth'].append((noun, english))
            elif any(word in english for word in ['book', 'page']):
                groups['books opened'].append((noun, english))
            else:
                groups['things you open'].append((noun, english))

    def _hints_shimeru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 閉める (to close)."""
        for noun, english in nouns:
            if any(word in english for word in ['door', 'gate']):
                groups['doors and gates'].append((noun, english))
            elif any(word in english for word in ['window']):
                groups['windows'].append((noun, english))
            elif any(word in english for word in ['eye', 'eyes']):
                groups['your eyes'].append((noun, english))
            elif any(word in english for word in ['mouth']):
                groups['your mouth'].append((noun, english))
            elif any(word in english for word in ['shop', 'store', 'restaurant']):
                groups['closing businesses'].append((noun, english))
            else:
                groups['things you close'].append((noun, english))

    def _hints_oshieru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 教える (to teach/tell)."""
        for noun, english in nouns:
            if any(word in english for word in ['japanese', 'english', 'language', 'chinese']):
                groups['languages taught'].append((noun, english))
            elif any(word in english for word in ['math', 'science', 'history', 'subject']):
                groups['school subjects'].append((noun, english))
            elif any(word in english for word in ['way', 'method', 'how']):
                groups['methods explained'].append((noun, english))
            elif any(word in english for word in ['address', 'phone', 'number', 'place', 'location']):
                groups['information shared'].append((noun, english))
            elif any(word in english for word in ['student', 'child', 'person']):
                groups['students taught'].append((noun, english))
            else:
                groups['knowledge conveyed'].append((noun, english))

    def _hints_narau(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 習う (to learn)."""
        for noun, english in nouns:
            if any(word in english for word in ['japanese', 'english', 'language', 'chinese']):
                groups['languages learned'].append((noun, english))
            elif any(word in english for word in ['piano', 'guitar', 'music', 'instrument']):
                groups['musical instruments'].append((noun, english))
            elif any(word in english for word in ['dance', 'dancing', 'ballet']):
                groups['dance and movement'].append((noun, english))
            elif any(word in english for word in ['cooking', 'cuisine']):
                groups['culinary skills'].append((noun, english))
            elif any(word in english for word in ['art', 'painting', 'drawing']):
                groups['artistic skills'].append((noun, english))
            elif any(word in english for word in ['martial', 'judo', 'karate']):
                groups['martial arts'].append((noun, english))
            else:
                groups['skills acquired'].append((noun, english))

    def _hints_kariru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 借りる (to borrow)."""
        for noun, english in nouns:
            if any(word in english for word in ['book', 'dictionary', 'magazine']):
                groups['library materials'].append((noun, english))
            elif any(word in english for word in ['money', 'yen', 'dollar', 'cash']):
                groups['money borrowed'].append((noun, english))
            elif any(word in english for word in ['room', 'house', 'apartment']):
                groups['places rented'].append((noun, english))
            elif any(word in english for word in ['pen', 'pencil', 'eraser', 'tool']):
                groups['items borrowed'].append((noun, english))
            elif any(word in english for word in ['video', 'dvd', 'cd', 'movie']):
                groups['media borrowed'].append((noun, english))
            else:
                groups['things borrowed'].append((noun, english))

    def _hints_kasu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 貸す (to lend)."""
        for noun, english in nouns:
            if any(word in english for word in ['book', 'dictionary', 'magazine']):
                groups['reading materials'].append((noun, english))
            elif any(word in english for word in ['money', 'yen', 'dollar', 'cash']):
                groups['money lent'].append((noun, english))
            elif any(word in english for word in ['room', 'house', 'apartment']):
                groups['properties rented'].append((noun, english))
            elif any(word in english for word in ['pen', 'pencil', 'eraser', 'tool']):
                groups['items lent'].append((noun, english))
            else:
                groups['things lent'].append((noun, english))

    def _hints_kaesu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 返す (to return)."""
        for noun, english in nouns:
            if any(word in english for word in ['book', 'dictionary', 'magazine']):
                groups['library returns'].append((noun, english))
            elif any(word in english for word in ['money', 'yen', 'dollar', 'cash', 'change']):
                groups['money returned'].append((noun, english))
            elif any(word in english for word in ['letter', 'email', 'message', 'reply', 'answer']):
                groups['responses sent'].append((noun, english))
            elif any(word in english for word in ['item', 'thing', 'product']):
                groups['items returned'].append((noun, english))
            else:
                groups['things returned'].append((noun, english))

    def _hints_okuru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 送る (to send)."""
        for noun, english in nouns:
            if any(word in english for word in ['letter', 'mail', 'postcard', 'card']):
                groups['mail sent'].append((noun, english))
            elif any(word in english for word in ['email', 'message', 'text']):
                groups['digital messages'].append((noun, english))
            elif any(word in english for word in ['present', 'gift', 'flower']):
                groups['gifts sent'].append((noun, english))
            elif any(word in english for word in ['package', 'parcel', 'box']):
                groups['packages shipped'].append((noun, english))
            elif any(word in english for word in ['person', 'friend', 'family']):
                groups['escorting people'].append((noun, english))
            elif any(word in english for word in ['life', 'time', 'day']):
                groups['spending time'].append((noun, english))
            else:
                groups['things dispatched'].append((noun, english))

    def _hints_ukeru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 受ける (to receive/take)."""
        for noun, english in nouns:
            if any(word in english for word in ['test', 'exam', 'examination']):
                groups['exams taken'].append((noun, english))
            elif any(word in english for word in ['interview', 'audit']):
                groups['interviews attended'].append((noun, english))
            elif any(word in english for word in ['treatment', 'operation', 'surgery', 'medical']):
                groups['medical procedures'].append((noun, english))
            elif any(word in english for word in ['damage', 'injury', 'harm', 'influence', 'impact']):
                groups['effects received'].append((noun, english))
            elif any(word in english for word in ['lesson', 'class', 'instruction']):
                groups['instruction received'].append((noun, english))
            else:
                groups['things received'].append((noun, english))

    def _hints_hajimeru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 始める (to begin)."""
        for noun, english in nouns:
            if any(word in english for word in ['work', 'job', 'business']):
                groups['work begun'].append((noun, english))
            elif any(word in english for word in ['study', 'learning', 'practice']):
                groups['studies started'].append((noun, english))
            elif any(word in english for word in ['life', 'living']):
                groups['new life phases'].append((noun, english))
            elif any(word in english for word in ['talk', 'speech', 'conversation']):
                groups['conversations started'].append((noun, english))
            elif any(word in english for word in ['preparation', 'ready']):
                groups['preparations begun'].append((noun, english))
            else:
                groups['activities initiated'].append((noun, english))

    def _hints_owaru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 終わる (to end/finish)."""
        for noun, english in nouns:
            if any(word in english for word in ['work', 'job', 'task']):
                groups['work completed'].append((noun, english))
            elif any(word in english for word in ['class', 'lesson', 'school']):
                groups['classes ending'].append((noun, english))
            elif any(word in english for word in ['meeting', 'conference']):
                groups['meetings concluded'].append((noun, english))
            elif any(word in english for word in ['war', 'fight', 'battle']):
                groups['conflicts ending'].append((noun, english))
            elif any(word in english for word in ['life', 'era', 'period']):
                groups['periods concluding'].append((noun, english))
            else:
                groups['things finishing'].append((noun, english))

    def _hints_tomaru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 止まる (to stop)."""
        for noun, english in nouns:
            if any(word in english for word in ['car', 'train', 'bus', 'vehicle', 'taxi']):
                groups['vehicles stopping'].append((noun, english))
            elif any(word in english for word in ['rain', 'snow', 'wind', 'storm']):
                groups['weather ceasing'].append((noun, english))
            elif any(word in english for word in ['clock', 'watch', 'time']):
                groups['time stopping'].append((noun, english))
            elif any(word in english for word in ['heart', 'breath']):
                groups['bodily functions'].append((noun, english))
            else:
                groups['things stopping'].append((noun, english))

    def _hints_tomaru_stay(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 泊まる (to stay overnight)."""
        for noun, english in nouns:
            if any(word in english for word in ['hotel', 'inn', 'motel', 'lodge']):
                groups['accommodations'].append((noun, english))
            elif any(word in english for word in ['friend', 'house', 'home', 'place']):
                groups['staying with others'].append((noun, english))
            elif any(word in english for word in ['ryokan', 'hostel']):
                groups['traditional lodging'].append((noun, english))
            else:
                groups['overnight stays'].append((noun, english))

    def _hints_sumu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 住む (to live/reside)."""
        for noun, english in nouns:
            if any(word in english for word in ['house', 'home', 'apartment', 'condominium']):
                groups['types of housing'].append((noun, english))
            elif any(word in english for word in ['tokyo', 'japan', 'country', 'city', 'town']):
                groups['locations lived'].append((noun, english))
            elif any(word in english for word in ['place', 'area', 'region']):
                groups['residential areas'].append((noun, english))
            else:
                groups['places of residence'].append((noun, english))

    def _hints_hataraku(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 働く (to work)."""
        for noun, english in nouns:
            if any(word in english for word in ['company', 'firm', 'corporation']):
                groups['companies'].append((noun, english))
            elif any(word in english for word in ['bank', 'hospital', 'school', 'university']):
                groups['institutions'].append((noun, english))
            elif any(word in english for word in ['factory', 'plant', 'office']):
                groups['workplaces'].append((noun, english))
            elif any(word in english for word in ['foreign', 'abroad', 'overseas', 'country']):
                groups['working abroad'].append((noun, english))
            else:
                groups['employment places'].append((noun, english))

    def _hints_yasumu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 休む (to rest)."""
        for noun, english in nouns:
            if any(word in english for word in ['school', 'class', 'lesson']):
                groups['absences from school'].append((noun, english))
            elif any(word in english for word in ['work', 'job', 'company']):
                groups['time off work'].append((noun, english))
            elif any(word in english for word in ['body', 'health']):
                groups['physical rest'].append((noun, english))
            elif any(word in english for word in ['day', 'week', 'weekend']):
                groups['rest periods'].append((noun, english))
            else:
                groups['taking breaks'].append((noun, english))

    def _hints_neru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 寝る (to sleep)."""
        for noun, english in nouns:
            if any(word in english for word in ['bed', 'futon']):
                groups['sleeping places'].append((noun, english))
            elif any(word in english for word in ['night', 'evening', 'time']):
                groups['sleep times'].append((noun, english))
            elif any(word in english for word in ['room', 'bedroom']):
                groups['sleeping rooms'].append((noun, english))
            elif any(word in english for word in ['hour', 'minute']):
                groups['sleep duration'].append((noun, english))
            else:
                groups['sleep contexts'].append((noun, english))

    def _hints_okiru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 起きる (to wake up/get up)."""
        for noun, english in nouns:
            if any(word in english for word in ['morning', 'dawn', 'early']):
                groups['wake-up times'].append((noun, english))
            elif any(word in english for word in ['time', 'hour', "o'clock"]):
                groups['specific times'].append((noun, english))
            elif any(word in english for word in ['accident', 'problem', 'incident', 'event', 'earthquake']):
                groups['incidents occurring'].append((noun, english))
            elif any(word in english for word in ['bed', 'futon']):
                groups['getting out of bed'].append((noun, english))
            else:
                groups['waking contexts'].append((noun, english))

    def _hints_suwaru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 座る (to sit)."""
        for noun, english in nouns:
            if any(word in english for word in ['chair', 'seat', 'bench']):
                groups['seats'].append((noun, english))
            elif any(word in english for word in ['floor', 'ground', 'tatami']):
                groups['floor seating'].append((noun, english))
            elif any(word in english for word in ['desk', 'table']):
                groups['at furniture'].append((noun, english))
            elif any(word in english for word in ['place', 'spot', 'position']):
                groups['sitting locations'].append((noun, english))
            else:
                groups['places to sit'].append((noun, english))

    def _hints_tateru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 立てる (to stand up/erect)."""
        for noun, english in nouns:
            if any(word in english for word in ['plan', 'strategy', 'scheme']):
                groups['plans formulated'].append((noun, english))
            elif any(word in english for word in ['sound', 'noise', 'voice']):
                groups['sounds made'].append((noun, english))
            elif any(word in english for word in ['flag', 'sign', 'pole']):
                groups['objects erected'].append((noun, english))
            elif any(word in english for word in ['building', 'house', 'structure']):
                groups['structures built'].append((noun, english))
            else:
                groups['things erected'].append((noun, english))

    def _hints_oku(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 置く (to place/put)."""
        for noun, english in nouns:
            if any(word in english for word in ['table', 'desk', 'shelf']):
                groups['on furniture'].append((noun, english))
            elif any(word in english for word in ['bag', 'luggage', 'package']):
                groups['items placed'].append((noun, english))
            elif any(word in english for word in ['book', 'paper', 'document']):
                groups['documents set down'].append((noun, english))
            elif any(word in english for word in ['place', 'spot', 'location', 'here', 'there']):
                groups['placement locations'].append((noun, english))
            else:
                groups['things positioned'].append((noun, english))

    def _hints_toru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 取る (to take)."""
        for noun, english in nouns:
            if any(word in english for word in ['photo', 'picture', 'photograph']):
                groups['photos taken'].append((noun, english))
            elif any(word in english for word in ['rest', 'break', 'vacation', 'holiday']):
                groups['breaks taken'].append((noun, english))
            elif any(word in english for word in ['contact', 'communication', 'touch']):
                groups['making contact'].append((noun, english))
            elif any(word in english for word in ['age', 'year', 'old']):
                groups['aging'].append((noun, english))
            elif any(word in english for word in ['meal', 'food', 'breakfast', 'lunch', 'dinner']):
                groups['meals taken'].append((noun, english))
            elif any(word in english for word in ['note', 'memo', 'record']):
                groups['notes taken'].append((noun, english))
            elif any(word in english for word in ['hand', 'hold', 'grab']):
                groups['grasping objects'].append((noun, english))
            else:
                groups['things taken'].append((noun, english))

    def _hints_watasu(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for 渡す (to hand over)."""
        for noun, english in nouns:
            if any(word in english for word in ['money', 'cash', 'yen', 'dollar']):
                groups['money handed'].append((noun, english))
            elif any(word in english for word in ['document', 'paper', 'form', 'report']):
                groups['documents given'].append((noun, english))
            elif any(word in english for word in ['present', 'gift', 'item', 'thing']):
                groups['items handed'].append((noun, english))
            elif any(word in english for word in ['letter', 'message', 'mail']):
                groups['correspondence'].append((noun, english))
            elif any(word in english for word in ['key', 'card']):
                groups['keys and cards'].append((noun, english))
            else:
                groups['things passed'].append((noun, english))

    def _hints_morau(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for もらう (to receive)."""
        for noun, english in nouns:
            if any(word in english for word in ['present', 'gift', 'souvenir']):
                groups['gifts received'].append((noun, english))
            elif any(word in english for word in ['money', 'cash', 'yen', 'dollar', 'salary']):
                groups['money received'].append((noun, english))
            elif any(word in english for word in ['letter', 'mail', 'email', 'message']):
                groups['mail received'].append((noun, english))
            elif any(word in english for word in ['help', 'assistance', 'advice']):
                groups['help received'].append((noun, english))
            elif any(word in english for word in ['permission', 'approval']):
                groups['permissions granted'].append((noun, english))
            else:
                groups['things received'].append((noun, english))

    def _hints_ageru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for あげる (to give)."""
        for noun, english in nouns:
            if any(word in english for word in ['present', 'gift', 'souvenir']):
                groups['gifts given'].append((noun, english))
            elif any(word in english for word in ['flower', 'bouquet']):
                groups['flowers given'].append((noun, english))
            elif any(word in english for word in ['money', 'cash', 'yen', 'dollar']):
                groups['money given'].append((noun, english))
            elif any(word in english for word in ['help', 'assistance', 'advice']):
                groups['help given'].append((noun, english))
            elif any(word in english for word in ['candy', 'chocolate', 'food']):
                groups['treats given'].append((noun, english))
            else:
                groups['things given'].append((noun, english))

    def _hints_kureru(self, nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """Generate hints for くれる (to give - to me/us)."""
        for noun, english in nouns:
            if any(word in english for word in ['present', 'gift', 'souvenir']):
                groups['gifts received'].append((noun, english))
            elif any(word in english for word in ['money', 'cash', 'yen', 'dollar']):
                groups['money received'].append((noun, english))
            elif any(word in english for word in ['help', 'assistance', 'advice']):
                groups['help received'].append((noun, english))
            elif any(word in english for word in ['thing', 'item', 'object']):
                groups['things given'].append((noun, english))
            elif any(word in english for word in ['information', 'news']):
                groups['information given'].append((noun, english))
            else:
                groups['what you receive'].append((noun, english))

    def _hints_generic(self, verb: str, verb_english: str,
                      nouns: List[Tuple[str, str]], groups: Dict[str, List]) -> None:
        """
        Generic fallback for verbs without specific handling.
        Attempts to create hints based on English meanings.
        """
        # Try to extract verb action from English
        verb_action = verb_english.split(';')[0].split(',')[0].strip()

        # Create generic groups based on common noun patterns
        for noun, english in nouns:
            categorized = False

            # People
            if any(word in english for word in ['person', 'people', 'man', 'woman', 'child', 'boy', 'girl', 'teacher', 'student', 'friend', 'family']):
                groups['people'].append((noun, english))
                categorized = True
            # Places
            elif any(word in english for word in ['place', 'room', 'house', 'building', 'school', 'company', 'shop', 'store', 'park', 'station']):
                groups['places'].append((noun, english))
                categorized = True
            # Time
            elif any(word in english for word in ['time', 'day', 'week', 'month', 'year', 'morning', 'evening', 'night', 'hour', 'minute']):
                groups['time expressions'].append((noun, english))
                categorized = True
            # Objects
            elif any(word in english for word in ['book', 'pen', 'paper', 'bag', 'phone', 'computer', 'tool', 'thing', 'item']):
                groups['objects'].append((noun, english))
                categorized = True
            # Activities
            elif any(word in english for word in ['work', 'study', 'practice', 'exercise', 'sport', 'game', 'play']):
                groups['activities'].append((noun, english))
                categorized = True

            # If not categorized, add to generic group
            if not categorized:
                groups[f'things you {verb_action}'].append((noun, english))

    def generate_hints(self) -> Dict[str, Dict[str, str]]:
        """
        Generate verb-specific hints for all verbs in the collocations data.

        Returns:
            Dictionary mapping verbs to {noun: hint} dictionaries
        """
        print("\nGenerating verb-specific hints...")

        for verb, verb_data in self.collocations_data['words'].items():
            # Only process verbs
            if verb_data.get('type') != 'verb':
                continue

            print(f"Processing verb: {verb}")

            # Get verb-specific hint groups
            hint_groups = self._get_verb_specific_hints(verb, verb_data)

            # Convert to flat dictionary of noun -> hint
            verb_hints = {}
            for hint_phrase, noun_list in hint_groups.items():
                self.hint_usage_stats[hint_phrase] += len(noun_list)
                for noun, english in noun_list:
                    verb_hints[noun] = hint_phrase

            self.verb_hints[verb] = verb_hints
            print(f"  Generated {len(hint_groups)} hints for {len(verb_hints)} nouns")

        return self.verb_hints

    def analyze_hint_uniqueness(self) -> Dict[str, any]:
        """
        Analyze the uniqueness and distribution of generated hints.

        Returns:
            Dictionary containing statistics about hint usage
        """
        total_hints = len(self.hint_usage_stats)
        total_noun_assignments = sum(self.hint_usage_stats.values())

        # Calculate how many hints are shared across multiple verbs
        hint_verb_map = defaultdict(set)
        for verb, hints in self.verb_hints.items():
            for hint_phrase in set(hints.values()):
                hint_verb_map[hint_phrase].add(verb)

        unique_hints = sum(1 for verbs in hint_verb_map.values() if len(verbs) == 1)
        shared_hints = sum(1 for verbs in hint_verb_map.values() if len(verbs) > 1)

        # Most common hints
        most_common = sorted(self.hint_usage_stats.items(),
                           key=lambda x: x[1], reverse=True)[:20]

        # Calculate overlap percentage
        overlap_pct = (shared_hints / total_hints * 100) if total_hints > 0 else 0

        return {
            'total_unique_hints': total_hints,
            'total_noun_assignments': total_noun_assignments,
            'unique_to_one_verb': unique_hints,
            'shared_across_verbs': shared_hints,
            'overlap_percentage': overlap_pct,
            'most_common_hints': most_common,
            'verbs_processed': len(self.verb_hints)
        }

    def get_verb_examples(self, num_verbs: int = 10) -> Dict[str, Dict]:
        """
        Get detailed examples for top verbs.

        Args:
            num_verbs: Number of verb examples to return

        Returns:
            Dictionary with verb examples and their hint breakdowns
        """
        examples = {}

        # Sort verbs by number of collocations
        sorted_verbs = sorted(
            self.verb_hints.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:num_verbs]

        for verb, noun_hints in sorted_verbs:
            # Group nouns by hint
            hint_breakdown = defaultdict(list)
            for noun, hint in noun_hints.items():
                hint_breakdown[hint].append(noun)

            examples[verb] = {
                'total_nouns': len(noun_hints),
                'total_hints': len(hint_breakdown),
                'hints': dict(hint_breakdown)
            }

        return examples

    def save_hints(self, output_path: str) -> None:
        """
        Save the generated hints to JSON file.

        Args:
            output_path: Path to save the hints file
        """
        output_data = {
            'version': '4.0.0',
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'regenerated': True,
            'verb_specific': True,
            'description': 'Verb-specific collocation hints that describe the relationship between each verb and its nouns',
            'total_words': len(self.verb_hints),
            'total_nouns_with_hints': sum(len(hints) for hints in self.verb_hints.values()),
            'hints': self.verb_hints
        }

        print(f"\nSaving hints to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print("Hints saved successfully!")


def main():
    """Main execution function."""
    # File paths
    collocations_path = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json'
    output_path = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocation_hints_refined.json'

    # Initialize generator
    print("="*80)
    print("VERB-SPECIFIC COLLOCATION HINT GENERATOR v4.0.0")
    print("="*80)

    generator = VerbSpecificHintGenerator(collocations_path)

    # Load and process
    generator.load_collocations()
    generator.generate_hints()

    # Analyze results
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)

    stats = generator.analyze_hint_uniqueness()
    print(f"\nHint Statistics:")
    print(f"  Total unique hint phrases: {stats['total_unique_hints']}")
    print(f"  Total noun assignments: {stats['total_noun_assignments']}")
    print(f"  Hints unique to one verb: {stats['unique_to_one_verb']}")
    print(f"  Hints shared across verbs: {stats['shared_across_verbs']}")
    print(f"  Overlap percentage: {stats['overlap_percentage']:.1f}%")
    print(f"  Verbs processed: {stats['verbs_processed']}")

    print(f"\nMost frequently used hints:")
    for hint, count in stats['most_common_hints'][:10]:
        print(f"  '{hint}': {count} nouns")

    # Show examples
    print("\n" + "="*80)
    print("TOP 10 VERBS - DETAILED BREAKDOWN")
    print("="*80)

    examples = generator.get_verb_examples(10)
    for verb, data in examples.items():
        print(f"\n{verb}: {data['total_nouns']} nouns, {data['total_hints']} hints")
        for hint, nouns in sorted(data['hints'].items(), key=lambda x: len(x[1]), reverse=True):
            noun_sample = ', '.join(nouns[:5])
            if len(nouns) > 5:
                noun_sample += f', ... ({len(nouns)} total)'
            print(f"  '{hint}': {noun_sample}")

    # Save results
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    generator.save_hints(output_path)

    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80)
    print("\nVerb-specific hints have been successfully generated!")
    print(f"Target overlap: <20%")
    print(f"Actual overlap: {stats['overlap_percentage']:.1f}%")
    if stats['overlap_percentage'] < 20:
        print("✓ SUCCESS: Overlap target achieved!")
    else:
        print("⚠ WARNING: Overlap slightly above target")


if __name__ == '__main__':
    main()
