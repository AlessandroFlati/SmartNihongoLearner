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
 * @param {Array} preFilteredMatches - Optional pre-filtered matches (e.g., by study list)
 * @returns {Promise<Array>} Limited array of matches, SRS-prioritized
 */
export const getLimitedNounMatchesWithProgress = async (wordJapanese, collocation, maxMatches = 15, newWordsTarget = 3, preFilteredMatches = null) => {
  const allMatches = preFilteredMatches || collocation.getNounMatches();
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

  // If we don't have enough matches, fill with any remaining matches
  if (selected.length < maxMatches) {
    const alreadySelected = new Set(selected.map(m => m.word));
    const remaining = matchesWithProgress
      .filter(m => !alreadySelected.has(m.word))
      .slice(0, maxMatches - selected.length);
    selected.push(...remaining);
  }

  // Return without progress metadata
  return selected.map(({ progress, isNew, strength, ...match }) => match);
};

/**
 * Get recommended practice words based on SRS progress
 * Prioritizes: failed/struggling > due for review > new words
 * @param {number} count - Maximum number of words to return
 * @param {Set} studyListWords - Optional set of words to filter noun matches by
 */
export const getRecommendedPracticeWords = async (count = 10, studyListWords = null) => {
  const allCollocations = await storage.getAllCollocations();
  const allProgress = await storage.getAllWordProgress();
  const now = new Date().toISOString();

  // Create progress map for quick lookup
  const progressMap = new Map(allProgress.map(p => [p.wordId, p]));

  // Score each word based on SRS priority
  const scored = allCollocations.map(entry => {
    const progress = progressMap.get(entry.word);
    const matches = entry.matches?.nouns || [];

    // Skip words with no matches at all
    if (matches.length === 0) {
      return null;
    }

    // Only count noun matches that are in the study list (if provided) for scoring
    // But don't exclude words with no study list matches - they'll get expanded later
    const filteredMatches = studyListWords
      ? matches.filter(m => studyListWords.has(m.word))
      : matches;

    // Use filtered matches for scoring, or all matches if filtered is empty
    const matchesForScoring = filteredMatches.length > 0 ? filteredMatches : matches.slice(0, 2);
    const collocationScore = matchesForScoring.reduce((sum, m) => sum + m.score, 0);

    if (!progress) {
      // NEW word - HIGHEST priority (learn new words first, sorted by frequency)
      return {
        ...entry,
        category: 'new',
        priority: 20000 + collocationScore,
      };
    }

    const interval = progress.interval || 0;
    const correctCount = progress.correctCount || 0;
    const level = progress.level || 0;
    const isDue = progress.nextReview && progress.nextReview <= now;

    // Calculate SRS priority
    let priority = 0;
    let category = 'mature';

    if (interval === 0 || correctCount === 0) {
      // FAILED - second highest priority
      category = 'failed';
      priority = 10000 + collocationScore;
    } else if (correctCount < 3 || interval < 3) {
      // LEARNING (struggling) - high priority, sorted by struggle level
      category = 'learning';
      priority = 5000 + (3 - correctCount) * 1000 + collocationScore;
    } else if (isDue) {
      // DUE FOR REVIEW - high priority based on how overdue
      const daysOverdue = (new Date() - new Date(progress.nextReview)) / (1000 * 60 * 60 * 24);
      category = 'due';
      priority = 2000 + daysOverdue * 100 + collocationScore;
    } else if (level < 5) {
      // YOUNG - medium-low priority
      category = 'young';
      priority = 500 + collocationScore;
    } else {
      // MATURE - low priority
      category = 'mature';
      priority = 100 + collocationScore;
    }

    return {
      ...entry,
      category,
      priority,
      progress,
    };
  });

  // Filter out nulls (words with no matches in study list)
  const withMatches = scored.filter(s => s !== null);

  // Sort by priority (descending)
  withMatches.sort((a, b) => b.priority - a.priority);

  // Debug: Log SRS selection breakdown
  const categories = { failed: 0, learning: 0, due: 0, young: 0, mature: 0, new: 0 };
  const selected = withMatches.slice(0, count);
  selected.forEach(s => categories[s.category]++);

  // Return top N (mix of review and new words naturally sorted by priority)
  return selected.map(s => new Collocation(s));
};

