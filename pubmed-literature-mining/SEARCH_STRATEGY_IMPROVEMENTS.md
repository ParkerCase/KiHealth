# PubMed Search Strategy Improvements

## Current Issues Identified

1. **Limited Search Query**: Current query is too basic and may miss many relevant articles
2. **Low Article Yield**: Only finding ~100 articles per run, but there are likely thousands
3. **Relevance Scoring**: Current 0-100 score may not be optimal for identifying truly valuable articles
4. **No Systematic Review Approach**: Not using comprehensive search strategies like systematic reviews

## Doctor's Questions Answered

### Q1: "How many articles will the scraping provide us?"

**Current**: ~100 articles per run (limited by `MAX_ARTICLES_PER_RUN=100`)

**Reality**: There are likely **thousands** of relevant articles in PubMed. A proper systematic review search strategy would find:
- **5,000-10,000+ articles** for knee OA progression
- **1,000-2,000+** after deduplication and basic filtering
- **200-500** high-quality articles after full-text screening

### Q2: "Is that not needed in our case to be able to find all relevant articles out there?"

**Answer: YES!** We should use systematic review search strategies. Current approach is too narrow.

### Q3: "How do we determine if an article is valuable or not?"

**Current System**:
- Relevance score 0-100 (threshold: 70 = "high relevance")
- Based on: keywords (40 pts), study design (30 pts), sample size (15 pts), journal (15 pts)

**Problems**:
- Score may not reflect true clinical value
- No distinction between "interesting" vs "actionable"
- No consideration of recency, novelty, or clinical applicability

---

## Proposed Improvements

### 1. Comprehensive PubMed Search Strategy

Use a **systematic review-style search strategy** with multiple search concepts:

```
# Concept 1: Disease
("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR 
 "gonarthrosis"[Title/Abstract] OR "knee arthrosis"[Title/Abstract] OR
 (knee[Title/Abstract] AND osteoarthritis[Title/Abstract]))

# Concept 2: Progression/Outcome
(progression[Title/Abstract] OR "total knee replacement"[Title/Abstract] OR 
 "total knee arthroplasty"[Title/Abstract] OR TKR[Title/Abstract] OR TKA[Title/Abstract] OR
 "knee replacement"[Title/Abstract] OR "knee arthroplasty"[Title/Abstract] OR
 "disease progression"[Title/Abstract] OR "structural progression"[Title/Abstract] OR
 "radiographic progression"[Title/Abstract] OR "symptom progression"[Title/Abstract])

# Concept 3: Prediction/Prognosis
(predictor[Title/Abstract] OR "risk factor"[Title/Abstract] OR 
 prognostic[Title/Abstract] OR prediction[Title/Abstract] OR
 "prediction model"[Title/Abstract] OR "prognostic model"[Title/Abstract] OR
 "risk prediction"[Title/Abstract] OR "outcome prediction"[Title/Abstract])

# Combined Query
(Concept 1) AND (Concept 2) AND (Concept 3)
```

**Additional Filters**:
- Publication date: Last 10 years (not just 5)
- Article types: All (not just Clinical Trial/Cohort/Review)
- Language: English
- Humans only

### 2. Enhanced Relevance Scoring System

**Current**: Single 0-100 score

**Proposed**: Multi-dimensional scoring with categories

#### A. Clinical Relevance Score (0-40 points)
- **High (30-40)**: Directly addresses prediction of TKR/progression
- **Medium (20-29)**: Related to OA progression but not directly predictive
- **Low (10-19)**: OA-related but not progression-focused
- **Very Low (0-9)**: Minimally relevant

#### B. Study Quality Score (0-30 points)
- **Study Design** (15 pts): Systematic review (15), Cohort (12), RCT (10), Case-control (8), Cross-sectional (5)
- **Sample Size** (10 pts): >1000 (10), 500-1000 (8), 100-500 (5), <100 (2)
- **Follow-up Duration** (5 pts): >5 years (5), 2-5 years (3), <2 years (1)

