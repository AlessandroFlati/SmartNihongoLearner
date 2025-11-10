/**
 * Data Loader Service
 *
 * Loads vocabulary and collocation data from JSON files.
 * Handles initial data loading and caching in IndexedDB.
 */

import storage from './storage';

/**
 * Load vocabulary data from JSON file
 */
export const loadVocabulary = async () => {
  try {
    const response = await fetch('/data/vocabulary.json');
    if (!response.ok) {
      throw new Error(`Failed to load vocabulary: ${response.statusText}`);
    }
    const data = await response.json();
    return data.vocabulary;
  } catch (error) {
    console.error('Error loading vocabulary:', error);
    throw error;
  }
};

/**
 * Load collocation data from JSON file
 */
export const loadCollocations = async () => {
  try {
    const response = await fetch('/data/collocations_complete.json');
    if (!response.ok) {
      throw new Error(`Failed to load collocations: ${response.statusText}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error loading collocations:', error);
    throw error;
  }
};

/**
 * Initialize all data (vocabulary and collocations)
 * This should be called once when the app first loads
 */
export const initializeAllData = async () => {
  try {
    // Check if data is already initialized
    const dbInfo = await storage.getDatabaseInfo();

    if (dbInfo.vocabularyCount === 0) {
      console.log('Initializing vocabulary data...');
      const vocabulary = await loadVocabulary();
      await storage.initializeVocabulary(vocabulary);
    } else {
      console.log('Vocabulary already initialized');
    }

    if (dbInfo.collocationsCount === 0) {
      console.log('Initializing collocation data...');
      const collocations = await loadCollocations();
      await storage.initializeCollocations(collocations);
    } else {
      console.log('Collocations already initialized');
    }

    console.log('Data initialization complete');
    return true;
  } catch (error) {
    console.error('Failed to initialize data:', error);
    return false;
  }
};

/**
 * Get vocabulary statistics
 */
export const getVocabularyStats = async () => {
  const vocab = await storage.getAllVocabulary();

  const stats = {
    total: vocab.length,
    byType: {},
    averageFrequency: 0,
  };

  let totalFreq = 0;
  vocab.forEach(word => {
    stats.byType[word.type] = (stats.byType[word.type] || 0) + 1;
    totalFreq += word.frequency || 0;
  });

  stats.averageFrequency = totalFreq / vocab.length;

  return stats;
};

/**
 * Get collocation statistics
 */
export const getCollocationStats = async () => {
  const collocations = await storage.getAllCollocations();

  const stats = {
    total: collocations.length,
    byType: {},
    totalPairs: 0,
  };

  collocations.forEach(entry => {
    stats.byType[entry.type] = (stats.byType[entry.type] || 0) + 1;

    if (entry.matches && entry.matches.nouns) {
      stats.totalPairs += entry.matches.nouns.length;
    }
  });

  return stats;
};

export default {
  loadVocabulary,
  loadCollocations,
  initializeAllData,
  getVocabularyStats,
  getCollocationStats,
};
