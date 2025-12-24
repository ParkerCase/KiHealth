# Answers to Doctor's Questions

## Question 1: "How many articles will the scraping provide us?"

### Current Situation
- **Current yield**: ~100 articles per run (limited by `MAX_ARTICLES_PER_RUN=100`)
- **Reality**: There are likely **thousands** of relevant articles in PubMed

### Expected with Proper Search Strategy

**Initial comprehensive search**:
- **5,000-10,000+ articles** matching a comprehensive search strategy
- After deduplication: **3,000-7,000 unique articles**
- After basic filtering: **1,000-2,000 high-quality articles**

**Ongoing weekly monitoring**:
- **50-200 new articles** per week (depending on publication rate)
- **10-50 high-value articles** per week

### Why the Discrepancy?

**Current search is too narrow**:
```
Current: ("knee osteoarthritis" OR "knee OA") AND 
         ("progression" OR "total knee replacement" OR "arthroplasty") 
         AND (human[Filter]) 
         AND (Clinical Trial[ptyp] OR Cohort Studies[ptyp] OR Systematic Review[ptyp])
```

**Problems**:
1. Only searches last 5 years
2. Only specific publication types
3. Limited search terms (missing synonyms, MeSH terms)
4. No MeSH term expansion
5. Too restrictive filters

**Proper systematic review search would include**:
- Multiple synonyms for knee OA
- MeSH terms (Medical Subject Headings)
- Multiple outcome terms
- Prediction/prognosis terms
- 10-year date range (not just 5)
- All relevant publication types

---

## Question 2: "Is that not needed in our case to be able to find all relevant articles out there?"

### Answer: **YES, absolutely!**

**Why we need proper search strategies**:

1. **Systematic Reviews Use Comprehensive Searches**
   - They aim to find ALL relevant articles
   - Use multiple search concepts
   - Include MeSH terms and synonyms
   - Search multiple databases
   - Document search strategy for reproducibility

2. **Current Approach Misses Articles**
   - Only finds ~100 articles when thousands exist
   - May miss important studies using different terminology
   - Doesn't use MeSH terms (PubMed's controlled vocabulary)
   - Too restrictive filters

3. **Example of What We're Missing**
   - Articles using "gonarthrosis" instead of "knee osteoarthritis"
   - Articles using "TKA" instead of "total knee arthroplasty"
   - Articles indexed with MeSH terms but not in title/abstract
   - Older articles (>5 years) that are still relevant
   - Articles in different publication types

### What We Should Do

**Implement a systematic review-style search strategy**:
- Multiple search concepts (disease, outcome, prediction)
- MeSH term expansion
- Synonym coverage
- Broader date range (10 years)
- Less restrictive filters
- Documented, reproducible search

---

## Question 3: "How do we determine if an article is valuable or not?"

### Current System

**Relevance Score (0-100)**:
- **Keywords** (40 points): Predictive factors, outcomes, imaging, symptoms, statistical terms
- **Study Design** (30 points): Systematic review (20), Cohort/RCT (15), Case-control (10), Cross-sectional (5)
- **Sample Size** (15 points): >1000 (15), 500-1000 (10), 100-500 (5), <100 (2)
- **Journal Impact** (15 points): Top-tier (15), Mid-tier (10), Other (5)

**Current Threshold**: Score ≥70 = "high relevance"

### Problems with Current System

1. **Score May Not Reflect True Value**
   - A score of 70 might be "interesting" but not "actionable"
   - Doesn't distinguish between "novel" vs "confirmatory"
   - Doesn't consider recency
   - Doesn't consider clinical applicability

2. **Why Only 3 High-Relevance Articles?**
   - Threshold of 70 may be too high
   - Scoring algorithm may be too strict
   - Many valuable articles might score 60-69
   - Need better categorization

### Improved Value Determination

**Multi-Dimensional Scoring**:

#### 1. Clinical Relevance (0-40 points)
- **High (30-40)**: Directly predicts TKR/progression, actionable findings
- **Medium (20-29)**: Related to progression, may be useful
- **Low (10-19)**: OA-related but not progression-focused
- **Very Low (0-9)**: Minimally relevant

#### 2. Study Quality (0-30 points)
- **Study Design** (15 pts): Systematic review (15), Cohort (12), RCT (10), Case-control (8), Cross-sectional (5)
- **Sample Size** (10 pts): >1000 (10), 500-1000 (8), 100-500 (5), <100 (2)
- **Follow-up** (5 pts): >5 years (5), 2-5 years (3), <2 years (1)

