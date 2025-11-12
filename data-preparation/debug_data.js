import fs from 'fs';

const collocationsData = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocations_complete.json', 'utf-8'));
const currentHints = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/public/data/collocation_hints.json', 'utf-8'));

console.log('Collocations keys:', Object.keys(collocationsData));
console.log('Current hints keys:', Object.keys(currentHints));

if (collocationsData.collocations) {
  console.log('Total verbs:', Object.keys(collocationsData.collocations).length);
  console.log('First verb:', Object.keys(collocationsData.collocations)[0]);
  const firstVerb = Object.keys(collocationsData.collocations)[0];
  console.log('First verb data:', collocationsData.collocations[firstVerb]);
}

if (currentHints.hints) {
  console.log('Verbs with hints:', Object.keys(currentHints.hints).length);
}