/**
 * Get recommended nouns for reverse practice (noun-to-verb, noun-to-adjective)
 * Prioritizes: failed/struggling > due for review > new words
 * @param {number} count - Maximum number of nouns to return
 * @param {Set} studyListWords - Optional set of words to filter matches by
 */
export const getRecommendedPracticeNouns = async (count = 10, studyListWords = null) => {
  const allVocabulary = await storage.getAllVocabulary();
  const allCollocations = await storage.getAllCollocations();
  const allProgress = await storage.getAllWordProgress();
  const now = new Date().toISOString();

  // Create progress map for quick lookup
  const progressMap = new Map(allProgress.map(p => [p.wordId, p]));

  // Get all nouns from vocabulary
  const nouns = allVocabulary.filter(v => v.type === 'noun');

  // Score each noun based on SRS priority
  const scored = nouns.map(noun => {
    let verbMatches = 0;
    let adjectiveMatches = 0;
    let totalScore = 0;
    let totalVerbMatches = 0;
    let totalAdjectiveMatches = 0;

    // Check all collocations to see which ones pair with this noun
    for (const entry of allCollocations) {
      if (entry.matches && entry.matches.nouns) {
        const match = entry.matches.nouns.find(m => m.word === noun.japanese);
        if (match) {
          // Count ALL matches
          if (entry.type === 'verb') {
            totalVerbMatches++;
          } else if (entry.type === 'adjective') {
            totalAdjectiveMatches++;
          }

          // Only count this match for scoring if the verb/adjective is in the study list (if provided)
          const inStudyList = !studyListWords || studyListWords.has(entry.word);
          if (inStudyList) {
            totalScore += match.score;
            if (entry.type === 'verb') {
              verbMatches++;
            } else if (entry.type === 'adjective') {
              adjectiveMatches++;
            }
          }
        }
      }
    }

    const matchCount = verbMatches + adjectiveMatches;
    const totalMatchCount = totalVerbMatches + totalAdjectiveMatches;

    // Skip nouns with no matches at all
    if (totalMatchCount === 0) {
      return null;
    }

    const progress = progressMap.get(noun.japanese);

    if (!progress) {
      // NEW word - HIGHEST priority (learn new words first, sorted by frequency)
      return {
        word: noun.japanese,
        japanese: noun.japanese,
        reading: noun.reading,
        english: noun.english,
        type: 'noun',
        matchCount,
        verbMatches,
        adjectiveMatches,
        totalVerbMatches,
        totalAdjectiveMatches,
        category: 'new',
        priority: 20000 + totalScore,
      };
    }

    const interval = progress.interval || 0;
    const correctCount = progress.correctCount || 0;
    const level = progress.level || 0;
    const isDue = progress.nextReview && progress.nextReview <= now;

    // Calculate SRS priority
    let priority = 0;
    let category = 'mature';

    if (interval === 0 || correctCount === 0) {
      // FAILED - second highest priority
      category = 'failed';
      priority = 10000 + totalScore;
    } else if (correctCount < 3 || interval < 3) {
      // LEARNING (struggling) - high priority, sorted by struggle level
      category = 'learning';
      priority = 5000 + (3 - correctCount) * 1000 + totalScore;
    } else if (isDue) {
      // DUE FOR REVIEW - high priority based on how overdue
      const daysOverdue = (new Date() - new Date(progress.nextReview)) / (1000 * 60 * 60 * 24);
      category = 'due';
      priority = 2000 + daysOverdue * 100 + totalScore;
    } else if (level < 5) {
      // YOUNG - medium-low priority
      category = 'young';
      priority = 500 + totalScore;
    } else {
      // MATURE - low priority
      category = 'mature';
      priority = 100 + totalScore;
    }

    return {
      word: noun.japanese,
      japanese: noun.japanese,
      reading: noun.reading,
      english: noun.english,
      type: 'noun',
      matchCount,
      verbMatches,
      adjectiveMatches,
      totalVerbMatches,
      totalAdjectiveMatches,
      category,
      priority,
      progress,
    };
  });

  // Filter out nulls (nouns with no matches)
  const withMatches = scored.filter(n => n !== null);

  // Sort by priority (descending)
  withMatches.sort((a, b) => b.priority - a.priority);

  // Debug: Log SRS selection breakdown
  const categories = { failed: 0, learning: 0, due: 0, young: 0, mature: 0, new: 0 };
  const selected = withMatches.slice(0, count);
  selected.forEach(s => categories[s.category]++);

  // Return top N
  return selected;
};

