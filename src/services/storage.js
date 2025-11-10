/**
 * Storage Service - Browser-based persistence (SERVERLESS)
 *
 * Uses LocalStorage for settings and IndexedDB for larger datasets.
 * All data persists across browser sessions (even when shut down).
 */

import Dexie from 'dexie';
import CryptoJS from 'crypto-js';

// IndexedDB setup using Dexie
const db = new Dexie('SmartNihongoLearner');

db.version(1).stores({
  vocabulary: 'id, japanese, type, frequency',
  collocations: '++id, word, type',
  wordProgress: 'wordId, level, nextReview',
  collocationProgress: 'pairId, correct, incorrect',
  settings: 'key',
});

// Encryption key for API key storage (browser fingerprint)
const getEncryptionKey = () => {
  return navigator.userAgent + navigator.language;
};

// ============================================================================
// API Key Management
// ============================================================================

export const storage = {
  /**
   * Save encrypted OpenAI API key to LocalStorage
   */
  setApiKey: (key) => {
    const encrypted = CryptoJS.AES.encrypt(key, getEncryptionKey()).toString();
    localStorage.setItem('openai_key', encrypted);
  },

  /**
   * Retrieve and decrypt OpenAI API key from LocalStorage
   */
  getApiKey: () => {
    const encrypted = localStorage.getItem('openai_key');
    if (!encrypted) return null;
    try {
      const decrypted = CryptoJS.AES.decrypt(encrypted, getEncryptionKey());
      return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
      console.error('Failed to decrypt API key:', error);
      return null;
    }
  },

  /**
   * Remove API key from LocalStorage
   */
  clearApiKey: () => {
    localStorage.removeItem('openai_key');
  },

  // ============================================================================
  // Settings Management
  // ============================================================================

  /**
   * Save user settings to IndexedDB
   */
  saveSetting: async (key, value) => {
    await db.settings.put({ key, value });
  },

  /**
   * Load user setting from IndexedDB
   */
  getSetting: async (key, defaultValue = null) => {
    const record = await db.settings.get(key);
    return record ? record.value : defaultValue;
  },

  /**
   * Get all settings
   */
  getAllSettings: async () => {
    const records = await db.settings.toArray();
    return records.reduce((acc, { key, value }) => {
      acc[key] = value;
      return acc;
    }, {});
  },

  // ============================================================================
  // Vocabulary Data Management
  // ============================================================================

  /**
   * Initialize vocabulary data from JSON (first load)
   */
  initializeVocabulary: async (vocabularyArray) => {
    const count = await db.vocabulary.count();
    if (count === 0) {
      await db.vocabulary.bulkAdd(vocabularyArray);
      console.log(`Initialized ${vocabularyArray.length} vocabulary words`);
    }
  },

  /**
   * Get all vocabulary
   */
  getAllVocabulary: async () => {
    return await db.vocabulary.toArray();
  },

  /**
   * Get vocabulary by type
   */
  getVocabularyByType: async (type) => {
    return await db.vocabulary.where('type').equals(type).toArray();
  },

  /**
   * Get vocabulary by ID
   */
  getVocabularyById: async (id) => {
    return await db.vocabulary.get(id);
  },

  // ============================================================================
  // Collocation Data Management
  // ============================================================================

  /**
   * Initialize collocation data from JSON (first load)
   */
  initializeCollocations: async (collocationsData) => {
    const count = await db.collocations.count();
    if (count === 0) {
      // Store collocations indexed by word for quick lookup
      const collocationRecords = [];

      for (const [word, data] of Object.entries(collocationsData.words)) {
        collocationRecords.push({
          word,
          type: data.type,
          reading: data.reading,
          english: data.english,
          matches: data.matches,
        });
      }

      await db.collocations.bulkAdd(collocationRecords);
      console.log(`Initialized ${collocationRecords.length} collocation entries`);
    }
  },

  /**
   * Get collocation data for a word
   */
  getCollocationsByWord: async (word) => {
    return await db.collocations.where('word').equals(word).first();
  },

  /**
   * Get all collocations
   */
  getAllCollocations: async () => {
    return await db.collocations.toArray();
  },

  // ============================================================================
  // Progress Tracking - Word Level
  // ============================================================================

  /**
   * Save word progress (SRS data)
   */
  saveWordProgress: async (wordId, progressData) => {
    await db.wordProgress.put({
      wordId,
      ...progressData,
      lastUpdated: new Date().toISOString(),
    });
  },

  /**
   * Get word progress
   */
  getWordProgress: async (wordId) => {
    return await db.wordProgress.get(wordId);
  },

  /**
   * Get all word progress
   */
  getAllWordProgress: async () => {
    return await db.wordProgress.toArray();
  },

  /**
   * Get words due for review
   */
  getWordsDueForReview: async () => {
    const now = new Date().toISOString();
    return await db.wordProgress.where('nextReview').belowOrEqual(now).toArray();
  },

  // ============================================================================
  // Progress Tracking - Collocation Pairs
  // ============================================================================

  /**
   * Save collocation pair progress
   */
  saveCollocationProgress: async (pairId, progressData) => {
    const existing = await db.collocationProgress.get(pairId);

    if (existing) {
      await db.collocationProgress.update(pairId, {
        ...existing,
        ...progressData,
        lastSeen: new Date().toISOString(),
      });
    } else {
      await db.collocationProgress.put({
        pairId,
        correct: 0,
        incorrect: 0,
        ...progressData,
        lastSeen: new Date().toISOString(),
      });
    }
  },

  /**
   * Get collocation pair progress
   */
  getCollocationProgress: async (pairId) => {
    return await db.collocationProgress.get(pairId);
  },

  /**
   * Get all collocation progress
   */
  getAllCollocationProgress: async () => {
    return await db.collocationProgress.toArray();
  },

  // ============================================================================
  // Statistics
  // ============================================================================

  /**
   * Save global statistics
   */
  saveStatistics: async (stats) => {
    await db.settings.put({
      key: 'statistics',
      value: {
        ...stats,
        lastUpdated: new Date().toISOString(),
      }
    });
  },

  /**
   * Get global statistics
   */
  getStatistics: async () => {
    const record = await db.settings.get('statistics');
    return record ? record.value : {
      totalReviews: 0,
      correctAnswers: 0,
      incorrectAnswers: 0,
      streak: 0,
      longestStreak: 0,
      studyDays: 0,
    };
  },

  // ============================================================================
  // Data Export/Import (Backup)
  // ============================================================================

  /**
   * Export all user data as JSON (for backup)
   */
  exportAllData: async () => {
    const data = {
      exportedAt: new Date().toISOString(),
      version: '1.0.0',
      wordProgress: await db.wordProgress.toArray(),
      collocationProgress: await db.collocationProgress.toArray(),
      settings: await db.settings.toArray(),
      statistics: await storage.getStatistics(),
    };
    return JSON.stringify(data, null, 2);
  },

  /**
   * Import user data from JSON (restore backup)
   */
  importAllData: async (jsonData) => {
    try {
      const data = JSON.parse(jsonData);

      // Clear existing progress
      await db.wordProgress.clear();
      await db.collocationProgress.clear();

      // Import data
      if (data.wordProgress) {
        await db.wordProgress.bulkAdd(data.wordProgress);
      }
      if (data.collocationProgress) {
        await db.collocationProgress.bulkAdd(data.collocationProgress);
      }
      if (data.settings) {
        for (const setting of data.settings) {
          await db.settings.put(setting);
        }
      }

      console.log('Data import successful');
      return true;
    } catch (error) {
      console.error('Failed to import data:', error);
      return false;
    }
  },

  /**
   * Clear all user data (reset app)
   */
  clearAllData: async () => {
    await db.wordProgress.clear();
    await db.collocationProgress.clear();
    await db.settings.clear();
    localStorage.clear();
    console.log('All user data cleared');
  },

  // ============================================================================
  // Database Info
  // ============================================================================

  /**
   * Get database statistics
   */
  getDatabaseInfo: async () => {
    return {
      vocabularyCount: await db.vocabulary.count(),
      collocationsCount: await db.collocations.count(),
      wordProgressCount: await db.wordProgress.count(),
      collocationProgressCount: await db.collocationProgress.count(),
    };
  },
};

export default storage;
