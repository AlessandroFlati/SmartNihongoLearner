# GOOD HINTS EXAMPLES

This document shows what QUALITY hints should look like, contrasted with the current POOR hints.

---

## Example 1: いる (to be/exist) - Currently VERY POOR (0.0/100)

### Current State (WRONG)
- **Quality Score**: 0.0/100
- **Total nouns**: 52
- **Unique hints**: 4
- **"related elements"**: 75.0% (39/52 nouns) ← CATASTROPHIC

**Current hints**:
```json
{
  "家": "related elements",
  "部屋": "related elements",
  "中": "related elements",
  "学校": "related elements",
  "会社": "related elements",
  "国": "related elements",
  "母": "related elements",
  "父": "related elements",
  "息子": "related elements",
  "娘": "related elements"
}
```

### What It Should Be (RIGHT)

**Target Quality Score**: 90+/100 (EXCELLENT)

**Semantic categorization**:
```json
{
  "家": "buildings and structures",
  "部屋": "interior spaces",
  "中": "spatial positions",
  "学校": "educational institutions",
  "会社": "organizations and workplaces",
  "国": "geographical areas",
  "母": "family members - parents",
  "父": "family members - parents",
  "息子": "family members - children",
  "娘": "family members - children",
  "医者": "professional roles",
  "先生": "professional roles",
  "看護婦": "professional roles",
  "犬": "domestic animals",
  "猫": "domestic animals"
}
```

**Expected distribution**:
- "family members - parents": 2 nouns (3.8%)
- "family members - children": 2 nouns (3.8%)
- "professional roles": 3 nouns (5.8%)
- "buildings and structures": 1 noun (1.9%)
- "interior spaces": 1 noun (1.9%)
- "educational institutions": 1 noun (1.9%)
- etc.

**Result**: Quality score ~96/100 (EXCELLENT)

---

## Example 2: ある (to be/have) - Currently VERY POOR (0.0/100)

### Current State (WRONG)
- **Quality Score**: 0.0/100
- **Total nouns**: 162
- **Unique hints**: 18
- **"elements present"**: 51.9% (84/162 nouns) ← CRITICAL FAILURE

**Current hints** (sample):
```json
{
  "場合": "elements present",
  "帰り": "elements present",
  "後": "elements present",
  "間": "elements present",
  "晩": "elements present",
  "夕方": "elements present",
  "上": "elements present",
  "下": "elements present",
  "友達": "elements present"
}
```

### What It Should Be (RIGHT)

**Target Quality Score**: 90+/100 (EXCELLENT)

**Semantic categorization**:
```json
{
  "場合": "situational contexts",
  "後": "temporal sequences - after",
  "帰り": "journey-related times",
  "間": "time intervals",
  "晩": "time periods - evening",
  "夕方": "time periods - afternoon",
  "毎週": "recurring periods",
  "上": "spatial positions - vertical",
  "下": "spatial positions - vertical",
  "右": "spatial positions - lateral",
  "左": "spatial positions - lateral",
  "友達": "social relationships",
  "両親": "family relationships",
  "兄弟": "sibling relationships",
  "質問": "communication acts",
  "理由": "logical elements",
  "問題": "challenges and issues"
}
```

**Expected distribution** (no single hint >15%):
- "time periods - evening": ~8 nouns (4.9%)
- "spatial positions - vertical": ~6 nouns (3.7%)
- "social relationships": ~5 nouns (3.1%)
- "recurring periods": ~7 nouns (4.3%)
- etc.

**Result**: Quality score ~92/100 (EXCELLENT)

---

## Example 3: する (to do) - Currently POOR (38.8/100)

### Current State (WRONG)
- **Quality Score**: 38.8/100
- **Total nouns**: 80
- **"activities performed"**: 21.3% (17/80 nouns) ← TOO GENERIC

**Current hints** (sample):
```json
{
  "電話": "activities performed",
  "会話": "activities performed",
  "料理": "activities performed",
  "掃除": "activities performed",
  "洗濯": "activities performed",
  "サッカー": "activities performed",
  "テニス": "activities performed",
  "勉強": "activities performed",
  "仕事": "activities performed"
}
```

### What It Should Be (RIGHT)

**Target Quality Score**: 90+/100 (EXCELLENT)

**Semantic categorization**:
```json
{
  "電話": "communication activities",
  "会話": "communication activities",
  "質問": "communication activities",
  "料理": "household tasks - cooking",
  "掃除": "household tasks - cleaning",
  "洗濯": "household tasks - laundry",
  "買い物": "household tasks - shopping",
  "サッカー": "team sports",
  "テニス": "racket sports",
  "野球": "team sports",
  "勉強": "learning activities",
  "仕事": "work activities",
  "準備": "preparatory tasks",
  "計画": "planning activities",
  "約束": "commitment actions",
  "予約": "reservation actions",
  "案内": "guidance activities",
  "説明": "explanatory actions"
}
```

