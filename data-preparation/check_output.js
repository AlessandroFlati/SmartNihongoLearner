import fs from 'fs';

const output = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/output/collocation_hints_complete.json', 'utf-8'));
const collocationsData = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocations_complete.json', 'utf-8'));

console.log('Output statistics:', output.statistics);

// Count hints per verb
let totalHints = 0;
for (const [verb, hints] of Object.entries(output.hints)) {
  const count = Object.keys(hints).length;
  totalHints += count;

  // Check if verb is in collocation data
  const verbData = collocationsData.words[verb];
  if (verbData && verbData.matches?.nouns) {
    const nounCount = verbData.matches.nouns.length;
    if (count !== nounCount) {
      console.log(`${verb}: ${count} hints vs ${nounCount} nouns (diff: ${count - nounCount})`);
    }
  }
}

console.log('\nTotal hints across all verbs:', totalHints);
