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
 * Build a reverse collocation object for a noun
 * This creates a Collocation-like object with verb/adjective matches
 */
export const getReverseCollocation = async (nounWord, nounData) => {
  const allMatches = await getWordsThatPairWithNoun(nounWord);

  // Separate verbs and adjectives
  const verbs = allMatches.filter(m => m.type === 'verb');
  const adjectives = allMatches.filter(m => m.type === 'adjective');

  // Create a collocation-like object
  const collocationData = {
    word: nounData.japanese,
    type: nounData.type,
    reading: nounData.reading,
    english: nounData.english,
    matches: {
      verbs: verbs,
      adjectives: adjectives,
    },
  };

  return new Collocation(collocationData);
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
 * Get limited noun matches for a word based on SRS progress
 *
 * Selection strategy:
 * 1. NEW collocations (never practiced) - prioritized by linguistic score
 * 2. REVIEW collocations (weak/struggling) - prioritized by low strength
 *
 * @param {string} wordJapanese - The word to get matches for
 * @param {Collocation} collocation - The collocation object
 * @param {number} maxMatches - Maximum number of matches to return (user-controlled)
 * @param {number} newWordsTarget - How many should be NEW (never practiced)
 * @returns {Promise<Array>} Limited array of matches, SRS-prioritized
 */
export const getLimitedNounMatchesWithProgress = async (wordJapanese, collocation, maxMatches = 15, newWordsTarget = 3) => {
  const allMatches = collocation.getNounMatches();
  const total = allMatches.length;

  // If total matches is less than or equal to max, return all
  if (total <= maxMatches) {
    return allMatches;
  }

  // Load progress for each collocation pair
  const matchesWithProgress = await Promise.all(
    allMatches.map(async (match) => {
      const pairId = getPairId(wordJapanese, match.word);
      const progress = await storage.getCollocationProgress(pairId);

      const isNew = !progress || (progress.correct === 0 && progress.incorrect === 0);
      const strength = progress?.strength || 0;

      return {
        ...match,
        progress,
        isNew,
        strength,
      };
    })
  );

  // Separate into NEW and REVIEW
  const newMatches = matchesWithProgress.filter(m => m.isNew);
  const reviewMatches = matchesWithProgress.filter(m => !m.isNew);

  // Sort NEW by linguistic score (3 > 2 > 1), then alphabetically
  newMatches.sort((a, b) => {
    if (b.score !== a.score) {
      return b.score - a.score;
    }
    return a.word.localeCompare(b.word);
  });

  // Sort REVIEW by strength (lowest first), then score, then alphabetically
  reviewMatches.sort((a, b) => {
    if (a.strength !== b.strength) {
      return a.strength - b.strength; // Lower strength first
    }
    if (b.score !== a.score) {
      return b.score - a.score;
    }
    return a.word.localeCompare(b.word);
  });

  // Select matches according to target
  const selected = [];

  // Take up to newWordsTarget from NEW
  const newToTake = Math.min(newWordsTarget, newMatches.length);
  selected.push(...newMatches.slice(0, newToTake));

  // Fill remaining with REVIEW
  const remaining = maxMatches - selected.length;
  selected.push(...reviewMatches.slice(0, remaining));

  // DEBUG: Log selection process
  console.log(`[getLimitedNounMatchesWithProgress] ${wordJapanese}:`, {
    totalMatches: total,
    requestedMax: maxMatches,
    requestedNew: newWordsTarget,
    availableNew: newMatches.length,
    availableReview: reviewMatches.length,
    selectedNew: newToTake,
    selectedReview: Math.min(remaining, reviewMatches.length),
    totalSelected: selected.length,
  });

  // If we don't have enough matches, fill with any remaining matches
  if (selected.length < maxMatches) {
    const alreadySelected = new Set(selected.map(m => m.word));
    const remaining = matchesWithProgress
      .filter(m => !alreadySelected.has(m.word))
      .slice(0, maxMatches - selected.length);
    selected.push(...remaining);
    console.log(`[getLimitedNounMatchesWithProgress] Filled ${remaining.length} more from remaining matches. Total: ${selected.length}`);
  }

  // Return without progress metadata
  return selected.map(({ progress, isNew, strength, ...match }) => match);
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

/**
 * Get recommended nouns for reverse practice (noun-to-verb, noun-to-adjective)
 * Returns nouns that have verb/adjective matches
 */
export const getRecommendedPracticeNouns = async (count = 5) => {
  const allVocabulary = await storage.getAllVocabulary();
  const allCollocations = await storage.getAllCollocations();
  const allProgress = await storage.getAllWordProgress();

  // Create set of practiced word IDs
  const practicedWords = new Set(allProgress.map(p => p.wordId));

  // Get all nouns from vocabulary
  const nouns = allVocabulary.filter(v => v.type === 'noun');

  // For each noun, count how many verbs/adjectives pair with it
  const scored = nouns.map(noun => {
    let verbMatches = 0;
    let adjectiveMatches = 0;
    let totalScore = 0;

    // Check all collocations to see which ones pair with this noun
    for (const entry of allCollocations) {
      if (entry.matches && entry.matches.nouns) {
        const match = entry.matches.nouns.find(m => m.word === noun.japanese);
        if (match) {
          totalScore += match.score;
          if (entry.type === 'verb') {
            verbMatches++;
          } else if (entry.type === 'adjective') {
            adjectiveMatches++;
          }
        }
      }
    }

    const isPracticed = practicedWords.has(noun.japanese);
    const matchCount = verbMatches + adjectiveMatches;

    return {
      word: noun.japanese,
      japanese: noun.japanese,
      reading: noun.reading,
      english: noun.english,
      type: 'noun',
      totalScore,
      matchCount,
      verbMatches,
      adjectiveMatches,
      isPracticed,
      // Prioritize unpracticed nouns with many matches
      priority: isPracticed ? totalScore * 0.3 : totalScore,
    };
  });

  // Filter out nouns with no matches
  const withMatches = scored.filter(n => n.matchCount > 0);

  // Sort by priority
  withMatches.sort((a, b) => b.priority - a.priority);

  // Return top N
  return withMatches.slice(0, count);
};

export default {
  getCollocation,
  getNounMatches,
  getNounMatchesByScore,
  validateCollocation,
  getCollocationScore,
  getWordsThatPairWithNoun,
  getReverseCollocation,
  searchCollocations,
  getRandomWordForPractice,
  getPairId,
  parsePairId,
  getWordCollocationStats,
  getRecommendedPracticeWords,
  getRecommendedPracticeNouns,
  getLimitedNounMatchesWithProgress,
};
