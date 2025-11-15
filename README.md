# Smart Nihongo Learner

A context-aware Japanese vocabulary learning application that helps users master word collocations through interactive games and spaced repetition.

## Quick Start

### Prerequisites

- **Node.js**: 16.x or higher
- **npm**: 7.x or higher
- **OpenAI API Key**: Optional, for enhanced gameplay features

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/SmartNihongoLearner.git
cd SmartNihongoLearner

# Install dependencies
npm install
```

### Running Locally

```bash
# Start the development server
npm run dev
```

The application will start on `http://localhost:5173` by default (or the next available port if 5173 is in use).

To run on a specific port:

```bash
npm run dev -- --port 3000
```

### Building for Production

```bash
# Create production build
npm run build

# Preview production build locally
npm run preview
```

The production build will be created in the `dist/` directory and can be deployed to any static hosting service (Netlify, Vercel, GitHub Pages, etc.).

---

## What is Smart Nihongo Learner?

Smart Nihongo Learner goes beyond traditional flashcards by teaching Japanese vocabulary **in context**. Instead of memorizing words in isolation, learners practice meaningful word combinations (collocations) like のむ (to drink) with コーヒー (coffee), 水 (water), or ビール (beer).

The app uses an intelligent **Spaced Repetition System (SRS)** to adapt to your learning pace, focusing more on words you struggle with and less on words you've mastered.

### Key Features

**Interactive Learning Games:**
- **"What Could Match"**: Given a word (verb/adjective/noun), find all compatible matches
  - Example: "What can you drink?" → water, coffee, tea, beer...
  - Supports 4 game modes: Verb→Noun, Adjective→Noun, Noun→Verb, Noun→Adjective
- **Reverse Modes**: Practice collocations in both directions for deeper understanding

**Intelligent Study System:**
- **Anki-Style SRS**: Proven spaced repetition algorithm that schedules reviews based on your performance
- **6-Tier Priority System**: Prioritizes failed/learning words over mature ones
- **Maturity Tracking**: Track progress from Learning (<3 correct) → Young (3-5) → Mature (6-10) → Mastered (>10)
- **JLPT Level Support**: Study N5 vocabulary or combined N5+N4 (1,342 words total)

**Rich Learning Experience:**
- **Context Hints**: Built-in hints for every collocation to aid understanding
- **Progress Statistics**: Detailed tracking of words practiced, correct answers, and mastery levels
- **Bonus Words**: Discover additional vocabulary during gameplay

**100% Serverless & Private:**
- **No Backend Server**: Everything runs in your browser
- **Offline-Ready**: All data persists locally using IndexedDB
- **Your Data Stays Private**: Progress never leaves your device
- **Optional OpenAI Integration**: Provide your own API key for enhanced features (entirely optional)

---

## How It Works

### 1. Select Your Study List
Choose between:
- **N5 Only**: 703 JLPT N5 words (beginner level)
- **N5 + N4**: 1,342 words (beginner + elementary level)

### 2. Choose a Game Mode
- **Verb → Noun**: Find nouns that work with a verb (e.g., drink → coffee, water)
- **Adjective → Noun**: Find nouns described by an adjective (e.g., delicious → food, ramen)
- **Noun → Verb**: Find verbs that work with a noun (e.g., water → drink, boil)
- **Noun → Adjective**: Find adjectives that describe a noun (e.g., food → delicious, spicy)

