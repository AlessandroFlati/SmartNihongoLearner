/**
 * SRS (Spaced Repetition System) Service
 *
 * Implements Anki-style SM-2 algorithm for scheduling reviews.
 * All scheduling is browser-based with no server required.
 */

import { WordProgress } from '../models/Progress';
import storage from './storage';

// SRS Configuration (based on Anki defaults)
const SRS_CONFIG = {
  INITIAL_INTERVAL: 1,        // 1 day
  GRADUATING_INTERVAL: 3,     // 3 days
  EASY_INTERVAL: 7,           // 7 days
  STARTING_EASE: 2.5,         // Starting ease factor
  MIN_EASE: 1.3,              // Minimum ease factor
  EASE_BONUS: 0.15,           // Ease increase for "Easy"
  EASE_PENALTY: 0.20,         // Ease decrease for "Hard"/"Again"
  HARD_INTERVAL_MULTIPLIER: 1.2,
  GOOD_INTERVAL_MULTIPLIER: 2.5,
  EASY_INTERVAL_MULTIPLIER: 3.0,
};

/**
 * Calculate next review date based on answer quality
 *
 * @param {WordProgress} progress - Current progress data
 * @param {string} answer - Quality of answer: 'again', 'hard', 'good', 'easy'
 * @returns {WordProgress} Updated progress data
 */
export const calculateNextReview = (progress, answer) => {
  const now = new Date();
  let newProgress = { ...progress };

  // Increment review count
  newProgress.reviewCount = (progress.reviewCount || 0) + 1;
  newProgress.lastReview = now.toISOString();

  switch (answer) {
    case 'again':
      // Failed - reset to learning
      newProgress.incorrectCount = (progress.incorrectCount || 0) + 1;
      newProgress.level = Math.max(0, progress.level - 2);
      newProgress.interval = SRS_CONFIG.INITIAL_INTERVAL;
      newProgress.easeFactor = Math.max(
        SRS_CONFIG.MIN_EASE,
        progress.easeFactor - SRS_CONFIG.EASE_PENALTY
      );
      break;

    case 'hard':
      // Difficult - small interval increase
      newProgress.correctCount = (progress.correctCount || 0) + 1;
      newProgress.level = Math.min(progress.level + 0.5, 10);
      newProgress.interval = Math.max(
        SRS_CONFIG.INITIAL_INTERVAL,
        progress.interval * SRS_CONFIG.HARD_INTERVAL_MULTIPLIER
      );
      newProgress.easeFactor = Math.max(
        SRS_CONFIG.MIN_EASE,
        progress.easeFactor - SRS_CONFIG.EASE_PENALTY
      );
      break;

    case 'good':
      // Correct - normal interval increase
      newProgress.correctCount = (progress.correctCount || 0) + 1;
      newProgress.level = Math.min(progress.level + 1, 10);

      if (progress.level === 0) {
        // First time seeing this word
        newProgress.interval = SRS_CONFIG.GRADUATING_INTERVAL;
      } else {
        newProgress.interval = Math.ceil(
          progress.interval * progress.easeFactor
        );
      }
      break;

    case 'easy':
      // Very easy - large interval increase
      newProgress.correctCount = (progress.correctCount || 0) + 1;
      newProgress.level = Math.min(progress.level + 2, 10);

      if (progress.level === 0) {
        // First time - jump to easy interval
        newProgress.interval = SRS_CONFIG.EASY_INTERVAL;
      } else {
        newProgress.interval = Math.ceil(
          progress.interval * progress.easeFactor * SRS_CONFIG.EASY_INTERVAL_MULTIPLIER
        );
      }

      newProgress.easeFactor = Math.min(
        4.0,
        progress.easeFactor + SRS_CONFIG.EASE_BONUS
      );
      break;

    default:
      throw new Error(`Invalid answer: ${answer}`);
  }

  // Calculate next review date
  const nextReviewDate = new Date(now);
  nextReviewDate.setDate(nextReviewDate.getDate() + newProgress.interval);
  newProgress.nextReview = nextReviewDate.toISOString();

  return newProgress;
};

