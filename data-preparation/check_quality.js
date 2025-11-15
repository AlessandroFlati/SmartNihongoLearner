import fs from 'fs';

const output = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/output/collocation_hints_complete.json', 'utf-8'));
const collocationsData = JSON.parse(fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocations_complete.json', 'utf-8'));

// Check quality criteria
let tooShort = 0;
let generic = 0;
const totalHints = Object.values(output.hints).reduce((sum, h) => sum + Object.keys(h).length, 0);

for (const [verb, hints] of Object.entries(output.hints)) {
  for (const [noun, hint] of Object.entries(hints)) {
    // Check if hint is too short (< 3 words)
    const wordCount = hint.split(/\s+/).length;
    if (wordCount < 3) {
      tooShort++;
      console.log(`Short hint for ${verb}/${noun}: "${hint}" (${wordCount} words)`);
    }

    // Check for generic terms
    if (hint.includes('things') || hint.includes('events')) {
      generic++;
    }
  }
}

console.log(`\n=== QUALITY CHECK ===`);
console.log(`Total hints: ${totalHints}`);
console.log(`Hints with < 3 words: ${tooShort} (${(tooShort/totalHints*100).toFixed(1)}%)`);
console.log(`Hints with generic terms: ${generic} (${(generic/totalHints*100).toFixed(1)}%)`);

// Sample some verbs
console.log(`\n=== SAMPLE HINTS ===`);
const sampleVerbs = ['好き', '出す', '着る', '開く', '閉まる'];
for (const verb of sampleVerbs) {
  if (output.hints[verb]) {
    const verbData = collocationsData.words[verb];
    console.log(`\n${verb} (${verbData ? verbData.english : 'unknown'}):`);
    const hints = output.hints[verb];
    const sampleNouns = Object.keys(hints).slice(0, 5);
    for (const noun of sampleNouns) {
      console.log(`  ${noun}: "${hints[noun]}"`);
    }
  }
}
