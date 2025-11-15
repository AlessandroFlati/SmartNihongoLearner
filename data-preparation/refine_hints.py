"""
Refine collocation hints by analyzing semantic patterns in noun collocations.

This script processes the complete collocations data and generates meaningful
semantic category hints based on the English meanings of noun collocations.
"""

import json
from collections import defaultdict
from typing import Dict, List, Tuple
import re
import sys

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def analyze_noun_meanings(nouns_data: List[Dict]) -> Dict[str, List[Tuple[str, str]]]:
    """
    Analyze noun collocations and group them by semantic similarity.

    Args:
        nouns_data: List of noun dictionaries with 'word' and 'english' keys

    Returns:
        Dictionary mapping semantic hints to lists of (noun, meaning) tuples
    """
    groups = defaultdict(list)

    # Extract all noun-meaning pairs
    noun_meanings = [(item['word'], item['english']) for item in nouns_data]

    # Semantic patterns - map keywords to category hints
    patterns = {
        # Time and temporal
        r'\b(time|hour|minute|second|day|week|month|year|morning|afternoon|evening|night|today|tomorrow|yesterday|date|schedule|deadline|period|era|season|age)\b': 'time and temporal expressions',
        r'\b(spring|summer|fall|autumn|winter|january|february|march|april|may|june|july|august|september|october|november|december)\b': 'seasons and months',

        # People and relationships
        r'\b(person|people|human|someone|man|woman|boy|girl|child|children|kid|baby|adult)\b': 'people',
        r'\b(family|mother|father|parent|son|daughter|sibling|brother|sister|grandfather|grandmother|uncle|aunt|cousin|relative|husband|wife|spouse)\b': 'family members',
        r'\b(friend|companion|colleague|coworker|partner|acquaintance|classmate|teammate|roommate)\b': 'friends and associates',
        r'\b(teacher|professor|instructor|student|pupil|learner|principal|tutor)\b': 'education roles',
        r'\b(doctor|nurse|patient|dentist|physician|surgeon|therapist|medical)\b': 'medical professionals and patients',
        r'\b(employee|employer|worker|staff|boss|manager|director|president|ceo|executive|officer|secretary|assistant|clerk)\b': 'occupations and workplace roles',
        r'\b(driver|pilot|captain|conductor|operator|chef|cook|waiter|server|customer|client|guest)\b': 'service and transportation roles',
        r'\b(artist|musician|singer|actor|actress|writer|author|painter|photographer|designer)\b': 'artists and creators',
        r'\b(police|officer|detective|guard|soldier|firefighter|lawyer|attorney|judge)\b': 'public service and legal roles',

        # Places and locations
        r'\b(place|location|area|region|spot|site|position)\b': 'places and locations',
        r'\b(house|home|apartment|room|bedroom|bathroom|kitchen|living room|dining room|office|building|floor|ceiling|wall|door|window|roof|garage)\b': 'buildings and rooms',
        r'\b(school|university|college|classroom|library|laboratory|campus|dormitory|gym|gymnasium)\b': 'educational facilities',
        r'\b(hospital|clinic|pharmacy|doctor\'s office)\b': 'medical facilities',
        r'\b(store|shop|market|supermarket|mall|department store|restaurant|cafe|bar|hotel|bank|post office|station|airport|port)\b': 'commercial and public facilities',
        r'\b(park|garden|zoo|museum|theater|cinema|stadium|temple|shrine|church|beach|mountain|forest|river|lake|sea|ocean)\b': 'recreational and natural places',
        r'\b(city|town|village|country|nation|prefecture|capital|downtown|suburb|neighborhood|street|road|avenue)\b': 'geographic locations',
        r'\b(tokyo|osaka|kyoto|japan|america|china|korea|europe|asia)\b': 'specific places',

        # Things and objects
        r'\b(thing|object|item|stuff|matter|material|substance)\b': 'things and objects',
        r'\b(book|magazine|newspaper|journal|novel|textbook|dictionary|document|paper|letter|mail|card|note|report|article|story|text)\b': 'reading materials and documents',
        r'\b(pen|pencil|notebook|eraser|ruler|scissors|tape|desk|chair|table|shelf|box|bag|briefcase|backpack)\b': 'stationery and office items',
        r'\b(computer|laptop|phone|smartphone|tablet|camera|television|tv|radio|video|cd|dvd|recorder|printer|keyboard|mouse|screen|internet|email|website|software|app|program)\b': 'technology and electronics',
        r'\b(car|vehicle|automobile|bus|train|subway|taxi|bicycle|bike|motorcycle|truck|ship|boat|airplane|plane)\b': 'vehicles and transportation',
        r'\b(clothes|clothing|shirt|t-shirt|pants|trousers|skirt|dress|suit|coat|jacket|sweater|shoes|hat|cap|glasses|watch|jewelry|ring|necklace)\b': 'clothing and accessories',
        r'\b(food|meal|breakfast|lunch|dinner|dish|rice|bread|meat|fish|chicken|beef|pork|vegetable|fruit|egg|cheese|butter|sugar|salt|pepper|sauce)\b': 'food and meals',
        r'\b(water|tea|coffee|juice|milk|beer|wine|alcohol|drink|beverage|soda|cola)\b': 'beverages',
        r'\b(medicine|drug|pill|tablet|vitamin|supplement|injection|vaccine)\b': 'medicine and supplements',
        r'\b(money|cash|coin|bill|dollar|yen|price|cost|fee|salary|wage|income|payment|deposit|debt|loan|tax|budget)\b': 'money and finances',
        r'\b(furniture|sofa|couch|bed|mattress|pillow|blanket|sheet|towel|curtain|lamp|light|clock)\b': 'furniture and household items',
        r'\b(dish|plate|bowl|cup|glass|mug|fork|knife|spoon|chopsticks|pot|pan|kettle)\b': 'kitchenware and utensils',
        r'\b(ball|game|toy|doll|cards|puzzle)\b': 'toys and games',
        r'\b(tool|equipment|machine|device|instrument|engine|motor)\b': 'tools and equipment',
        r'\b(key|lock|battery|wire|cable|switch|button|handle)\b': 'small objects and parts',

        # Activities and events
        r'\b(work|job|task|duty|business|occupation|career|profession|labor|employment)\b': 'work and employment',
        r'\b(study|learning|education|training|practice|lesson|course|class|lecture|exam|test|quiz|homework|assignment|research)\b': 'academic and study activities',
        r'\b(meeting|conference|discussion|talk|conversation|chat|debate|interview|presentation|speech)\b': 'meetings and discussions',
        r'\b(party|celebration|festival|event|ceremony|wedding|funeral|birthday|anniversary)\b': 'celebrations and events',
        r'\b(sport|exercise|training|practice|game|match|competition|race|running|swimming|tennis|soccer|baseball|basketball|golf)\b': 'sports and physical activities',
        r'\b(hobby|leisure|recreation|entertainment|fun|amusement|play)\b': 'hobbies and leisure',
        r'\b(travel|trip|journey|tour|vacation|holiday|visit|sightseeing)\b': 'travel and tourism',
        r'\b(shopping|purchase|buying|selling|sale|trade|order)\b': 'shopping and commerce',
        r'\b(cooking|baking|preparing|meal preparation)\b': 'cooking and food preparation',
        r'\b(cleaning|washing|sweeping|wiping|tidying|organizing|laundry)\b': 'cleaning and housework',
        r'\b(driving|riding|walking|running|moving|going|coming|arriving|departing|leaving|entering|exiting)\b': 'movement and transportation',
        r'\b(reading|writing|drawing|painting|singing|playing|listening|watching|seeing|looking|hearing)\b': 'cultural and creative activities',
        r'\b(sleeping|waking|resting|relaxing|lying|sitting|standing)\b': 'rest and posture',
        r'\b(eating|drinking|consuming|tasting)\b': 'eating and drinking',
        r'\b(wearing|putting on|taking off|dressing)\b': 'wearing and clothing',
        r'\b(opening|closing|shutting|locking|unlocking)\b': 'opening and closing',
        r'\b(starting|beginning|ending|finishing|completing|stopping|continuing)\b': 'beginning and ending',
        r'\b(making|creating|building|constructing|producing|manufacturing)\b': 'creation and production',
        r'\b(breaking|destroying|damaging|ruining|fixing|repairing|mending)\b': 'damage and repair',
        r'\b(giving|providing|offering|presenting|handing|delivering|sending|receiving|getting|obtaining|acquiring)\b': 'giving and receiving',
        r'\b(showing|displaying|exhibiting|demonstrating|explaining|teaching|telling|informing|notifying)\b': 'showing and explaining',
        r'\b(helping|assisting|supporting|aiding|serving|caring)\b': 'helping and support',
        r'\b(using|utilizing|employing|applying|operating|handling)\b': 'using and operating',
        r'\b(choosing|selecting|deciding|determining|picking)\b': 'choosing and deciding',
        r'\b(thinking|considering|pondering|reflecting|remembering|forgetting|knowing|understanding|believing|imagining)\b': 'mental activities',
        r'\b(feeling|emotion|mood|happiness|joy|sadness|anger|fear|worry|anxiety|excitement|surprise|interest|love|hate|like|dislike)\b': 'emotions and feelings',
        r'\b(wanting|desiring|wishing|hoping|needing|requiring)\b': 'desires and needs',

        # Abstract concepts
        r'\b(idea|concept|thought|opinion|view|belief|theory|principle|rule|law|regulation|policy)\b': 'ideas and concepts',
        r'\b(problem|issue|matter|question|difficulty|trouble|challenge|concern)\b': 'problems and issues',
        r'\b(solution|answer|result|outcome|consequence|effect|impact|influence)\b': 'results and solutions',
        r'\b(plan|planning|preparation|arrangement|organization|scheme|project|program)\b': 'planning and preparation',
        r'\b(goal|aim|objective|purpose|target|intention)\b': 'goals and objectives',
        r'\b(reason|cause|factor|basis|ground|motive)\b': 'reasons and causes',
        r'\b(way|method|means|manner|style|approach|technique|system|process|procedure)\b': 'methods and processes',
        r'\b(information|data|fact|detail|knowledge|news|story|rumor)\b': 'information and knowledge',
        r'\b(language|word|vocabulary|grammar|pronunciation|accent|translation|interpretation)\b': 'language and linguistics',
        r'\b(culture|custom|tradition|habit|manner|etiquette|courtesy|politeness)\b': 'culture and customs',
        r'\b(society|community|public|social|group|team|club|organization|company|corporation|firm|business)\b': 'social groups and organizations',
        r'\b(government|politics|political|administration|policy|law|legislation)\b': 'government and politics',
        r'\b(economy|economic|finance|financial|market|industry|trade|commerce|business)\b': 'economics and business',
        r'\b(science|scientific|technology|technical|research|study|experiment|discovery|invention)\b': 'science and technology',
        r'\b(art|artistic|music|musical|literature|literary|culture|cultural)\b': 'arts and culture',
        r'\b(history|historical|past|ancient|modern|traditional|contemporary)\b': 'history and time periods',
        r'\b(nature|natural|environment|environmental|ecology|ecological|weather|climate|temperature)\b': 'nature and environment',
        r'\b(health|healthy|medical|medicine|illness|disease|sickness|injury|pain|symptom|treatment|cure|care)\b': 'health and medical',
        r'\b(life|living|birth|death|growth|development|change|evolution)\b': 'life and existence',
        r'\b(quality|characteristic|feature|property|attribute|trait|nature)\b': 'qualities and characteristics',
        r'\b(size|amount|quantity|number|degree|level|extent|measure|measurement)\b': 'quantities and measurements',
        r'\b(color|shape|form|appearance|look|design|pattern|style)\b': 'appearance and design',
        r'\b(sound|noise|voice|volume|tone|pitch)\b': 'sounds',
        r'\b(smell|scent|odor|fragrance|aroma)\b': 'smells and scents',
        r'\b(taste|flavor)\b': 'tastes',
        r'\b(touch|feel|texture|surface)\b': 'touch and texture',
        r'\b(light|brightness|darkness|shadow|shine|glow)\b': 'light and darkness',
        r'\b(power|energy|force|strength|ability|capability|skill|talent|gift)\b': 'abilities and powers',
        r'\b(importance|significance|value|worth|meaning|sense|implication)\b': 'importance and meaning',
        r'\b(difference|distinction|contrast|comparison|similarity|likeness)\b': 'comparisons and differences',
        r'\b(relationship|relation|connection|link|association|bond|tie)\b': 'relationships and connections',
        r'\b(state|status|situation|condition|circumstance|case|position)\b': 'states and conditions',
        r'\b(change|transformation|conversion|shift|transition|alteration|modification|adjustment)\b': 'changes and transformations',
        r'\b(increase|growth|rise|expansion|decrease|reduction|decline|fall)\b': 'increases and decreases',
        r'\b(success|achievement|accomplishment|victory|win|failure|defeat|loss|mistake|error)\b': 'success and failure',
        r'\b(beginning|start|origin|source|end|ending|finish|conclusion|termination)\b': 'beginnings and endings',
        r'\b(part|portion|section|segment|piece|fragment|component|element|unit|whole|entirety|total)\b': 'parts and wholes',
        r'\b(inside|interior|inner|outside|exterior|outer|surface|top|bottom|front|back|side|left|right|center|middle|edge|corner)\b': 'spatial positions',
        r'\b(direction|course|route|path|way)\b': 'directions and routes',
        r'\b(distance|length|width|height|depth|thickness)\b': 'dimensions and distances',
        r'\b(speed|pace|rate|velocity)\b': 'speed and pace',
        r'\b(order|sequence|series|arrangement|organization|structure|system)\b': 'order and structure',
        r'\b(permission|approval|consent|agreement|acceptance|refusal|rejection|denial|opposition|objection)\b': 'permission and opposition',
        r'\b(promise|commitment|pledge|vow|oath|guarantee|assurance)\b': 'promises and commitments',
        r'\b(request|demand|requirement|claim|appeal|petition)\b': 'requests and demands',
        r'\b(offer|proposal|suggestion|recommendation|advice|guidance|instruction|direction|command|order)\b': 'offers and instructions',
        r'\b(thanks|gratitude|appreciation|apology|excuse|forgiveness)\b': 'gratitude and apologies',
        r'\b(greeting|welcome|introduction|farewell|goodbye)\b': 'greetings and farewells',
        r'\b(praise|compliment|criticism|complaint|accusation|blame)\b': 'praise and criticism',
        r'\b(invitation|welcome|hospitality|entertainment|treat)\b': 'invitations and hospitality',
        r'\b(reservation|booking|appointment|schedule|registration|application)\b': 'bookings and arrangements',
        r'\b(contact|communication|message|notice|notification|announcement|declaration|statement)\b': 'communication and announcements',
        r'\b(question|inquiry|query|answer|reply|response|explanation|description|account)\b': 'questions and answers',
        r'\b(story|tale|narrative|account|description|report|news|article)\b': 'stories and reports',
        r'\b(example|instance|case|sample|model|pattern)\b': 'examples and models',
        r'\b(experience|practice|trial|attempt|effort|endeavor)\b': 'experiences and attempts',
        r'\b(habit|custom|routine|ritual|ceremony)\b': 'habits and rituals',
        r'\b(rule|regulation|law|principle|standard|norm|criterion)\b': 'rules and standards',
        r'\b(right|privilege|freedom|liberty|duty|obligation|responsibility)\b': 'rights and duties',
        r'\b(interest|concern|attention|care|regard|consideration)\b': 'interest and attention',
        r'\b(safety|security|danger|risk|threat|hazard|protection|defense)\b': 'safety and danger',
        r'\b(advantage|benefit|merit|disadvantage|drawback|defect|fault|weakness)\b': 'advantages and disadvantages',
        r'\b(possibility|potential|chance|opportunity|probability|likelihood|impossibility)\b': 'possibilities and chances',
        r'\b(necessity|need|requirement|importance|urgency)\b': 'necessity and importance',
        r'\b(convenience|ease|comfort|inconvenience|difficulty|hardship|trouble)\b': 'convenience and difficulty',
    }

    # First pass: try to match patterns
    unmatched = []
    for noun, meaning in noun_meanings:
        matched = False
        meaning_lower = meaning.lower()

        for pattern, hint in patterns.items():
            if re.search(pattern, meaning_lower):
                groups[hint].append((noun, meaning))
                matched = True
                break

        if not matched:
            unmatched.append((noun, meaning))

    # Second pass: create better semantic hints for unmatched items
    if unmatched:
        # Additional manual categorization for common patterns not caught
        manual_categories = {
            # Foods
            r'\b(candy|cake|jam|steak|hamburg|sandwich|salad|pizza|pasta|noodles|soup|rice|bread|meat|fish|egg|cheese|butter|milk|cream|yogurt|ice cream|chocolate|cookie|biscuit|fruit|apple|banana|orange|grape|strawberry|vegetable|carrot|potato|tomato|onion|cabbage|lettuce|spinach)\b': 'food and meals',
            # Drinks
            r'\b(tea|coffee|juice|water|milk|beer|wine|sake|soda|cola|drink)\b': 'beverages',
            # Days of week
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b': 'days of the week',
            # Numbers and counting
            r'\b(one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|million|billion|dozen|pair|couple|zero|double|triple|half|quarter)\b': 'numbers and quantities',
            # Directions
            r'\b(north|south|east|west|left|right|up|down|front|back|forward|backward|upward|downward)\b': 'directions',
            # Body parts
            r'\b(head|face|eye|nose|mouth|ear|neck|shoulder|arm|hand|finger|chest|back|stomach|leg|foot|toe|skin|hair|tooth|teeth|bone|muscle|heart|brain|blood)\b': 'body parts',
            # Clothing and accessories
            r'\b(clothes|shirt|pants|dress|skirt|coat|jacket|sweater|hat|cap|shoes|boots|socks|gloves|scarf|tie|belt|glasses|watch|ring|necklace|earrings|bracelet)\b': 'clothing and accessories',
            # Colors
            r'\b(red|blue|green|yellow|orange|purple|pink|brown|black|white|gray|grey)\b': 'colors',
            # Weather
            r'\b(weather|sunny|cloudy|rainy|snowy|windy|stormy|hot|cold|warm|cool|humid|dry|temperature|cloud|rain|snow|wind|storm|thunder|lightning|fog|mist)\b': 'weather and climate',
            # Animals
            r'\b(animal|dog|cat|bird|fish|horse|cow|pig|chicken|duck|rabbit|mouse|rat|lion|tiger|bear|elephant|monkey|snake|frog|insect|ant|bee|butterfly|spider)\b': 'animals',
            # Plants
            r'\b(plant|tree|flower|grass|leaf|root|branch|seed|fruit|vegetable|bush|shrub|vine)\b': 'plants and vegetation',
            # Materials
            r'\b(wood|wooden|stone|rock|metal|iron|steel|gold|silver|copper|glass|plastic|rubber|leather|cloth|fabric|paper|cardboard|sand|soil|dirt|mud|water|oil|gas)\b': 'materials and substances',
            # Shapes
            r'\b(circle|square|triangle|rectangle|oval|round|flat|straight|curved|sharp|pointed)\b': 'shapes and forms',
            # Academic subjects
            r'\b(mathematics|math|science|physics|chemistry|biology|history|geography|literature|language|music|art|physical education|pe)\b': 'academic subjects',
            # Occupations not caught
            r'\b(farmer|fisherman|sailor|soldier|chef|cook|waiter|waitress|cashier|salesperson|clerk|secretary|receptionist)\b': 'occupations and workplace roles',
            # Family
            r'\b(family|relatives|relationship|papa|mama|daddy|mommy|grandpa|grandma|grandson|granddaughter|nephew|niece|stepfather|stepmother|stepson|stepdaughter)\b': 'family members',
            # Household items
            r'\b(telephone|phone|clock|mirror|picture|photo|lamp|candle|vase|ashtray|trash|garbage|dustbin)\b': 'household items',
            # Documents
            r'\b(passport|license|certificate|diploma|form|application|contract|agreement|receipt|invoice|bill|ticket|stamp|postcard|envelope|package)\b': 'documents and papers',
            # Activities
            r'\b(dance|song|music|singing|dancing|playing|drawing|painting|writing|reading)\b': 'cultural and creative activities',
            # Natural features
            r'\b(mountain|hill|valley|cliff|cave|island|peninsula|continent|ocean|sea|lake|river|stream|pond|waterfall|beach|coast|shore|desert|plain|field|meadow|forest|woods|jungle)\b': 'natural features',
            # Urban features
            r'\b(city|town|village|street|road|avenue|boulevard|highway|bridge|tunnel|building|tower|skyscraper|apartment|condominium)\b': 'urban features',
            # Abstract concepts
            r'\b(dream|hope|wish|desire|fear|worry|anxiety|happiness|joy|sadness|anger|love|hate|peace|war|freedom|justice|truth|lie|beauty|ugliness)\b': 'abstract concepts and emotions',
            # Positions/locations
            r'\b(top|bottom|middle|center|corner|edge|side|inside|outside|above|below|over|under|between|among|near|far|here|there)\b': 'spatial positions',
            # Proper nouns - Countries
            r'\b(japan|china|korea|america|usa|canada|mexico|brazil|england|britain|france|germany|italy|spain|russia|india|australia|africa|asia|europe)\b': 'countries and regions',
            # Cities
            r'\b(tokyo|osaka|kyoto|yokohama|nagoya|sapporo|kobe|fukuoka|sendai|hiroshima|london|paris|berlin|rome|madrid|moscow|beijing|shanghai|seoul|bangkok|singapore|sydney|new york|los angeles|chicago)\b': 'cities',
            # Miscellaneous specific items
            r'\b(name|type|kind|sort|brand|model|size|shape|color|pattern|design|style|fashion|trend)\b': 'types and categories',
            r'\b(century|decade|era|period|age|epoch|generation)\b': 'time periods',
            r'\b(page|chapter|section|paragraph|line|sentence|word|character|letter)\b': 'text elements',
            r'\b(concert|performance|show|exhibition|display|festival|fair|carnival)\b': 'cultural events',
            r'\b(scenery|landscape|view|sight|scene)\b': 'scenery and views',
            r'\b(map|atlas|globe|chart|diagram|graph|table|list)\b': 'reference materials',
            r'\b(embassy|consulate|ministry|department|bureau|agency|administration)\b': 'government offices',
            r'\b(island|isle)\b': 'islands',
            r'\b(hall|corridor|hallway|passage|passageway|lobby|entrance|exit|gate|door|doorway|window)\b': 'architectural elements',
        }

        # Try manual categories first
        still_unmatched = []
        for noun, meaning in unmatched:
            matched = False
            meaning_lower = meaning.lower()

            for pattern, hint in manual_categories.items():
                if re.search(pattern, meaning_lower):
                    groups[hint].append((noun, meaning))
                    matched = True
                    break

            if not matched:
                still_unmatched.append((noun, meaning))

        # For remaining unmatched, use a cleaned-up version of the meaning
        for noun, meaning in still_unmatched:
            # Extract key concept from meaning
            # Remove common suffixes and particles
            cleaned = re.sub(r';\s*(suffix|prefix|particle|counter|auxiliary|copula|interjection).*$', '', meaning, flags=re.IGNORECASE)
            # Take first meaningful clause before semicolon
            parts = cleaned.split(';')
            first_part = parts[0].strip()

            # Remove articles and create hint
            words = first_part.lower().split()
            significant_words = [w for w in words if w not in {'a', 'an', 'the', 'to', 'of', 'and', 'or', 'in', 'on', 'at', 'for', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'being', 'been'}]

            if significant_words:
                # Use first 2-3 significant words as hint
                hint_words = significant_words[:min(3, len(significant_words))]
                hint = ' '.join(hint_words)
                groups[hint].append((noun, meaning))
            else:
                groups['miscellaneous'].append((noun, meaning))

    return dict(groups)