#### C. Novelty/Impact Score (0-20 points)
- **Journal Impact** (10 pts): Top-tier (10), Mid-tier (7), Other (3)
- **Recency** (5 pts): <1 year (5), 1-2 years (3), 2-5 years (1)
- **Novel Findings** (5 pts): New factors, new methods, significant results

#### D. Actionability Score (0-10 points)
- **Modifiable Factors** (5 pts): Identifies factors that can be changed
- **Clinical Applicability** (5 pts): Results can be used in practice

**Total Score**: 0-100 (same scale, but more nuanced)

**New Categories**:
- **High Value (80-100)**: Must-read, actionable, high-quality
- **Medium Value (60-79)**: Relevant, good quality, may be useful
- **Low Value (40-59)**: Somewhat relevant, lower quality
- **Very Low Value (0-39)**: Minimally relevant or poor quality

### 3. Article Value Determination Framework

**Value = Clinical Relevance × Study Quality × Actionability**

#### High-Value Articles (Priority 1):
- ✅ Directly predict TKR or progression
- ✅ Large sample size (>500)
- ✅ Longitudinal/cohort design
- ✅ Identifies modifiable factors
- ✅ Recent (<3 years) or from high-impact journal
- ✅ Provides actionable insights

#### Medium-Value Articles (Priority 2):
- ✅ Related to OA progression
- ✅ Moderate sample size (100-500)
- ✅ Good study design
- ✅ May provide supporting evidence

#### Low-Value Articles (Priority 3):
- ⚠️ OA-related but not progression-focused
- ⚠️ Small sample size (<100)
- ⚠️ Cross-sectional or case study
- ⚠️ Older (>5 years) or low-impact journal

### 4. Improved Filtering and Categorization

**Add Categories**:
1. **Prediction Models**: Articles developing/validating prediction models
2. **Risk Factors**: Articles identifying new risk factors
3. **Biomarkers**: Articles on biomarkers for progression
4. **Imaging**: Articles on imaging predictors
5. **Clinical Factors**: Articles on clinical/symptom predictors
6. **Interventions**: Articles on modifiable factors
7. **Reviews**: Systematic reviews and meta-analyses

**Add Tags**:
- `high-priority`: Score ≥80
- `modifiable-factors`: Identifies changeable factors
- `large-sample`: n≥500
- `longitudinal`: Follow-up ≥2 years
- `recent`: <2 years old
- `top-journal`: High-impact journal

---

## Implementation Plan

### Phase 1: Enhanced Search Strategy
1. Create comprehensive search query with multiple concepts
2. Expand date range to 10 years
3. Remove restrictive publication type filters
4. Add MeSH terms for better coverage

### Phase 2: Improved Relevance Scoring
1. Implement multi-dimensional scoring system
2. Add recency weighting
3. Add actionability scoring
4. Create value categories

### Phase 3: Better Filtering
1. Add article categories
2. Add tags for quick filtering
3. Create priority levels
4. Add "must-read" flagging

### Phase 4: Reporting Improvements
1. Generate summary statistics:
   - Total articles found
   - High-value articles (score ≥80)
   - Medium-value articles (score 60-79)
   - By category
   - By recency
2. Create "Top Articles" report
3. Generate "Action Items" list

---

## Expected Outcomes

### Before Improvements:
- ~100 articles per run
- ~3 high-relevance articles (score ≥70)
- Limited coverage of literature

### After Improvements:
- **1,000-5,000 articles** per initial run (then incremental)
- **50-200 high-value articles** (score ≥80)
- **200-500 medium-value articles** (score 60-79)
- Comprehensive coverage of literature
- Better identification of truly valuable articles

---

## Next Steps

1. ✅ Review current system (done)
2. ⏳ Implement enhanced search strategy
3. ⏳ Update relevance scoring algorithm
4. ⏳ Add categorization and tagging
5. ⏳ Test with full search
6. ⏳ Generate improved reports

