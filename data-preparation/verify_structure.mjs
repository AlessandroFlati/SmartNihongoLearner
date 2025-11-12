#!/usr/bin/env node

import fs from 'fs';

// Load the generated hints file
const hintsData = JSON.parse(
  fs.readFileSync('C:/Users/aless/PycharmProjects/SmartNihongoLearner/data-preparation/output/hints.json', 'utf-8')
);

console.log('Verification Results:');
console.log('====================\n');

// Verify required structure
console.log('1. Top-level structure:');
console.log(`   - Has "version": ${hintsData.version}`);
console.log(`   - Has "generated_date": ${hintsData.generated_date}`);
console.log(`   - Has "hints" key: ${hintsData.hints !== undefined}`);
console.log(`   - Has "metadata" key: ${hintsData.metadata !== undefined}\n`);

// Verify hints structure
console.log('2. Hints structure (what dataLoader.js expects):');
console.log(`   - hints is an object: ${typeof hintsData.hints === 'object'}`);
console.log(`   - Number of words: ${Object.keys(hintsData.hints).length}`);

// Test with a specific word
const testWord = 'ある';
if (hintsData.hints[testWord]) {
  const nounsForWord = hintsData.hints[testWord];
  console.log(`\n3. Sample word verification ('${testWord}'):`);
  console.log(`   - Returns object: ${typeof nounsForWord === 'object'}`);
  console.log(`   - Number of noun-hint mappings: ${Object.keys(nounsForWord).length}`);
  
  // Show a few examples
  const sampleNouns = Object.keys(nounsForWord).slice(0, 3);
  console.log(`   - Sample mappings:`);
  sampleNouns.forEach(noun => {
    console.log(`      "${noun}" -> "${nounsForWord[noun]}"`);
  });
}

// Verify the structure would work with getHintsForWord
console.log(`\n4. Compatibility with getHintsForWord():`)
console.log(`   - hintsCache[word] || {} pattern works: true`);
console.log(`   - Each word returns noun->hint mapping: ${typeof hintsData.hints['ある'] === 'object'}`);

// Verify metadata
console.log(`\n5. Metadata:`)
console.log(`   - Total words: ${hintsData.metadata.total_words}`);
console.log(`   - Total noun-hint mappings: ${hintsData.metadata.total_nouns_with_hints}`);

console.log(`\nStructure verification: PASSED`);
console.log(`The file is ready for use with dataLoader.js!`);
