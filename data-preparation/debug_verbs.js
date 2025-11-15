import fs from 'fs';

const collocationsData = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocations_complete.json', 'utf-8'));
const currentHints = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/public/data/collocation_hints.json', 'utf-8'));

// Count verbs
const verbsInData = Object.values(collocationsData.words).filter(w => w.type === 'verb' && w.matches?.nouns?.length > 0);
console.log('Total verbs in collocation data:', verbsInData.length);

// Check which words in hints are verbs
const hintsVerbs = Object.keys(currentHints.hints);
console.log('Words with hints:', hintsVerbs.length);
console.log('Hint words:', hintsVerbs);

// Check if hint words are verbs
for (const word of hintsVerbs) {
  if (collocationsData.words[word]) {
    console.log(`${word}: ${collocationsData.words[word].type}, ${collocationsData.words[word].matches?.nouns?.length || 0} nouns`);
  } else {
    console.log(`${word}: NOT FOUND in collocation data`);
  }
}

// Count total pairs
let totalPairs = 0;
for (const word of Object.values(collocationsData.words)) {
  if (word.type === 'verb' && word.matches?.nouns) {
    totalPairs += word.matches.nouns.length;
  }
}
console.log('\nTotal verb-noun pairs:', totalPairs);