### 3. Play and Learn
- Type answers in Japanese (using your system's Japanese IME)
- Get instant feedback with context hints
- Skip difficult words to focus on what you know
- See results and review what you missed

### 4. Track Your Progress
- View detailed statistics showing your mastery levels
- See how many words are learning, young, mature, or mastered
- The SRS algorithm automatically prioritizes words you need to review

---

## Technology & Architecture

### Frontend Stack
- **React 18.3.1**: Modern UI framework with hooks
- **Vite**: Fast build tool and dev server
- **Material UI 6.3.0**: Component library with dark theme
- **Wanakana 5.3.1**: Japanese text processing for answer matching

### Storage (100% Browser-Based)
- **IndexedDB** (via Dexie): Stores vocabulary, collocations, and progress
- **LocalStorage**: Stores settings and encrypted API keys
- **All data persists across sessions**: Your progress is never lost

### Data Sources
- **JLPT Vocabulary**: 703 N5 + 663 N4 words with frequency data
- **Pre-computed Collocations**: 1,000+ verb-noun, adjective-noun pairs
- **Context Hints**: Manually curated hints for better understanding

### Serverless Architecture
This is a **fully serverless application** with **NO backend server**. All data, progress tracking, and user preferences are stored exclusively in the browser using LocalStorage and IndexedDB. Your learning progress persists across sessions and browser restarts. No data is ever sent to external servers except optional OpenAI API calls for gameplay assistance.

---

## Project Structure

```
SmartNihongoLearner/
├── data-preparation/              # Offline data processing scripts
│   ├── raw/                       # Source data and processing scripts
│   └── input/                     # CSV vocabulary files (N5, N4, N54)
├── public/                        # Static assets
│   └── data/
│       ├── vocabulary.json        # Full vocabulary database
│       ├── collocations_complete.json  # Collocation pairs
│       ├── collocation_hints.json      # Context hints (forward mode)
│       └── reverse_hints.json          # Context hints (reverse mode)
├── src/
│   ├── components/
│   │   ├── games/
│   │   │   └── WhatCouldMatch.jsx      # Main game component
│   │   ├── ui/
│   │   │   ├── FuriganaText.jsx        # Furigana display
│   │   │   └── AnswerInput.jsx         # Japanese text input
│   │   └── settings/
│   │       └── ApiKeyManager.jsx       # OpenAI key management
│   ├── services/
│   │   ├── storage.js             # IndexedDB + LocalStorage
│   │   ├── dataLoader.js          # Load vocabulary & hints
│   │   ├── collocation.js         # Word selection & SRS logic
│   │   └── srs.js                 # Spaced repetition algorithm
│   ├── App.jsx                    # Main app component
│   ├── main.jsx                   # Entry point
│   └── theme.js                   # Material UI dark theme
├── package.json
├── vite.config.js
└── README.md
```

---

## Development

### Available Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
```

### Adding New Vocabulary

Vocabulary is stored in `public/data/vocabulary.json` with this structure:

```json
{
  "vocabulary": [
    {
      "id": "unique-id",
      "japanese": "のむ",
      "reading": "nomu",
      "english": "to drink",
      "type": "verb",
      "frequency": 5.23,
      "jlpt": ["N5"]
    }
  ]
}
```

### Adding New Collocations

Collocations are stored in `public/data/collocations_complete.json`:

```json
{
  "words": {
    "のむ": {
      "type": "verb",
      "reading": "nomu",
      "english": "to drink",
      "matches": {
        "nouns": [
          {"word": "水", "reading": "みず", "english": "water"},
          {"word": "コーヒー", "reading": "koーhiー", "english": "coffee"}
        ]
      }
    }
  }
}
```

---

## Future Enhancements

- **Fill the Blanks Game**: Complete sentences with correct vocabulary
- **Audio Pronunciation**: Listen to native pronunciation
- **Export/Import Progress**: Backup and restore your learning data
- **Additional JLPT Levels**: N3, N2, N1 vocabulary support
- **Mobile App**: Native iOS and Android apps
- **Community Features**: Share custom word lists

---

## Contributing

This is currently a personal learning project. Future contributions may be accepted after initial stable release.

---

## License

MIT License (to be confirmed)

---

## Acknowledgments

- Frequency data integrated from the **wordfreq** library
- Vocabulary sourced from **JLPT** official word lists
- Inspired by **Anki's** spaced repetition algorithm
- Built with assistance from **Claude Code**

---

## Support & Documentation

For detailed technical documentation, see:
- **PROJECT_STATUS.md**: Current implementation status and progress
- **IMPLEMENTATION_PLAN.md**: Detailed technical specifications

For issues or questions, please open an issue on GitHub.

---

**Note**: This project is in active development. Check the commit history for latest updates and improvements.
