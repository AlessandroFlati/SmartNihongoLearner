# Project Status - Smart Nihongo Learner

**Last Updated**: 2025-11-08
**Current Phase**: Planning & Setup Complete

## Completed Items

### Documentation
- [x] Comprehensive README.md with project overview, architecture, and features
- [x] Detailed IMPLEMENTATION_PLAN.md with technical specifications
- [x] Sample study list CSV (30 common Japanese words)

### Project Structure
- [x] Created folder structure for data preparation
- [x] Created folder structure for React application
- [x] Setup .gitignore for the project

## Current Status

**Phase**: Ready to begin Phase 1 (Data Preparation)

**Repository Structure**:
```
SmartNihongoLearner/
├── data-preparation/
│   ├── input/
│   │   └── study-list-sample.csv (30 words: 8 verbs, 10 nouns, 12 adjectives)
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

## Next Steps

### Immediate (Start Here)

1. **CSV Parser** - `data-preparation/parsers/csv-parser.js`
   - Read and validate study-list-sample.csv
   - Output structured JSON with vocabulary data
   - Add UUID generation for each word

2. **Basic Collocation Database** - Manual curation for sample data
   - Create initial collocations.json with meaningful pairs
   - Start with obvious pairs (e.g., のむ + 水, たべる + ごはん)
   - Use adjacency list format as specified in implementation plan

3. **Package.json Setup**
   - Initialize Node.js project for data preparation scripts
   - Add dependencies: csv-parser, uuid, fs-extra

### Short-Term (This Week)

4. **React Project Initialization**
   - Run `npm create vite@latest` for frontend
   - Install Material UI and dependencies
   - Setup dark theme configuration

5. **Kanshudo Scraper** (Optional - can skip for MVP)
   - Research Kanshudo's robots.txt
   - Implement basic scraper for frequency data
   - May skip this if manual curation is sufficient for sample data

### Medium-Term (Next 2 Weeks)

6. **Core Services Implementation**
   - Storage service (LocalStorage + IndexedDB)
   - OpenAI service with rate limiting
   - SRS algorithm implementation

7. **First Game - "What Could Match"**
   - Basic game component
   - Answer validation logic
   - Furigana display component

## Decision Points

### Data Preparation Approach

**Option A: Manual Curation First (Recommended for MVP)**
- Manually create collocations.json for 30-word sample
- ~50-100 meaningful pairs can be created in 1-2 hours
- Allows immediate testing of frontend/games
- Can add scraper/automation later

**Option B: Scraper First**
- Implement Kanshudo scraper
- More time-consuming upfront
- Better for scaling to larger vocabulary lists

**Recommendation**: Start with Option A to get a working prototype faster.

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

None at this time - all 20 questions were answered clearly. Ready to proceed with implementation.

## Resources

- [Kanshudo Routledge Collection](https://www.kanshudo.com/collections/routledge)
- [SM-2 Algorithm Documentation](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)
- [Material UI Dark Theme](https://mui.com/material-ui/customization/dark-mode/)
- [OpenAI API Pricing](https://openai.com/pricing)

---

**Ready to start Phase 1!**

The next concrete action is to implement the CSV parser and create a basic collocation database for the sample vocabulary.
