# Implementation Plan - Smart Nihongo Learner

This document provides detailed technical specifications and implementation guidelines for the Smart Nihongo Learner project.

## Table of Contents

1. [Phase 1: Data Preparation](#phase-1-data-preparation)
2. [Phase 2: Core Infrastructure](#phase-2-core-infrastructure)
3. [Phase 3: SRS System](#phase-3-srs-system)
4. [Phase 4: Game 1 - What Could Match](#phase-4-game-1---what-could-match)
5. [Phase 5: Game 2 - Fill the Blanks](#phase-5-game-2---fill-the-blanks)
6. [Phase 6: UI/UX Polish](#phase-6-uiux-polish)
7. [Technical Specifications](#technical-specifications)
8. [API Usage & Cost Optimization](#api-usage--cost-optimization)

---

## Phase 1: Data Preparation

**Goal**: Create pre-computed collocation database from frequency resources and study list.

### 1.1 Study List CSV Parser

**File**: `data-preparation/parsers/csv-parser.js`

```javascript
// Read and validate study list CSV
// Validate required fields: japanese, reading, english, type
// Filter by word type: noun, verb, adjective (exclude 'other')
// Output: Structured vocabulary array
```

**Validation Rules**:
- Required fields must not be empty
- Word type must be one of: `noun`, `verb`, `adjective`, `other`
- Japanese field must contain valid Japanese characters
- No duplicate entries (by japanese + type combination)

**Output Schema**:
```json
{
  "vocabulary": [
    {
      "id": "uuid",
      "japanese": "のむ",
      "reading": "nomu",
      "english": "to drink",
      "type": "verb"
    }
  ]
}
```

### 1.2 Kanshudo Web Scraper

**File**: `data-preparation/scrapers/kanshudo-scraper.js`

**Target**: https://www.kanshudo.com/collections/routledge

**Strategy**:
1. Respect robots.txt and rate limiting (1 request/2 seconds)
2. Extract word pairs and their frequency scores
3. Store raw HTML for future re-parsing if needed
4. Cache results to avoid repeated scraping

**Technologies**:
- Puppeteer (for JavaScript-rendered content)
- Cheerio (for parsing HTML)
- fs/promises (for file I/O)

**Data to Extract**:
- Word 1 (Japanese)
- Word 2 (Japanese)
- Frequency score
- Context/example sentence (if available)

**Output**: `data-preparation/output/kanshudo-raw.json`

### 1.3 Collocation Generation with Claude

**File**: `data-preparation/generators/collocation-generator.js`

**Approach**:
This is an iterative process using Claude Code locally (not API calls) to analyze the study list and frequency data to generate meaningful collocations.

**Process**:
1. Load study list vocabulary
2. Load frequency data from Kanshudo
3. For each verb in study list:
   - Find compatible nouns from study list
   - Check against frequency data
   - Score compatibility (high/medium/low)
4. For each adjective in study list:
   - Find compatible nouns from study list
   - Score compatibility
5. For each noun in study list:
   - Find compatible verbs and adjectives
   - Score compatibility

**Compatibility Scoring**:
- **High (3)**: Common collocation in frequency data + makes semantic sense
- **Medium (2)**: Not in frequency data but semantically valid
- **Low (1)**: Rare but possible combination
- **None (0)**: Invalid combination

**Manual Review**:
- Output candidates for human review
- Iterate on edge cases
- Build curated list over multiple passes

**Output**: `data-preparation/output/collocations-raw.json`

### 1.4 Database Optimization

**File**: `data-preparation/optimizers/database-optimizer.js`

**Goal**: Convert raw collocation data into efficient lookup structure.

**Strategy 1: Adjacency List**
```json
{
  "version": "1.0.0",
  "generatedAt": "2025-11-08T00:00:00Z",
  "index": {
    "のむ": {
      "word": "のむ",
      "reading": "nomu",
      "english": "to drink",
      "type": "verb",
      "matches": [
        {"word": "水", "score": 3},
        {"word": "コーヒー", "score": 3},
        {"word": "ビール", "score": 3}
      ]
    }
  }
}
```

**Strategy 2: Matrix Format** (if lookup performance is critical)
```json
{
  "version": "1.0.0",
  "words": ["のむ", "水", "コーヒー", "食べる", "ごはん"],
  "matrix": [
    [0, 3, 3, 0, 0],  // のむ
    [3, 0, 0, 0, 0],  // 水
    [3, 0, 0, 0, 0],  // コーヒー
    [0, 0, 0, 0, 3],  // 食べる
    [0, 0, 0, 3, 0]   // ごはん
  ]
}
```

**Recommendation**: Use Adjacency List for better readability and smaller file size. Matrix is only needed if we have 1000+ words and need O(1) lookup.

**Final Output**: `public/data/collocations.json`

---

## Phase 2: Core Infrastructure

**Goal**: Set up React application with essential services.

### 2.1 Project Initialization

```bash
npm create vite@latest . -- --template react
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install openai
npm install dexie  # For IndexedDB
npm install crypto-js  # For API key encryption
```

**Vite Configuration** (`vite.config.js`):
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
```

### 2.2 Material UI Dark Theme Setup

**File**: `src/theme.js`

```javascript
import { createTheme } from '@mui/material/styles';

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',  // Light blue for primary actions
    },
    secondary: {
      main: '#f48fb1',  // Pink for secondary actions
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    success: {
      main: '#66bb6a',  // Green for correct answers
    },
    error: {
      main: '#f44336',  // Red for incorrect answers
    },
  },
  typography: {
    fontFamily: [
      'Noto Sans JP',  // For Japanese text
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: { fontSize: '2rem' },
    h2: { fontSize: '1.5rem' },
    h3: { fontSize: '1.25rem' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',  // Disable uppercase
        },
      },
    },
  },
});
```

### 2.3 Storage Service

**File**: `src/services/storage.js`

**Requirements**:
- LocalStorage for settings and progress (< 5MB)
- IndexedDB for large datasets using Dexie
- Encrypted API key storage
- Automatic backup/restore

**Implementation**:

```javascript
import Dexie from 'dexie';
import CryptoJS from 'crypto-js';

// IndexedDB setup
const db = new Dexie('SmartNihongoLearner');
db.version(1).stores({
  vocabulary: 'id, japanese, type',
  collocations: 'id, word1, word2, score',
  progress: 'key'
});

// API Key encryption (use browser fingerprint as key)
const getEncryptionKey = () => {
  return navigator.userAgent + navigator.language;
};

export const storage = {
  // API Key
  setApiKey: (key) => {
    const encrypted = CryptoJS.AES.encrypt(key, getEncryptionKey()).toString();
    localStorage.setItem('openai_key', encrypted);
  },

  getApiKey: () => {
    const encrypted = localStorage.getItem('openai_key');
    if (!encrypted) return null;
    const decrypted = CryptoJS.AES.decrypt(encrypted, getEncryptionKey());
    return decrypted.toString(CryptoJS.enc.Utf8);
  },

  // Progress
  saveProgress: async (data) => {
    await db.progress.put({ key: 'main', data });
  },

  loadProgress: async () => {
    const record = await db.progress.get('main');
    return record?.data || null;
  },

  // Statistics
  updateStats: (statsUpdate) => {
    const current = JSON.parse(localStorage.getItem('statistics') || '{}');
    const updated = { ...current, ...statsUpdate };
    localStorage.setItem('statistics', JSON.stringify(updated));
  }
};
```

### 2.4 Data Models

**File**: `src/models/Vocabulary.js`

```javascript
export class Vocabulary {
  constructor({ id, japanese, reading, english, type }) {
    this.id = id;
    this.japanese = japanese;
    this.reading = reading;
    this.english = english;
    this.type = type; // noun, verb, adjective
  }

  isNoun() { return this.type === 'noun'; }
  isVerb() { return this.type === 'verb'; }
  isAdjective() { return this.type === 'adjective'; }
}
```

**File**: `src/models/Collocation.js`

```javascript
export class Collocation {
  constructor({ word1, word2, score }) {
    this.word1 = word1; // Vocabulary object
    this.word2 = word2; // Vocabulary object
    this.score = score; // 1-3 compatibility score
  }

  getKey() {
    return `${this.word1.japanese}|${this.word2.japanese}`;
  }

  includes(word) {
    return this.word1.japanese === word || this.word2.japanese === word;
  }
}
```

**File**: `src/models/Progress.js`

```javascript
export class Progress {
  constructor() {
    this.wordMastery = new Map(); // word -> mastery data
    this.collocationMastery = new Map(); // pair key -> mastery data
    this.statistics = {
      totalReviews: 0,
      correctAnswers: 0,
      incorrectAnswers: 0,
      streak: 0,
      longestStreak: 0,
      startDate: new Date().toISOString()
    };
  }

  updateWordMastery(word, correct) {
    // Update SRS data for individual word
  }

  updateCollocationMastery(pair, correct) {
    // Update SRS data for word pair
  }

  getNextReview(word) {
    // Calculate next review date based on SRS
  }
}
```

### 2.5 OpenAI Service

**File**: `src/services/openai.js`

```javascript
import OpenAI from 'openai';
import { storage } from './storage';

class OpenAIService {
  constructor() {
    this.client = null;
    this.requestQueue = [];
    this.isProcessing = false;
  }

  initialize() {
    const apiKey = storage.getApiKey();
    if (!apiKey) throw new Error('API key not set');

    this.client = new OpenAI({
      apiKey,
      dangerouslyAllowBrowser: true // For client-side usage
    });
  }

  // Rate limiting: max 3 requests per minute
  async queueRequest(fn) {
    return new Promise((resolve, reject) => {
      this.requestQueue.push({ fn, resolve, reject });
      this.processQueue();
    });
  }

  async processQueue() {
    if (this.isProcessing || this.requestQueue.length === 0) return;

    this.isProcessing = true;
    const { fn, resolve, reject } = this.requestQueue.shift();

    try {
      const result = await fn();
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      setTimeout(() => {
        this.isProcessing = false;
        this.processQueue();
      }, 20000); // 20 second delay between requests
    }
  }

  async validateAnswer(word, userAnswer, validOptions) {
    return this.queueRequest(async () => {
      const response = await this.client.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are a Japanese language expert. Validate if the user\'s answer is semantically equivalent to any of the valid options, considering variations in hiragana/katakana/kanji.'
          },
          {
            role: 'user',
            content: `Word: ${word}\nUser answer: ${userAnswer}\nValid options: ${validOptions.join(', ')}\nIs the user's answer correct? Reply with only "yes" or "no".`
          }
        ],
        max_tokens: 10,
        temperature: 0
      });

      return response.choices[0].message.content.toLowerCase().includes('yes');
    });
  }

  async generateSentence(vocabulary, targetWord) {
    return this.queueRequest(async () => {
      const vocabList = vocabulary.map(v => v.japanese).join(', ');

      const response = await this.client.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are a Japanese language teacher. Generate natural Japanese sentences using only the provided vocabulary.'
          },
          {
            role: 'user',
            content: `Vocabulary: ${vocabList}\nCreate a simple Japanese sentence that includes "${targetWord}" and uses only words from the vocabulary list. Return only the sentence.`
          }
        ],
        max_tokens: 100,
        temperature: 0.7
      });

      return response.choices[0].message.content.trim();
    });
  }
}

