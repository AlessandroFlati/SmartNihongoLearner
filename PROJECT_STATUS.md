# Project Status - Smart Nihongo Learner

**Last Updated**: 2025-11-10
**Current Phase**: Data Preparation Complete - Ready for Frontend Development

> **CRITICAL ARCHITECTURE REQUIREMENT**
> This is a **SERVERLESS PROJECT** - NO backend server. All resources, progress tracking, vocabulary data, and user settings MUST be stored in the browser (LocalStorage/IndexedDB) and persist across browser sessions (even when shut down).

## Completed Items

### Documentation
- [x] Comprehensive README.md with project overview, architecture, and features
- [x] Detailed IMPLEMENTATION_PLAN.md with technical specifications
- [x] Sample study list CSV (30 common Japanese words)
- [x] Frequency data analysis and documentation

### Project Structure
- [x] Created folder structure for data preparation
- [x] Created folder structure for React application
- [x] Setup .gitignore for the project

### Data Preparation (Phase 1 Complete)
- [x] **N5 Vocabulary**: Manually classified 703 JLPT N5 words with type annotations
- [x] **N4 Vocabulary**: Manually classified 663 JLPT N4 words with type annotations
- [x] **N54 Combined**: Created merged dataset with 1,342 unique words (24 duplicates removed)
- [x] **Frequency Data Collection**: Integrated wordfreq library for 100% coverage
- [x] **Data Scripts**: Created Python tools for scraping, processing, and analysis

## Current Status

**Phase**: Phase 1 Complete - Vocabulary Data Preparation & Frequency Integration

**Repository Structure**:
```
SmartNihongoLearner/
├── data-preparation/
│   ├── input/
│   │   ├── N5.csv                    (703 words with frequency data)
│   │   ├── N4.csv                    (663 words with frequency data)
│   │   ├── N54.csv                   (1,342 unique words combined)
│   │   └── study-list-sample.csv     (30 sample words)
│   ├── raw/
│   │   ├── collected-tabs.html       (N5 source data)
│   │   ├── N4.html                   (N4 source data)
│   │   ├── scrape_kanshudo_frequency.py     (Routledge frequency scraper)
│   │   ├── inspect_kanshudo_html.py         (HTML structure analyzer)
│   │   ├── export_from_marumori_collection.js
│   │   ├── add_wordfreq_data.py             (Wordfreq integration)
│   │   ├── cleanup_frequency_columns.py     (CSV cleanup)
│   │   ├── frequency_summary.py             (Analysis report)
│   │   └── map_frequency_to_csvs.py         (Frequency mapping)
│   ├── scrapers/       (empty - ready for implementation)
│   ├── generators/     (empty - ready for implementation)
│   ├── parsers/        (empty - ready for implementation)
│   ├── optimizers/     (empty - ready for implementation)
│   └── output/         (empty - for generated data)
├── public/data/        (empty - for final static assets)
├── src/                (empty - for React app)
├── .gitignore
├── README.md
├── IMPLEMENTATION_PLAN.md
└── PROJECT_STATUS.md
```

### Vocabulary Data Statistics

**N5 Vocabulary (703 words)**
- Average frequency: 4.69 (Zipf scale 0-8)
- Very common (6.0+): 34 words (4.8%)
- Common (4.0-6.0): 551 words (78.4%)
- Less common (<4.0): 118 words (16.8%)

**N4 Vocabulary (663 words)**
- Average frequency: 4.44 (Zipf scale 0-8)
- Very common (6.0+): 7 words (1.1%)
- Common (4.0-6.0): 486 words (73.3%)
- Less common (<4.0): 170 words (25.6%)

**N54 Combined (1,342 unique words)**
- Average frequency: 4.56 (Zipf scale 0-8)
- Very common (6.0+): 34 words (2.5%)
- Common (4.0-6.0): 1,022 words (76.2%)
- Less common (<4.0): 286 words (21.3%)

### Frequency Data Sources Evaluated

1. **Routledge 5000** (via Kanshudo scraping)
   - Coverage: 4,904 words scraped
   - JLPT Coverage: ~15% of N5/N4 vocabulary
   - Status: Evaluated but not used due to low coverage

2. **wordfreq Library** ✓ SELECTED
   - Coverage: 100% of all 1,342 JLPT N5/N4 words
   - Sources: Multi-corpus (Wikipedia, subtitles, news, books, web, Twitter, Reddit)
   - Scale: Zipf frequency (0-8, higher = more common)
   - Installation: `pip install wordfreq[cjk]`

3. **BCCWJ (NINJAL)** - Evaluated but not needed
   - Most authoritative Japanese corpus (104M words)
   - Considered but wordfreq provided sufficient coverage

## Next Steps

### Phase 2: Collocation Database & React Setup

1. **Collocation Generation** - PRIORITY
   - Create collocation pairs from N5/N4 vocabulary
   - Use frequency data to prioritize common combinations
   - Generate adjacency list structure
   - Target: ~500-1000 meaningful verb-noun, adjective-noun pairs

2. **CSV to JSON Converter**
   - Convert N5.csv, N4.csv, N54.csv to JSON format
   - Add UUID generation for each word
   - Output to `public/data/vocabulary.json`