/**
 * Get or create progress for a word
 */
export const getWordProgress = async (wordId) => {
  let progress = await storage.getWordProgress(wordId);

  if (!progress) {
    // Create new progress entry
    progress = new WordProgress({
      wordId,
      level: 0,
      easeFactor: SRS_CONFIG.STARTING_EASE,
      interval: 0,
      nextReview: new Date().toISOString(),
      lastReview: null,
      reviewCount: 0,
      correctCount: 0,
      incorrectCount: 0,
    });
  } else {
    progress = new WordProgress(progress);
  }

  return progress;
};

/**
 * Record a review for a word
 */
export const recordReview = async (wordId, answer) => {
  const currentProgress = await getWordProgress(wordId);
  const updatedProgress = calculateNextReview(currentProgress, answer);

  await storage.saveWordProgress(wordId, updatedProgress);

  // Update global statistics
  await updateStatistics(answer === 'good' || answer === 'easy');

  return updatedProgress;
};

/**
 * Get all words due for review
 */
export const getWordsDueForReview = async () => {
  const dueWords = await storage.getWordsDueForReview();
  return dueWords;
};

/**
 * Get review queue sorted by priority
 * Priority: failed cards > learning > young > mature
 */
export const getReviewQueue = async () => {
  const dueWords = await getWordsDueForReview();

  // Sort by priority
  dueWords.sort((a, b) => {
    // Failed cards (level 0-1) come first
    if (a.level < 2 && b.level >= 2) return -1;
    if (a.level >= 2 && b.level < 2) return 1;

    // Then by level (lower levels = higher priority)
    if (a.level !== b.level) return a.level - b.level;

    // Then by next review date (earlier = higher priority)
    return new Date(a.nextReview) - new Date(b.nextReview);
  });

  return dueWords;
};

/**
 * Update global statistics
 */
const updateStatistics = async (correct) => {
  const stats = await storage.getStatistics();

  stats.totalReviews = (stats.totalReviews || 0) + 1;

  if (correct) {
    stats.correctAnswers = (stats.correctAnswers || 0) + 1;
    stats.streak = (stats.streak || 0) + 1;
    stats.longestStreak = Math.max(stats.longestStreak || 0, stats.streak);
  } else {
    stats.incorrectAnswers = (stats.incorrectAnswers || 0) + 1;
    stats.streak = 0;
  }

  // Track study days
  const today = new Date().toDateString();
  const lastStudyDay = stats.lastStudyDay;

  if (lastStudyDay !== today) {
    stats.studyDays = (stats.studyDays || 0) + 1;
    stats.lastStudyDay = today;
  }

  await storage.saveStatistics(stats);
};

/**
 * Get learning statistics
 */
export const getLearningStats = async () => {
  const allProgress = await storage.getAllWordProgress();
  const globalStats = await storage.getStatistics();

  const stats = {
    totalWords: allProgress.length,
    newWords: 0,
    learning: 0,
    young: 0,
    mature: 0,
    mastered: 0,
    dueToday: 0,
    averageAccuracy: 0,
    ...globalStats,
  };

  let totalAccuracy = 0;

  allProgress.forEach(p => {
    const progress = new WordProgress(p);

    // Count by mastery level
    const mastery = progress.getMasteryLevel();
    if (mastery === 'new') stats.newWords++;
    else if (mastery === 'learning') stats.learning++;
    else if (mastery === 'young') stats.young++;
    else if (mastery === 'mature') stats.mature++;

    if (progress.isMastered()) stats.mastered++;
    if (progress.isDue()) stats.dueToday++;

    totalAccuracy += progress.getAccuracy();
  });

  if (allProgress.length > 0) {
    stats.averageAccuracy = totalAccuracy / allProgress.length;
  }

  return stats;
};

export default {
  calculateNextReview,
  getWordProgress,
  recordReview,
  getWordsDueForReview,
  getReviewQueue,
  getLearningStats,
  SRS_CONFIG,
};
