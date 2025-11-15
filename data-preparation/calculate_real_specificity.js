import fs from 'fs';

const output = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/output/collocation_hints_complete.json', 'utf-8'));

// Map each hint to the set of verbs using it
const hintToVerbs = {};

for (const [verb, hints] of Object.entries(output.hints)) {
  for (const [noun, hint] of Object.entries(hints)) {
    if (!hintToVerbs[hint]) {
      hintToVerbs[hint] = new Set();
    }
    hintToVerbs[hint].add(verb);
  }
}

// Count verb-specific hints (hints used by only 1 verb)
let totalNouns = 0;
let verbSpecificNouns = 0;

for (const [verb, hints] of Object.entries(output.hints)) {
  for (const [noun, hint] of Object.entries(hints)) {
    totalNouns++;
    if (hintToVerbs[hint].size === 1) {
      verbSpecificNouns++;
    }
  }
}

const specificity = ((verbSpecificNouns / totalNouns) * 100).toFixed(1);

console.log(`Total nouns: ${totalNouns}`);
console.log(`Nouns with verb-specific hints: ${verbSpecificNouns}`);
console.log(`Verb-specificity: ${specificity}%`);

// Show hints shared across multiple verbs
const sharedHints = Object.entries(hintToVerbs)
  .filter(([hint, verbs]) => verbs.size > 1)
  .sort((a, b) => b[1].size - a[1].size);

console.log(`\nHints shared across multiple verbs: ${sharedHints.length}`);
for (const [hint, verbs] of sharedHints.slice(0, 15)) {
  console.log(`  "${hint}" - ${verbs.size} verbs: ${Array.from(verbs).join(', ')}`);
}
