# Smart Nihongo Learner

A context-aware Japanese vocabulary learning application that helps users master word collocations through interactive games and spaced repetition.

## 🎯 Overview

Smart Nihongo Learner goes beyond traditional flashcards by teaching Japanese vocabulary in context. Instead of memorizing words in isolation, learners practice meaningful word combinations (collocations) like のむ (to drink) with コーヒー (coffee), 水 (water), or ビール (beer).

> **IMPORTANT: SERVERLESS ARCHITECTURE**
> This is a **fully serverless application** with **NO backend server**. All data, progress tracking, and user preferences are stored **exclusively in the browser** using LocalStorage and IndexedDB. Your learning progress persists across sessions and browser restarts. No data is ever sent to external servers except optional OpenAI API calls for gameplay assistance.

### Key Features

- **Context-Based Learning**: Learn vocabulary through meaningful word pairs and collocations
- **Two Interactive Games**:
  - **"What Could Match"**: Given a word, find all compatible matches (e.g., "What can you drink?")
  - **"Fill the Blanks"**: Complete sentences with the correct vocabulary from your study list
- **Intelligent SRS**: Anki-style spaced repetition that adapts to your performance
- **AI-Assisted Gameplay**: Real-time answer validation and sentence generation using OpenAI API
- **Granular Progress Tracking**: Tracks mastery of individual words, collocations, and overall statistics
- **Fully Offline-Ready**: Pre-computed collocation database requires no API calls for core functionality

## 🏗️ Architecture

### Two-Phase Approach

#### Phase 1: Data Preparation (Offline)
Pre-deployment data processing using local tools (Claude Code, web scrapers):

1. **Frequency Analysis**: Parse established frequency resources (e.g., Kanshudo Routledge collections)
2. **Collocation Generation**: Generate meaningful word pairs from study list
3. **Database Creation**: Create pre-computed collocation matrix/database

**Input**: CSV study list (Japanese word, reading, English translation, word type)
**Output**: Static collocation database (JSON/optimized format)

#### Phase 2: Web Application (Online)
**100% serverless static web application** with browser-only persistence:

- **Frontend Framework**: React with Vite
- **UI Library**: Material UI (dark theme)
- **Storage**: LocalStorage/IndexedDB for ALL progress, settings, and data persistence
  - **All resources stored in browser** (vocabulary, collocations, user progress)
  - **Progress persists across browser sessions** (even when browser is shut down)
  - **No backend server** - everything runs client-side
- **API Integration**: OpenAI API for gameplay assistance (user-provided API key, optional)

### Project Structure

```
SmartNihongoLearner/
├── data-preparation/              # Offline data processing
│   ├── scrapers/                 # Web scrapers for frequency data
│   │   └── kanshudo-scraper.js
│   ├── generators/               # Collocation generation scripts
│   │   └── collocation-generator.js
│   ├── input/                    # Source data
│   │   └── study-list.csv
│   └── output/                   # Generated databases
│       └── collocations.json
├── public/                        # Static assets
│   ├── data/
│   │   ├── study-list.csv        # Vocabulary list
│   │   └── collocations.json     # Pre-computed word pairs
│   └── index.html
├── src/                          # Frontend application
│   ├── components/
│   │   ├── games/
│   │   │   ├── WhatCouldMatch.jsx
│   │   │   └── FillTheBlanks.jsx
│   │   ├── settings/
│   │   │   ├── ApiKeyManager.jsx
│   │   │   └── GameModeSelector.jsx
│   │   ├── progress/
│   │   │   ├── Statistics.jsx
│   │   │   └── MasteryIndicator.jsx
│   │   └── ui/
│   │       ├── FuriganaText.jsx
│   │       └── AnswerInput.jsx
│   ├── services/
│   │   ├── openai.js             # OpenAI API integration
│   │   ├── srs.js                # Anki-style SRS algorithm
│   │   ├── storage.js            # Browser storage management
│   │   ├── collocation.js        # Collocation query logic
│   │   └── gameLogic.js          # Game mechanics
│   ├── hooks/
│   │   ├── useSRS.js
│   │   └── useProgress.js
│   ├── models/
│   │   ├── Vocabulary.js
│   │   ├── Collocation.js
│   │   └── Progress.js
│   ├── utils/
│   │   ├── furigana.js
│   │   └── japanese.js
│   ├── App.jsx
│   ├── main.jsx
│   └── theme.js                  # Dark theme configuration
├── package.json
├── vite.config.js
├── IMPLEMENTATION_PLAN.md
└── README.md
```