/**
 * Get SRS statistics for a JLPT level
 * @param {string} level - 'n5' or 'n54'
 * @param {Set} studyListWords - Set of words in this level
 * @returns {Promise<Object>} Statistics object
 */
export const getSRSStatisticsForLevel = async (level, studyListWords) => {
  const allProgress = await storage.getAllWordProgress();
  const allVocabulary = await storage.getAllVocabulary();
  const allCollocationProgress = await storage.getAllCollocationProgress();

  // Filter vocabulary by study list
  const levelVocabulary = allVocabulary.filter(v => studyListWords.has(v.japanese));

  // Create progress map for quick lookup (main word progress)
  const progressMap = new Map(allProgress.map(p => [p.wordId, p]));

  // Create map of word -> correct answer count from collocation pairs
  const wordCorrectCount = new Map();
  for (const collocationProg of allCollocationProgress) {
    if (collocationProg.pairId && (collocationProg.correct > 0 || collocationProg.incorrect > 0)) {
      const [word1, word2] = collocationProg.pairId.split('|');
      const correctCount = collocationProg.correct || 0;

      // Add correct count to both words in the pair
      wordCorrectCount.set(word1, (wordCorrectCount.get(word1) || 0) + correctCount);
      wordCorrectCount.set(word2, (wordCorrectCount.get(word2) || 0) + correctCount);
    }
  }

  // Initialize stats
  const stats = {
    total: levelVocabulary.length,
    practiced: 0,
    new: 0,
    learning: 0, // < 3 correct
    young: 0, // 3-5 correct
    mature: 0, // 6-10 correct
    mastered: 0, // > 10 correct
    byType: {
      noun: { total: 0, practiced: 0 },
      verb: { total: 0, practiced: 0 },
      adjective: { total: 0, practiced: 0 },
    },
  };

  // Calculate statistics
  for (const word of levelVocabulary) {
    const progress = progressMap.get(word.japanese);
    const type = word.type;

    // Count by type
    if (stats.byType[type]) {
      stats.byType[type].total++;
    }

    // Calculate effective correct count based on practice type
    let effectiveCorrectCount = 0;

    if (progress && progress.reviewCount > 0) {
      // Word has been practiced as MAIN WORD - use main word's correct count only
      // This prevents inflating the count when multiple collocations are answered in one session
      effectiveCorrectCount = progress.correctCount || 0;
    } else if (wordCorrectCount.has(word.japanese)) {
      // Word has ONLY been seen as collocation answer - use collocation correct count
      effectiveCorrectCount = wordCorrectCount.get(word.japanese);
    }

    // Word is "practiced" if it has progress OR appears in collocation pairs
    const hasCollocationProgress = wordCorrectCount.has(word.japanese) ||
      allCollocationProgress.some(cp => {
        if (!cp.pairId) return false;
        const [w1, w2] = cp.pairId.split('|');
        return (w1 === word.japanese || w2 === word.japanese) &&
               ((cp.correct || 0) + (cp.incorrect || 0) > 0);
      });
    const isPracticed = progress || hasCollocationProgress;

    if (isPracticed) {
      stats.practiced++;
      if (stats.byType[type]) {
        stats.byType[type].practiced++;
      }

      // Categorize by consecutive correct count (SRS progression)
      if (effectiveCorrectCount < 3) {
        stats.learning++;
      } else if (effectiveCorrectCount <= 5) {
        stats.young++;
      } else if (effectiveCorrectCount <= 10) {
        stats.mature++;
      } else {
        stats.mastered++;
      }
    } else {
      stats.new++;
    }
  }

  // Calculate percentages
  stats.practicedPercentage = stats.total > 0 ? Math.round((stats.practiced / stats.total) * 100) : 0;
  stats.masteryPercentage = stats.total > 0 ? Math.round(((stats.young + stats.mature + stats.mastered) / stats.total) * 100) : 0;

  return stats;
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
  getSRSStatisticsForLevel,
};
