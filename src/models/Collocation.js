/**
 * Collocation Model
 *
 * Represents a word with its collocation matches (verb/adjective with nouns).
 */

export class Collocation {
  constructor(data) {
    this.word = data.word;
    this.type = data.type;
    this.reading = data.reading;
    this.english = data.english;
    this.matches = data.matches || {};
  }

  /**
   * Get all noun matches for this word
   */
  getNounMatches() {
    return this.matches.nouns || [];
  }

  /**
   * Get noun matches filtered by score
   */
  getNounMatchesByScore(minScore) {
    return this.getNounMatches().filter(match => match.score >= minScore);
  }

  /**
   * Get very common matches (score 3)
   */
  getVeryCommonMatches() {
    return this.getNounMatchesByScore(3);
  }

  /**
   * Get common matches (score 2+)
   */
  getCommonMatches() {
    return this.getNounMatchesByScore(2);
  }

  /**
   * Check if a noun is a valid match
   */
  isValidMatch(nounJapanese) {
    return this.getNounMatches().some(match => match.word === nounJapanese);
  }

  /**
   * Get score for a specific noun match
   */
  getMatchScore(nounJapanese) {
    const match = this.getNounMatches().find(m => m.word === nounJapanese);
    return match ? match.score : 0;
  }

  /**
   * Get total number of matches
   */
  getTotalMatches() {
    return this.getNounMatches().length;
  }

  /**
   * Convert to plain object
   */
  toJSON() {
    return {
      word: this.word,
      type: this.type,
      reading: this.reading,
      english: this.english,
      matches: this.matches,
    };
  }
}

export default Collocation;