## 📊 Data Schema

### Study List CSV Format
```csv
japanese,reading,english,type
のむ,nomu,to drink,verb
水,みず,water,noun
コーヒー,こーひー,coffee,noun
おいしい,oishii,delicious,adjective
```

**Word Types**: `noun`, `verb`, `adjective`, `other`

### Collocation Database
Pre-computed word pair compatibility with frequency scores:

```json
{
  "pairs": [
    {
      "word1": "のむ",
      "word2": "水",
      "frequency": 950,
      "context": "drink water"
    }
  ],
  "matrix": {
    // Optimized lookup structure
  }
}
```

### Progress Data (LocalStorage)
```json
{
  "apiKey": "encrypted_key",
  "wordMastery": {
    "のむ": {"level": 3, "lastReview": "2025-11-08", "nextReview": "2025-11-10"},
    "水": {"level": 2, "lastReview": "2025-11-07", "nextReview": "2025-11-09"}
  },
  "collocationMastery": {
    "のむ|水": {"correct": 5, "incorrect": 1, "lastSeen": "2025-11-08"},
    "のむ|コーヒー": {"correct": 2, "incorrect": 3, "lastSeen": "2025-11-07"}
  },
  "statistics": {
    "totalReviews": 150,
    "correctAnswers": 120,
    "streak": 5
  }
}
```

## 🎮 Game Mechanics

### "What Could Match" Game

**Modes** (user-selectable):
- Verb → Nouns: "What can you drink?" → water, coffee, beer...
- Adjective → Nouns: "What can be delicious?" → food, cake, ramen...
- Noun → Verbs: "What can you do with water?" → drink, boil, pour...
- Noun → Adjectives: "How can food be?" → delicious, hot, spicy...

**Flow**:
1. Present a word with furigana (e.g., のむ [飲む])
2. User enters answers one by one
3. AI validates each answer (handles variations, synonyms)
4. User continues until they give up or find all matches
5. System reveals missed answers and updates SRS

**Scoring**:
- Correct answers: Increase mastery for both word and pair
- Missed answers: Increase review frequency for that pair
- Incorrect answers: Decrease mastery, flag for review

### "Fill the Blanks" Game

**Flow**:
1. AI generates a sentence using vocabulary from study list
2. System removes one word (noun/verb/adjective)
3. User fills in the blank
4. AI validates answer against compatibility list
5. Update SRS based on correctness

**Example**:
```
Generated: 私は＿＿を飲みます。(I drink _____.)
Removed: 水 (water)
Accepted answers: 水, コーヒー, ビール (any compatible noun from study list)
```

## 🧠 SRS Algorithm (Anki-Style)

Based on SM-2 algorithm with modifications:

- **Initial Interval**: 1 day
- **Graduating Interval**: 3 days
- **Easy Interval**: 7 days
- **Ease Factor**: Starting at 2.5, adjusted based on performance

**Mastery Levels**:
- Level 0: New/Unlearned
- Level 1-2: Learning
- Level 3-5: Young
- Level 6+: Mature

**Review Priority**:
- Words/pairs due for review
- Failed items (more frequent)
- Partially correct items (medium frequency)
- Mastered items (less frequent)

## 🚀 Technology Stack

