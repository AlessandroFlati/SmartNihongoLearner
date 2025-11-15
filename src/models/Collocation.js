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
   * Get all verb matches for this word (for nouns)
   */
  getVerbMatches() {
    return this.matches.verbs || [];
  }

  /**
   * Get all adjective matches for this word (for nouns)
   */
  getAdjectiveMatches() {
    return this.matches.adjectives || [];
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
   * Get limited noun matches for gameplay
   *
   * Applies smart limiting based on total match count:
   * - 30+ matches → limit to 15 best matches
   * - 20-29 matches → limit to 20 best matches
   * - 15-19 matches → keep all
   * - <15 matches → keep all
   *
   * Prioritizes higher scores: score 3, then 2, then 1
   */
  getLimitedNounMatches() {
    const allMatches = this.getNounMatches();
    const total = allMatches.length;

    // Determine limit based on total count
    let limit;
    if (total >= 30) {
      limit = 15;
    } else if (total >= 20) {
      limit = 20;
    } else {
      // Keep all for reasonable counts
      return allMatches;
    }

    // Sort by score (descending), then alphabetically for consistency
    const sorted = [...allMatches].sort((a, b) => {
      if (b.score !== a.score) {
        return b.score - a.score; // Higher score first
      }
      return a.word.localeCompare(b.word); // Alphabetical for same score
    });

    // Return top N matches
    return sorted.slice(0, limit);
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
