"""Quick script to inspect data structure."""
import json

hints_data = json.load(open(r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\public\data\collocation_hints.json', encoding='utf-8'))

print("Top-level keys:", list(hints_data.keys()))

# The actual hints are under the 'hints' key
if 'hints' in hints_data:
    verb_data = hints_data['hints']
    verbs = list(verb_data.keys())[:3]
    print(f"\nVerbs found: {len(verb_data)}")
    print("Sample verbs:", verbs)

    verb = verbs[0]
    print(f"\nFirst verb: {verb}")
    print(f"Type: {type(verb_data[verb])}")

    if isinstance(verb_data[verb], dict):
        nouns = list(verb_data[verb].keys())[:3]
        print(f"Sample nouns: {nouns}")
        for noun in nouns:
            hint_value = verb_data[verb][noun]
            print(f"  {noun}: {type(hint_value)}")
            if isinstance(hint_value, dict):
                print(f"    Keys: {list(hint_value.keys())}")
                print(f"    Content: {hint_value}")
            else:
                print(f"    Value: {hint_value}")
