import fs from 'fs';

const output = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/output/collocation_hints_complete.json', 'utf-8'));

// Find hints shared across multiple verbs
const hintToVerbs = {};

for (const [verb, hints] of Object.entries(output.hints)) {
  for (const [noun, hint] of Object.entries(hints)) {
    if (!hintToVerbs[hint]) {
      hintToVerbs[hint] = [];
    }
    hintToVerbs[hint].push({ verb, noun });
  }
}

// Show hints used by multiple verbs
const sharedHints = Object.entries(hintToVerbs)
  .filter(([hint, verbs]) => verbs.length > 1)
  .sort((a, b) => b[1].length - a[1].length);

console.log('Top shared hints (used by multiple verbs):');
for (const [hint, occurrences] of sharedHints.slice(0, 20)) {
  console.log(`\n"${hint}" - used ${occurrences.length} times across ${new Set(occurrences.map(o => o.verb)).size} verbs:`);
  const verbCounts = {};
  for (const {verb} of occurrences) {
    verbCounts[verb] = (verbCounts[verb] || 0) + 1;
  }
  for (const [verb, count] of Object.entries(verbCounts)) {
    console.log(`  ${verb}: ${count} nouns`);
  }
}

console.log(`\n\nTotal hints: ${Object.keys(hintToVerbs).length}`);
console.log(`Shared hints: ${sharedHints.length}`);
console.log(`Verb-specific hints: ${Object.keys(hintToVerbs).length - sharedHints.length}`);
