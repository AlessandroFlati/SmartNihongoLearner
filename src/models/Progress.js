/**
 * Progress Model
 *
 * Represents learning progress for a vocabulary word or collocation pair.
 * Based on Anki's SM-2 algorithm.
 */

export class WordProgress {
  constructor(data = {}) {
    this.wordId = data.wordId;
    this.level = data.level || 0;  // 0 = new, 1-2 = learning, 3-5 = young, 6+ = mature
    this.easeFactor = data.easeFactor || 2.5;
    this.interval = data.interval || 0;  // Days until next review
    this.nextReview = data.nextReview || new Date().toISOString();
    this.lastReview = data.lastReview || null;
    this.reviewCount = data.reviewCount || 0;
    this.correctCount = data.correctCount || 0;
    this.incorrectCount = data.incorrectCount || 0;
  }

  /**
   * Check if this word is due for review
   */
  isDue() {
    return new Date(this.nextReview) <= new Date();
  }

  /**
   * Get mastery level category
   */
  getMasteryLevel() {
    if (this.level === 0) return 'new';
    if (this.level <= 2) return 'learning';
    if (this.level <= 5) return 'young';
    return 'mature';
  }

  /**
   * Get accuracy percentage
   */
  getAccuracy() {
    if (this.reviewCount === 0) return 0;
    return (this.correctCount / this.reviewCount) * 100;
  }

  /**
   * Check if word is mastered (level 6+)
   */
  isMastered() {
    return this.level >= 6;
  }

  /**
   * Convert to plain object for storage
   */
  toJSON() {
    return {
      wordId: this.wordId,
      level: this.level,
      easeFactor: this.easeFactor,
      interval: this.interval,
      nextReview: this.nextReview,
      lastReview: this.lastReview,
      reviewCount: this.reviewCount,
      correctCount: this.correctCount,
      incorrectCount: this.incorrectCount,
    };
  }
}

export class CollocationProgress {
  constructor(data = {}) {
    this.pairId = data.pairId;  // Format: "verb|noun" or "adjective|noun"
    this.correct = data.correct || 0;
    this.incorrect = data.incorrect || 0;
    this.lastSeen = data.lastSeen || null;
    this.strength = data.strength || 0;  // 0-100 strength score
  }

  /**
   * Get total attempts
   */
  getTotalAttempts() {
    return this.correct + this.incorrect;
  }

  /**
   * Get accuracy percentage
   */
  getAccuracy() {
    const total = this.getTotalAttempts();
    if (total === 0) return 0;
    return (this.correct / total) * 100;
  }

  /**
   * Update strength based on accuracy
   */
  updateStrength() {
    const accuracy = this.getAccuracy();
    const attempts = this.getTotalAttempts();

    // Strength increases with both accuracy and number of attempts
    // Max strength when accuracy > 80% and attempts > 5
    if (accuracy >= 80 && attempts >= 5) {
      this.strength = 100;
    } else if (accuracy >= 60 && attempts >= 3) {
      this.strength = 70;
    } else if (accuracy >= 40 && attempts >= 2) {
      this.strength = 40;
    } else {
      this.strength = Math.min(accuracy, 30);
    }

    return this.strength;
  }

  /**
   * Record a correct answer
   */
  recordCorrect() {
    this.correct++;
    this.lastSeen = new Date().toISOString();
    this.updateStrength();
  }

  /**
   * Record an incorrect answer
   */
  recordIncorrect() {
    this.incorrect++;
    this.lastSeen = new Date().toISOString();
    this.updateStrength();
  }

  /**
   * Convert to plain object for storage
   */
  toJSON() {
    return {
      pairId: this.pairId,
      correct: this.correct,
      incorrect: this.incorrect,
      lastSeen: this.lastSeen,
      strength: this.strength,
    };
  }
}

export default { WordProgress, CollocationProgress };
