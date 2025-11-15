#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

/**
 * Transform hint structure from nested format to flat format.
 *
 * Converts from:
 * {
 *   "verbs": {
 *     "verb": {
 *       "hints": [
 *         {"hint": "...", "all_nouns": [...]}
 *       ]
 *     }
 *   }
 * }
 *
 * To:
 * {
 *   "version": "5.0.0",
 *   "hints": {
 *     "verb": {
 *       "noun": "hint text"
 *     }
 *   }
 * }
 */
function transformHints(inputFile, outputFile) {
  // Load the input file
  const data = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));

  // Initialize the new structure
  const transformed = {
    version: '5.0.0',
    generated_date: new Date().toISOString(),
    hints: {}
  };

  // Counters for metadata
  let totalWords = 0;
  let totalNounsWithHints = 0;

  // Process each verb
  const verbsData = data.verbs || {};

  for (const [verb, verbData] of Object.entries(verbsData)) {
    transformed.hints[verb] = {};

    // Process each hint for this verb
    const hints = verbData.hints || [];
    for (const hintEntry of hints) {
      const hintText = hintEntry.hint || '';
      const allNouns = hintEntry.all_nouns || [];

      // Map each noun to the hint
      for (const noun of allNouns) {
        transformed.hints[verb][noun] = hintText;
        totalNounsWithHints++;
      }
    }

    totalWords++;
  }

  // Add metadata
  transformed.metadata = {
    total_words: totalWords,
    total_nouns_with_hints: totalNounsWithHints
  };

  // Ensure output directory exists
  const outputDir = path.dirname(outputFile);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Save the transformed file
  fs.writeFileSync(outputFile, JSON.stringify(transformed, null, 2), 'utf-8');

  console.log('Transformation complete!');
  console.log(`  Verbs processed: ${totalWords}`);
  console.log(`  Total noun-hint mappings: ${totalNounsWithHints}`);
  console.log(`  Output file: ${outputFile}`);

  // Verify the structure
  console.log('\nStructure verification:');
  console.log(`  Top-level keys: ${Object.keys(transformed).join(', ')}`);
  const verbKeys = Object.keys(transformed.hints).slice(0, 3);
  console.log(`  Sample verb keys (first 3): ${verbKeys.join(', ')}`);

  if (Object.keys(transformed.hints).length > 0) {
    const firstVerb = Object.keys(transformed.hints)[0];
    const nounKeys = Object.keys(transformed.hints[firstVerb]).slice(0, 3);
    console.log(`  Sample nouns under '${firstVerb}': ${nounKeys.join(', ')}`);
    const firstNoun = Object.keys(transformed.hints[firstVerb])[0];
    console.log(`  Sample hint: "${transformed.hints[firstVerb][firstNoun]}"`);
  }
}

if (require.main === module) {
  const inputPath = 'C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/input/collocation_hints_refined.json';
  const outputPath = 'C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/output/hints.json';

  transformHints(inputPath, outputPath);
}

module.exports = transformHints;