### Frontend
- **Framework**: React 18+ with Vite
- **UI Library**: Material UI v5 (dark theme)
- **State Management**: React Context + Hooks
- **Storage**: LocalStorage (settings/progress) + IndexedDB (large datasets)
- **Japanese Text**: react-furigana or custom component

### Data Processing (Offline)
- **Runtime**: Node.js
- **Scraping**: Cheerio/Puppeteer
- **Processing**: Claude Code for collocation generation
- **Format**: CSV → JSON conversion

### APIs
- **OpenAI API**: GPT-4 for sentence generation and answer validation
- **Rate Limiting**: Client-side throttling to manage costs

## 📝 Development Phases

### Phase 1: Data Preparation
- [ ] Create study list CSV parser
- [ ] Implement Kanshudo web scraper
- [ ] Generate collocation database using Claude
- [ ] Optimize database format for quick lookups

### Phase 2: Core Infrastructure
- [ ] Initialize React + Vite project
- [ ] Set up Material UI with dark theme
- [ ] Implement storage service (LocalStorage/IndexedDB)
- [ ] Create data models (Vocabulary, Collocation, Progress)
- [ ] Implement OpenAI API service with retry logic

### Phase 3: SRS System
- [ ] Implement Anki-style SRS algorithm
- [ ] Create progress tracking system
- [ ] Build mastery level calculations
- [ ] Implement review scheduling

### Phase 4: Game 1 - "What Could Match"
- [ ] Create game component
- [ ] Implement game mode selector
- [ ] Build answer input with validation
- [ ] Add furigana display
- [ ] Integrate SRS for answer feedback
- [ ] Create results/review screen

### Phase 5: Game 2 - "Fill the Blanks"
- [ ] Implement sentence generation (OpenAI)
- [ ] Create blank insertion logic
- [ ] Build answer validation
- [ ] Integrate with collocation database
- [ ] Add SRS tracking

### Phase 6: UI/UX Polish
- [ ] Design statistics dashboard
- [ ] Create mastery indicators
- [ ] Add loading states and error handling
- [ ] Implement API key management UI
- [ ] Add onboarding/tutorial

### Phase 7: Testing & Optimization
- [ ] Test SRS algorithm accuracy
- [ ] Optimize database queries
- [ ] Test OpenAI integration
- [ ] Cross-browser testing
- [ ] Performance optimization

### Phase 8: Deployment
- [ ] Build production bundle
- [ ] Deploy to static hosting (Netlify/Vercel)
- [ ] Create user documentation
- [ ] Monitor initial usage

## 🔒 Security Considerations

- **API Key Storage**: Encrypt OpenAI API key in LocalStorage
- **Client-Side Only**: No backend server reduces attack surface
- **CORS**: Ensure proper CORS handling for OpenAI API calls
- **Input Validation**: Sanitize all user inputs
- **Rate Limiting**: Prevent excessive API usage

## 🎨 UI/UX Design Principles

- **Dark Theme**: Reduce eye strain during study sessions
- **Minimalist**: Focus on content, minimal distractions
- **Responsive**: Mobile-first design
- **Accessibility**: Proper contrast ratios, keyboard navigation
- **Japanese Typography**: Proper font rendering for kanji/kana

## 📚 Future Enhancements

- Multi-list support (JLPT levels, textbooks)
- Audio pronunciation integration
- Export/import progress
- Offline mode (Service Worker)
- Community-shared collocation databases
- Gamification (badges, achievements)
- Mobile app (React Native)

## 🤝 Contributing

This is currently a personal learning project. Future contributions may be accepted after initial stable release.

## 📄 License

MIT License (to be confirmed)

## 🙏 Acknowledgments

- Frequency data sourced from Kanshudo and other Japanese learning resources
- Inspired by Anki's SRS algorithm
- Built with assistance from Claude Code

---

**Note**: This project is in active development. Check IMPLEMENTATION_PLAN.md for detailed technical specifications and current progress.