export const openAIService = new OpenAIService();
```

---

## Phase 3: SRS System

**Goal**: Implement Anki-style spaced repetition algorithm.

### 3.1 SRS Algorithm Implementation

**File**: `src/services/srs.js`

Based on **SM-2 Algorithm** with modifications:

```javascript
export class SRSCard {
  constructor(item) {
    this.item = item; // word or collocation
    this.interval = 0; // days until next review
    this.repetitions = 0; // number of successful reviews
    this.easeFactor = 2.5; // difficulty multiplier
    this.dueDate = new Date(); // when next review is due
    this.level = 0; // mastery level (0-10)
  }

  review(quality) {
    // quality: 0-5 (0=complete fail, 5=perfect)

    if (quality < 3) {
      // Failed review - reset
      this.repetitions = 0;
      this.interval = 1;
      this.level = Math.max(0, this.level - 1);
    } else {
      // Successful review
      this.repetitions++;
      this.level = Math.min(10, this.level + 1);

      if (this.repetitions === 1) {
        this.interval = 1;
      } else if (this.repetitions === 2) {
        this.interval = 6;
      } else {
        this.interval = Math.round(this.interval * this.easeFactor);
      }

      // Adjust ease factor
      this.easeFactor = Math.max(1.3, this.easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)));
    }

    // Set next review date
    this.dueDate = new Date();
    this.dueDate.setDate(this.dueDate.getDate() + this.interval);
  }

  isDue() {
    return new Date() >= this.dueDate;
  }

  getMasteryLevel() {
    if (this.level === 0) return 'New';
    if (this.level <= 2) return 'Learning';
    if (this.level <= 5) return 'Young';
    return 'Mature';
  }
}

