/**
 * Vocabulary Model
 *
 * Represents a single vocabulary word with all its properties.
 */

export class VocabularyWord {
  constructor(data) {
    this.id = data.id;
    this.japanese = data.japanese;
    this.reading = data.reading;
    this.english = data.english;
    this.type = data.type;
    this.frequency = data.frequency;
  }

  /**
   * Check if this is a noun
   */
  isNoun() {
    return this.type === 'noun';
  }

  /**
   * Check if this is a verb
   */
  isVerb() {
    return this.type === 'verb';
  }

  /**
   * Check if this is an adjective
   */
  isAdjective() {
    return this.type === 'adjective';
  }

  /**
   * Get frequency category
   */
  getFrequencyCategory() {
    if (this.frequency >= 6.0) return 'very-common';
    if (this.frequency >= 4.0) return 'common';
    return 'less-common';
  }

  /**
   * Convert to plain object
   */
  toJSON() {
    return {
      id: this.id,
      japanese: this.japanese,
      reading: this.reading,
      english: this.english,
      type: this.type,
      frequency: this.frequency,
    };
  }
}

export default VocabularyWord;
