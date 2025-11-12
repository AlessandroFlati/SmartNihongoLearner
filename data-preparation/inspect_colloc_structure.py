"""Inspect collocations structure."""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

colloc_data = json.load(open(r'C:\Users\aless\PycharmProjects\SmartNihongoLearner\data-preparation\input\collocations_complete.json', encoding='utf-8'))

print("Top-level keys:", list(colloc_data.keys()))

if 'words' in colloc_data:
    words_data = colloc_data['words']
    print(f"\nType of 'words': {type(words_data)}")

    if isinstance(words_data, dict):
        verbs = list(words_data.keys())[:3]
        print(f"Sample verbs in 'words': {verbs}")

        for verb in verbs[:1]:
            verb_data = words_data[verb]
            print(f"\nVerb: {verb}")
            print(f"Type: {type(verb_data)}")
            if isinstance(verb_data, dict):
                print(f"Keys: {list(verb_data.keys())}")
                if 'matches' in verb_data:
                    matches = verb_data['matches']
                    print(f"Matches type: {type(matches)}")
                    print(f"Matches count: {len(matches)}")
                    if isinstance(matches, dict):
                        match_keys = list(matches.keys())[:3]
                        print(f"Sample match keys (nouns): {match_keys}")
                        if len(match_keys) > 0:
                            first_noun = match_keys[0]
                            print(f"First noun: {first_noun}")
                            print(f"Match value type: {type(matches[first_noun])}")
                            print(f"Match value: {matches[first_noun]}")
    elif isinstance(words_data, list):
        print(f"'words' is a list with {len(words_data)} items")
        if len(words_data) > 0:
            print(f"First item type: {type(words_data[0])}")
            print(f"First item: {words_data[0]}")