export class SRSScheduler {
  constructor(cards) {
    this.cards = cards; // Map of item ID -> SRSCard
  }

  getNextCard() {
    const dueCards = Array.from(this.cards.values())
      .filter(card => card.isDue())
      .sort((a, b) => {
        // Priority: failed cards, then by due date
        if (a.level === 0 && b.level !== 0) return -1;
        if (b.level === 0 && a.level !== 0) return 1;
        return a.dueDate - b.dueDate;
      });

    return dueCards[0] || null;
  }

  getDueCount() {
    return Array.from(this.cards.values()).filter(c => c.isDue()).length;
  }

  getStats() {
    const cards = Array.from(this.cards.values());
    return {
      total: cards.length,
      new: cards.filter(c => c.level === 0).length,
      learning: cards.filter(c => c.level > 0 && c.level <= 2).length,
      young: cards.filter(c => c.level > 2 && c.level <= 5).length,
      mature: cards.filter(c => c.level > 5).length,
      due: this.getDueCount()
    };
  }
}
```

### 3.2 Progress Tracking

**File**: `src/services/progress.js`

```javascript
import { SRSCard, SRSScheduler } from './srs';
import { storage } from './storage';

export class ProgressTracker {
  constructor() {
    this.wordCards = new Map(); // word -> SRSCard
    this.collocationCards = new Map(); // pairKey -> SRSCard
    this.sessionStats = {
      correct: 0,
      incorrect: 0,
      partiallyCorrect: 0
    };
  }