3. **React Project Initialization**
   - Run `npm create vite@latest` for frontend
   - Install Material UI and dependencies
   - Setup dark theme configuration
   - Create basic project structure

### Phase 3: Core Services (Next 2 Weeks)

4. **Storage Service Implementation** (SERVERLESS - Browser-Only)
   - LocalStorage for settings and API keys
   - IndexedDB for vocabulary, collocations, and progress (using Dexie)
   - **ALL data stored in browser** - no backend server
   - Progress tracking and backup (browser-based)
   - **Data persists across browser sessions** (even when shut down)

5. **SRS Algorithm**
   - Implement SM-2 spaced repetition
   - Card scheduling logic
   - Progress persistence

6. **OpenAI Service**
   - API integration with rate limiting
   - Answer validation endpoint
   - Sentence generation (for Game 2)

### Phase 4: Game Development

7. **Game 1 - "What Could Match"**
   - Basic game component with Material UI
   - Answer validation using collocation database
   - Furigana display component
   - SRS integration

8. **Game 2 - "Fill the Blanks"**
   - Sentence generation using OpenAI
   - Blank creation logic
   - Answer validation

## Completed Work Summary

### Data Preparation Accomplishments

**Vocabulary Collection**
- Manually processed 1,366 total entries from HTML sources
- Classified each word by grammatical type using Japanese grammar patterns
- Removed 24 duplicates to create clean N54 combined dataset
- Final vocabulary: 703 N5 + 663 N4 = 1,342 unique words

**Frequency Integration**
- Researched multiple frequency data sources (Routledge, BCCWJ, wordfreq)
- Integrated wordfreq library for 100% vocabulary coverage
- Added Zipf frequency scores (0-8 scale) to all words
- Created analysis tools to validate data quality

**Scripts & Tools Created**
1. `scrape_kanshudo_frequency.py` - Routledge 5000 scraper (50 collections, 4,904 words)
2. `inspect_kanshudo_html.py` - HTML structure analyzer
3. `add_wordfreq_data.py` - Wordfreq library integration
4. `cleanup_frequency_columns.py` - CSV standardization
5. `frequency_summary.py` - Statistical analysis and reporting
6. `map_frequency_to_csvs.py` - Frequency data mapping utility

**CSV File Structure**
All vocabulary files follow consistent schema:
- `japanese` - Japanese word
- `reading` - Romaji/hiragana reading
- `english` - English translation
- `type` - Grammatical type (verb, noun, adjective, etc.)
- `frequency` - Zipf frequency score (0-8, higher = more common)

## Decision Points

### Data Preparation Approach ✓ COMPLETED

**Decision Made**: Combined manual classification with automated frequency integration
- Manually classified 1,366 words by grammatical type
- Used wordfreq library for automated frequency data (100% coverage)
- Created Python scripts for data processing and analysis
- Result: High-quality dataset ready for collocation generation

### Frequency Data Source ✓ SELECTED

**Decision Made**: wordfreq library
- Provides 100% coverage vs. Routledge's 15%
- Multi-source corpus (Wikipedia, web, news, subtitles, etc.)
- Easy programmatic access via Python
- Standardized Zipf scale (0-8)

### Frontend Framework

**Confirmed**: React + Vite + Material UI (dark theme)
- Modern, fast development experience
- Good TypeScript support (can add later)
- Material UI provides dark theme out of box

## Known Challenges

1. **Japanese Text Input**: Need to handle IME input properly in React
2. **Furigana Rendering**: May need custom component or library (kuroshiro)
3. **OpenAI Cost Management**: Need clear user warnings about API usage costs
4. **Browser Compatibility**: Test furigana rendering across browsers

## Questions for User

None at this time - all questions answered. Phase 1 complete, ready for Phase 2.

## Resources

### Data Sources
- [wordfreq Library](https://github.com/rspeer/wordfreq) - Multi-corpus frequency data
- [Kanshudo Routledge Collection](https://www.kanshudo.com/collections/routledge) - Japanese frequency database
- [BCCWJ (NINJAL)](https://clrd.ninjal.ac.jp/bccwj/en/freq-list.html) - Balanced Corpus of Contemporary Written Japanese
- [University of Leeds Corpus](https://github.com/hingston/japanese) - 44,998 Japanese words by frequency

### Development Resources
- [SM-2 Algorithm Documentation](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2) - Spaced repetition
- [Material UI Dark Theme](https://mui.com/material-ui/customization/dark-mode/)
- [OpenAI API Pricing](https://openai.com/pricing)
- [Dexie.js](https://dexie.org/) - IndexedDB wrapper

### Python Environment
- Virtual environment: `/home/alessandro/.virtualenvs/SmartNihongoLearner`
- Dependencies installed: `requests`, `beautifulsoup4`, `wordfreq[cjk]`

---

**Phase 1 Complete! ✓**

We now have:
- ✓ 1,342 vocabulary words across N5 and N4 levels
- ✓ 100% frequency coverage using wordfreq library
- ✓ Clean, consistent CSV format ready for JSON conversion
- ✓ Analysis tools for data validation

**Next concrete actions**:
1. Generate collocation pairs from vocabulary using frequency data
2. Convert CSV files to JSON format for React app
3. Initialize React + Vite project with Material UI
