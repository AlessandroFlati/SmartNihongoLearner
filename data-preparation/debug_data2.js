import fs from 'fs';

const collocationsData = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocations_complete.json', 'utf-8'));

console.log('Total words:', Object.keys(collocationsData.words).length);
console.log('First 5 words:', Object.keys(collocationsData.words).slice(0, 5));

const firstWord = Object.keys(collocationsData.words)[0];
console.log('\nFirst word:', firstWord);
console.log('First word data:', JSON.stringify(collocationsData.words[firstWord], null, 2));