#### 3. Novelty/Impact (0-20 points)
- **Journal Impact** (10 pts): Top-tier (10), Mid-tier (7), Other (3)
- **Recency** (5 pts): <1 year (5), 1-2 years (3), 2-5 years (1)
- **Novel Findings** (5 pts): New factors, new methods, significant results

#### 4. Actionability (0-10 points)
- **Modifiable Factors** (5 pts): Identifies factors that can be changed
- **Clinical Applicability** (5 pts): Results can be used in practice

**New Value Categories**:
- **High Value (80-100)**: Must-read, actionable, high-quality
- **Medium Value (60-79)**: Relevant, good quality, may be useful
- **Low Value (40-59)**: Somewhat relevant, lower quality
- **Very Low Value (0-39)**: Minimally relevant or poor quality

### What Makes an Article "Valuable"?

**High-Value Articles Should Have**:
1. ✅ **Direct relevance**: Predicts TKR or progression
2. ✅ **Large sample**: >500 participants
3. ✅ **Good design**: Longitudinal/cohort study
4. ✅ **Actionable**: Identifies modifiable factors
5. ✅ **Recent or high-impact**: <3 years old or top journal
6. ✅ **Novel findings**: New factors or methods

**Medium-Value Articles**:
- Related to OA progression
- Moderate sample size (100-500)
- Good study design
- May provide supporting evidence

**Low-Value Articles**:
- OA-related but not progression-focused
- Small sample size (<100)
- Cross-sectional or case study
- Older (>5 years) or low-impact journal

---

## Addressing the Specific Concerns

### "Only 41 paywalled articles, only 3 high relevance"

**Why this happened**:
1. **Limited search**: Only finding ~100 articles total
2. **High threshold**: Score ≥70 may be too strict
3. **Scoring issues**: May not capture all valuable articles

**What we'll do**:
1. **Expand search**: Use comprehensive search strategy
2. **Adjust thresholds**: 
   - High value: ≥80 (truly exceptional)
   - Medium-high: 70-79 (very relevant)
   - Medium: 60-69 (relevant)
3. **Better categorization**: Not just "high/low", but multiple tiers
4. **Report all tiers**: Show distribution of scores

### "58 free articles but varying relevance"

**This is normal!** Not all articles will be high-value. We should:
1. **Categorize by value**: High/Medium/Low
2. **Prioritize review**: Start with high-value articles
3. **Track all articles**: Even low-value ones may have useful details
4. **Report distribution**: Show how many in each category

---

## Proposed Improvements

### 1. Enhanced Search Strategy ✅
- Comprehensive systematic review-style search
- Multiple search concepts
- MeSH term expansion
- 10-year date range
- Less restrictive filters

### 2. Improved Relevance Scoring ✅
- Multi-dimensional scoring
- Better value categories
- Actionability scoring
- Recency weighting

### 3. Better Reporting ✅
- Show total articles found
- Distribution by value category
- Top articles list
- Action items

### 4. Incremental Updates ✅
- Initial comprehensive search (one-time)
- Then weekly updates (new articles only)
- Avoid reprocessing existing articles

---

## Expected Outcomes After Improvements

### Search Results
- **Initial run**: 1,000-5,000 articles found
- **Weekly updates**: 50-200 new articles
- **Better coverage**: Won't miss relevant articles

### Value Distribution
- **High-value (≥80)**: 50-200 articles
- **Medium-high (70-79)**: 100-300 articles
- **Medium (60-69)**: 200-500 articles
- **Low (40-59)**: 300-800 articles
- **Very low (<40)**: Remaining articles

### Actionable Insights
- Clear identification of must-read articles
- Better prioritization for review
- More comprehensive literature coverage

---

## Next Steps

1. ✅ **Review current system** (done)
2. ⏳ **Implement enhanced search strategy** (in progress)
3. ⏳ **Update relevance scoring** (in progress)
4. ⏳ **Add better categorization** (in progress)
5. ⏳ **Test with comprehensive search**
6. ⏳ **Generate improved reports**

---

## Summary

**To answer your questions directly**:

1. **How many articles?** 
   - Currently: ~100 per run
   - With improvements: 1,000-5,000 initially, then 50-200 per week

2. **Do we need search strategies?**
   - **YES!** Current search is too narrow and misses many articles

3. **How do we determine value?**
   - Current: Single 0-100 score (threshold 70)
   - Improved: Multi-dimensional scoring with better categories
   - High-value (≥80): Must-read, actionable
   - Medium-high (70-79): Very relevant
   - Medium (60-69): Relevant
   - Low (<60): Less relevant

**The improvements will**:
- Find many more articles
- Better identify valuable ones
- Provide clearer prioritization
- Give you comprehensive literature coverage