  async load() {
    const data = await storage.loadProgress();
    if (data) {
      // Restore SRS cards from saved data
      this.wordCards = this.deserializeCards(data.words);
      this.collocationCards = this.deserializeCards(data.collocations);
    }
  }

  async save() {
    await storage.saveProgress({
      words: this.serializeCards(this.wordCards),
      collocations: this.serializeCards(this.collocationCards),
      lastUpdated: new Date().toISOString()
    });
  }

  recordAnswer(word, collocationPair, correctAnswers, incorrectAnswers) {
    // Update word mastery
    const wordCard = this.getOrCreateWordCard(word);
    const wordQuality = incorrectAnswers.length === 0 ? 5 : 3;
    wordCard.review(wordQuality);

    // Update collocation mastery for correct pairs
    correctAnswers.forEach(answer => {
      const pairKey = `${word}|${answer}`;
      const pairCard = this.getOrCreateCollocationCard(pairKey);
      pairCard.review(5);
    });

    // Penalize incorrect pairs
    incorrectAnswers.forEach(answer => {
      const pairKey = `${word}|${answer}`;
      const pairCard = this.getOrCreateCollocationCard(pairKey);
      pairCard.review(0);
    });

    // Update session stats
    this.sessionStats.correct += correctAnswers.length;
    this.sessionStats.incorrect += incorrectAnswers.length;

    this.save();
  }

  getOrCreateWordCard(word) {
    if (!this.wordCards.has(word)) {
      this.wordCards.set(word, new SRSCard(word));
    }
    return this.wordCards.get(word);
  }