**Expected distribution**:
- "communication activities": 3 nouns (3.8%)
- "household tasks - cooking": 1 noun (1.3%)
- "household tasks - cleaning": 1 noun (1.3%)
- "team sports": 2 nouns (2.5%)
- etc.

**Result**: Quality score ~95/100 (EXCELLENT)

---

## Example 4: 行く (to go) - Currently FAIR (54.6/100)

### Current State (PARTIALLY RIGHT, needs improvement)
- **Quality Score**: 54.6/100
- **Total nouns**: 68
- **"destinations visited"**: 47.1% (32/68 nouns) ← STILL TOO GENERIC

**Current hints**:
```json
{
  "学校": "destinations visited",
  "会社": "destinations visited",
  "病院": "destinations visited",
  "図書館": "destinations visited",
  "レストラン": "destinations visited"
}
```

**Problem**: While "destinations visited" is more specific than "related elements", it's still too generic. It doesn't help differentiate between types of destinations.

### What It Should Be (RIGHT)

**Target Quality Score**: 90+/100 (EXCELLENT)

**Semantic categorization**:
```json
{
  "学校": "educational institutions",
  "大学": "educational institutions",
  "図書館": "educational facilities",
  "会社": "work destinations",
  "仕事": "work destinations",
  "病院": "healthcare facilities",
  "医者": "healthcare destinations",
  "レストラン": "dining establishments",
  "喫茶店": "dining establishments",
  "デパート": "shopping venues",
  "スーパー": "shopping venues",
  "公園": "recreational spaces",
  "山": "natural destinations",
  "海": "natural destinations",
  "国": "geographical destinations - countries",
  "東京": "geographical destinations - cities",
  "駅": "transportation hubs",
  "空港": "transportation hubs"
}
```

**Expected distribution**:
- "educational institutions": 2 nouns (2.9%)
- "work destinations": 2 nouns (2.9%)
- "dining establishments": 2 nouns (2.9%)
- "shopping venues": 2 nouns (2.9%)
- etc.

**Result**: Quality score ~94/100 (EXCELLENT)

---

## Key Principles for GOOD Hints

### 1. Semantic Specificity
- ✅ "family members - parents" (specific)
- ❌ "people involved" (too generic)
- ❌ "related elements" (meaningless)

### 2. Meaningful Distinctions
- ✅ "team sports" vs "racket sports" vs "individual sports"
- ❌ "sports activities" (doesn't help distinguish)

### 3. Hierarchical Categories
- ✅ "household tasks - cooking" (shows hierarchy)
- ✅ "household tasks - cleaning" (shows hierarchy)
- ❌ "activities performed" (no hierarchy)

### 4. Distribution Balance
- ✅ No single hint used >15% (ideally <10%)
- ❌ One hint used >50% (catastrophic)

### 5. User Value Test
Ask: "Does this hint help the user understand WHY this noun goes with this verb?"

- ✅ "communication activities" → Yes, helps understand する with 電話, 会話
- ❌ "related elements" → No, provides zero semantic information

### 6. Pattern Recognition
Good hints enable users to think:
- ✅ "Ah, いる is used with family members like 母, 父, 息子"
- ✅ "Ah, 行く is used with educational institutions like 学校, 大学"
- ❌ "These nouns are... related elements?" (meaningless)

---

## Quality Score Calculation

### Formula
```
Quality Score = 100 - (max_percentage_single_hint × 2)
```

### Examples

**EXCELLENT (いる with good hints)**:
- Most common hint: 5.8% usage
- Quality score: 100 - (5.8 × 2) = 88.4 (GOOD, bordering EXCELLENT)

**VERY POOR (いる with current hints)**:
- Most common hint: 75.0% usage
- Quality score: 100 - (75.0 × 2) = -50 → 0.0 (VERY POOR)

**Target for all verbs**: >90 quality score (EXCELLENT)

---

## Summary

Current hints are CATASTROPHIC because:
1. 38.2% of ALL hints are just "related elements"
2. 76.4% of hints are generic and meaningless
3. Users get zero semantic value

Good hints should:
1. Be semantically specific and meaningful
2. Help users understand collocation patterns
3. Have balanced distribution (<15% per hint)
4. Enable pattern recognition and learning

**Bottom line**: Every hint should answer the question "WHY does this noun go with this verb?" in a way that helps users learn and remember patterns.

---

*Document created: 2025-11-11*
*Purpose: Reference for future hint regeneration*