def create_refined_hint(verb: str, group_data: List[Tuple[str, str]]) -> str:
    """
    Create a refined semantic hint for a group of nouns.

    Args:
        verb: The verb/adjective being analyzed
        group_data: List of (noun, meaning) tuples in the group

    Returns:
        A refined semantic hint string
    """
    # This function receives already-grouped data from analyze_noun_meanings
    # The hint is determined by the semantic analysis in that function
    # Here we just return a representative hint based on the meanings

    if not group_data:
        return "related items"

    # The grouping key from analyze_noun_meanings already provides a good hint
    # This function is called after grouping, so we trust the semantic analysis
    return "semantic category"  # Placeholder - actual hint comes from the grouping key


def process_collocations(collocations_file: str, output_file: str, start_word: str = None):
    """
    Process all collocations and generate refined hints.

    Args:
        collocations_file: Path to collocations_complete.json
        output_file: Path to collocation_hints_refined.json
        start_word: Word to start processing from (None = start from beginning)
    """
    print("Loading collocations data...")
    with open(collocations_file, 'r', encoding='utf-8') as f:
        collocations_file_data = json.load(f)

    # Extract the words dictionary from the JSON structure
    collocations_data = collocations_file_data.get('words', {})

    print("Loading existing refined hints...")
    with open(output_file, 'r', encoding='utf-8') as f:
        refined_data = json.load(f)

    hints = refined_data['hints']

    # Get list of all verbs/adjectives
    all_verbs = list(collocations_data.keys())
    print(f"Total words to process: {len(all_verbs)}")

    # Find starting position
    start_idx = 0
    if start_word and start_word in all_verbs:
        start_idx = all_verbs.index(start_word) + 1
        print(f"Starting from word #{start_idx + 1}: {all_verbs[start_idx] if start_idx < len(all_verbs) else 'END'}")

    # Process each verb/adjective
    processed_count = 0
    total_nouns = sum(len(nouns) for nouns in hints.values())

    for i in range(start_idx, len(all_verbs)):
        verb = all_verbs[i]
        verb_entry = collocations_data[verb]

        # Extract the nouns list from the matches
        noun_data = verb_entry.get('matches', {}).get('nouns', [])

        if i % 10 == 0:
            print(f"Processing {i+1}/{len(all_verbs)}: {verb}")

        # Analyze and group nouns by semantic similarity
        semantic_groups = analyze_noun_meanings(noun_data)

        # Create hints for each noun based on its semantic group
        verb_hints = {}
        for hint_category, noun_list in semantic_groups.items():
            for noun, meaning in noun_list:
                verb_hints[noun] = hint_category

        # Add to refined hints
        hints[verb] = verb_hints
        processed_count += 1
        total_nouns += len(verb_hints)

    # Update metadata
    refined_data['total_words'] = len(hints)
    refined_data['total_nouns_with_hints'] = total_nouns
    refined_data['generated_date'] = '2025-11-11'
    refined_data['hints'] = hints

    # Write updated data
    print(f"\nWriting refined hints to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(refined_data, f, ensure_ascii=False, indent=2)

    print(f"\nProcessing complete!")
    print(f"- Words processed: {processed_count}")
    print(f"- Total words: {len(hints)}")
    print(f"- Total nouns with hints: {total_nouns}")

    return processed_count, len(hints), total_nouns


if __name__ == '__main__':
    collocations_file = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json'
    output_file = r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocation_hints_refined.json'

    # Start processing from after する (already completed)
    processed, total_words, total_nouns = process_collocations(
        collocations_file,
        output_file,
        start_word='する'
    )

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Words newly processed: {processed}")
    print(f"Total words in database: {total_words}")
    print(f"Total nouns with hints: {total_nouns}")
    print(f"Average nouns per word: {total_nouns / total_words:.1f}")