  getOrCreateCollocationCard(pairKey) {
    if (!this.collocationCards.has(pairKey)) {
      this.collocationCards.set(pairKey, new SRSCard(pairKey));
    }
    return this.collocationCards.get(pairKey);
  }
}
```

---

## Phase 4: Game 1 - What Could Match

### 4.1 Game Component

**File**: `src/components/games/WhatCouldMatch.jsx`

**State Management**:
```javascript
const [currentWord, setCurrentWord] = useState(null);
const [gameMode, setGameMode] = useState('verb-noun'); // verb-noun, adj-noun, noun-verb, noun-adj
const [userAnswers, setUserAnswers] = useState([]);
const [validAnswers, setValidAnswers] = useState([]);
const [currentInput, setCurrentInput] = useState('');
const [feedback, setFeedback] = useState(null);
const [isFinished, setIsFinished] = useState(false);
```

**Game Flow**:
1. Load next word from SRS scheduler
2. Determine valid answers from collocation database
3. Show word with furigana
4. Accept user answers one by one
5. Validate each answer (check collocation database + OpenAI)
6. When user gives up, show results
7. Update SRS progress
8. Move to next word

### 4.2 Answer Validation Logic

**File**: `src/services/gameLogic.js`

```javascript
export const validateAnswer = async (word, userAnswer, collocationDb, openAI) => {
  // Step 1: Check exact match in collocation database
  const exactMatch = collocationDb.findMatch(word, userAnswer);
  if (exactMatch) {
    return { valid: true, confidence: 'high', source: 'database' };
  }

  // Step 2: Check for hiragana/katakana/kanji variations
  const variations = generateVariations(userAnswer);
  for (const variant of variations) {
    const match = collocationDb.findMatch(word, variant);
    if (match) {
      return { valid: true, confidence: 'high', source: 'database-variant' };
    }
  }

  // Step 3: Use OpenAI for semantic validation
  const validOptions = collocationDb.getMatches(word).map(m => m.japanese);
  const aiValidation = await openAI.validateAnswer(word, userAnswer, validOptions);

  return {
    valid: aiValidation,
    confidence: 'medium',
    source: 'ai'
  };
};
```

### 4.3 Furigana Display

**File**: `src/components/ui/FuriganaText.jsx`

```javascript
export const FuriganaText = ({ japanese, reading }) => {
  // Parse kanji and add furigana
  return (
    <ruby>
      {japanese}
      <rt>{reading}</rt>
    </ruby>
  );
};
```

For more complex parsing (mixed kanji/kana), use kuroshiro library or implement custom parser.

---

## Phase 5: Game 2 - Fill the Blanks

### 5.1 Sentence Generation

**Approach**:
1. Select random word from study list (based on SRS due date)
2. Find compatible words from collocation database
3. Send to OpenAI to generate natural sentence
4. Validate that sentence uses only study list vocabulary
5. Remove target word and present to user

**Validation**:
- Check that generated sentence doesn't use vocabulary outside study list
- Ensure sentence is grammatically correct
- Fallback to template sentences if generation fails

### 5.2 Template Sentences (Fallback)

**File**: `public/data/sentence-templates.json`

```json
{
  "verb-noun": [
    "{subject}は{object}を{verb}ます。",
    "{subject}は{time}に{object}を{verb}ました。"
  ],
  "adj-noun": [
    "{noun}は{adjective}です。",
    "とても{adjective}{noun}です。"
  ]
}
```

Use templates when OpenAI is unavailable or rate-limited.

---

## Technical Specifications

### Performance Targets

- **Initial Load**: < 2 seconds
- **Database Query**: < 50ms
- **Game Transition**: < 200ms
- **API Response**: < 5 seconds (with loading indicator)

### Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile: iOS Safari 14+, Android Chrome 90+

### Data Size Estimates

- Study List (100 words): ~10KB
- Collocation Database (500 pairs): ~50KB
- Progress Data (per user): ~100KB
- Total Static Assets: ~500KB

### IndexedDB Schema

```javascript
db.version(1).stores({
  vocabulary: 'id, japanese, type',
  collocations: 'id, [word1+word2], word1, word2, score',
  srsCards: 'id, type, dueDate',
  progress: 'key',
  sessions: '++id, date'
});
```

---

## API Usage & Cost Optimization

### OpenAI API Cost Estimate

**GPT-4 Pricing** (as of 2025):
- Input: $0.03 / 1K tokens
- Output: $0.06 / 1K tokens

**Usage Per Game Session** (10 rounds):
- Answer Validation: ~100 tokens × 10 = 1,000 tokens → $0.03
- Sentence Generation: ~200 tokens × 10 = 2,000 tokens → $0.06
- **Total per session**: ~$0.09

**Monthly Cost** (assuming 1 session/day):
- $0.09 × 30 = **$2.70/month**

### Cost Reduction Strategies

1. **Cache Common Validations**: Store frequently validated answers locally
2. **Use GPT-3.5-turbo for Validation**: Reduce cost by 10x for simple tasks
3. **Batch Requests**: Combine multiple validations when possible
4. **Fallback to Templates**: Use pre-generated sentences when API is slow
5. **Client-Side Validation**: Check collocation database before calling API

---

## Development Workflow

### Git Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature branches
- `data/*`: Data preparation branches

### Testing Strategy

**Unit Tests**:
- SRS algorithm correctness
- Collocation database queries
- Data model validation

**Integration Tests**:
- OpenAI API integration
- Storage service (LocalStorage + IndexedDB)
- Game flow

**Manual Testing**:
- User experience
- Japanese text rendering
- Mobile responsiveness

### Deployment Checklist

- [ ] Minimize bundle size
- [ ] Optimize images and assets
- [ ] Test on multiple browsers
- [ ] Verify API key encryption
- [ ] Test offline functionality
- [ ] Add error boundaries
- [ ] Setup analytics (optional)
- [ ] Create user guide

---

## Next Steps

1. **Phase 1**: Start with data preparation
   - Create sample study list CSV (20-30 words)
   - Build basic CSV parser
   - Manual collocation curation for sample data

2. **Phase 2**: Setup project scaffolding
   - Initialize Vite + React
   - Configure Material UI theme
   - Create basic routing

3. **Phase 3**: Implement core services
   - Storage service
   - SRS algorithm
   - Data models

4. **Iterate**: Build games incrementally and test frequently

---

**Document Version**: 1.0
**Last Updated**: 2025-11-08
**Status**: Planning Phase
