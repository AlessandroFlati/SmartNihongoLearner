/**
 * Collocation Service
 *
 * Handles querying and validating word collocations.
 * All queries run locally in the browser using IndexedDB.
 */

import storage from './storage';
import { Collocation } from '../models/Collocation';

/**
 * Get collocation data for a word
 */
export const getCollocation = async (word) => {
  const data = await storage.getCollocationsByWord(word);
  return data ? new Collocation(data) : null;
};

/**
 * Get all noun matches for a verb or adjective
 */
export const getNounMatches = async (word) => {
  const collocation = await getCollocation(word);
  return collocation ? collocation.getNounMatches() : [];
};

/**
 * Get noun matches filtered by minimum score
 */
export const getNounMatchesByScore = async (word, minScore = 1) => {
  const collocation = await getCollocation(word);
  return collocation ? collocation.getNounMatchesByScore(minScore) : [];
};

/**
 * Check if a word pair is a valid collocation
 *
 * @param {string} word1 - First word (verb or adjective)
 * @param {string} word2 - Second word (noun)
 * @returns {Object|null} Match data if valid, null otherwise
 */
export const validateCollocation = async (word1, word2) => {
  const collocation = await getCollocation(word1);

  if (!collocation) return null;

  const matches = collocation.getNounMatches();
  const match = matches.find(m => m.word === word2);

  return match || null;
};

/**
 * Get collocation score for a word pair
 */
export const getCollocationScore = async (word1, word2) => {
  const match = await validateCollocation(word1, word2);
  return match ? match.score : 0;
};

/**
 * Get all verbs/adjectives that pair with a noun
 *
 * This requires searching all collocations (reverse lookup).
 * For performance, we should have pre-computed this in the data.
 */
export const getWordsThatPairWithNoun = async (noun) => {
  const allCollocations = await storage.getAllCollocations();

  const matches = [];

  for (const entry of allCollocations) {
    if (entry.matches && entry.matches.nouns) {
      const match = entry.matches.nouns.find(m => m.word === noun);
      if (match) {
        matches.push({
          word: entry.word,
          type: entry.type,
          reading: entry.reading,
          english: entry.english,
          score: match.score,
        });
      }
    }
  }

  // Sort by score (descending)
  matches.sort((a, b) => b.score - a.score);

  return matches;
};

/**
 * Search for collocations by partial Japanese text
 */
export const searchCollocations = async (searchTerm) => {
  const allCollocations = await storage.getAllCollocations();

  return allCollocations.filter(entry =>
    entry.word.includes(searchTerm) ||
    entry.reading.includes(searchTerm)
  );
};

/**
 * Get random word for practice (filtered by type)
 */
export const getRandomWordForPractice = async (type, excludeWords = []) => {
  const allCollocations = await storage.getAllCollocations();

  // Filter by type and exclude already seen
  const candidates = allCollocations.filter(
    entry => entry.type === type && !excludeWords.includes(entry.word)
  );

  if (candidates.length === 0) return null;

  // Pick random
  const randomIndex = Math.floor(Math.random() * candidates.length);
  return new Collocation(candidates[randomIndex]);
};

/**
 * Get word pair ID for progress tracking
 * Format: "word1|word2"
 */
export const getPairId = (word1, word2) => {
  return `${word1}|${word2}`;
};

/**
 * Parse pair ID back to words
 */
export const parsePairId = (pairId) => {
  const [word1, word2] = pairId.split('|');
  return { word1, word2 };
};

/**
 * Get collocation statistics for a word
 */
export const getWordCollocationStats = async (word) => {
  const collocation = await getCollocation(word);

  if (!collocation) {
    return {
      totalMatches: 0,
      veryCommon: 0,
      common: 0,
      possible: 0,
    };
  }

  const matches = collocation.getNounMatches();

  return {
    totalMatches: matches.length,
    veryCommon: matches.filter(m => m.score === 3).length,
    common: matches.filter(m => m.score === 2).length,
    possible: matches.filter(m => m.score === 1).length,
  };
};

/**
 * Get recommended practice words based on user progress
 * Prioritizes words with many collocations that haven't been practiced
 */
export const getRecommendedPracticeWords = async (count = 5) => {
  const allCollocations = await storage.getAllCollocations();
  const allProgress = await storage.getAllWordProgress();

  // Create set of practiced word IDs
  const practicedWords = new Set(allProgress.map(p => p.wordId));

  // Score each word
  const scored = allCollocations.map(entry => {
    const matches = entry.matches?.nouns || [];
    const totalScore = matches.reduce((sum, m) => sum + m.score, 0);
    const isPracticed = practicedWords.has(entry.word);

    return {
      ...entry,
      totalScore,
      matchCount: matches.length,
      isPracticed,
      // Prioritize unpracticed words with high scores
      priority: isPracticed ? totalScore * 0.3 : totalScore,
    };
  });

  // Sort by priority
  scored.sort((a, b) => b.priority - a.priority);

  // Return top N
  return scored.slice(0, count).map(s => new Collocation(s));
};

export default {
  getCollocation,
  getNounMatches,
  getNounMatchesByScore,
  validateCollocation,
  getCollocationScore,
  getWordsThatPairWithNoun,
  searchCollocations,
  getRandomWordForPractice,
  getPairId,
  parsePairId,
  getWordCollocationStats,
  getRecommendedPracticeWords,
};
