# Implementation Plan: Enhanced Search & Relevance Scoring

## Overview

This document outlines the implementation plan to address the doctor's concerns about:
1. Limited article yield (only ~100 articles)
2. Need for proper PubMed search strategies
3. Better article value determination

## Phase 1: Enhanced Search Strategy ✅ (Ready to Implement)

### Files to Modify
- `scripts/pubmed_scraper.py` - Update `run()` method
- `config/search_strategy.json` - New comprehensive search queries

### Changes Needed

1. **Load search strategy from config**
   ```python
   # Load search strategy
   strategy_path = os.path.join(project_root, 'config', 'search_strategy.json')
   with open(strategy_path, 'r') as f:
       search_config = json.load(f)
   ```

2. **Use comprehensive search query**
   ```python
   # Use comprehensive search instead of basic query
   query = search_config['search_strategies']['comprehensive']['query']
   max_results = search_config['search_strategies']['comprehensive']['max_results']
   ```

3. **Update date range**
   ```python
   # Change from 5 years to 10 years
   mindate = (datetime.now() - timedelta(days=10*365)).strftime('%Y/%m/%d')
   ```

### Expected Impact
- **Before**: ~100 articles per run
- **After**: 1,000-5,000 articles initially, then 50-200 per week

---

## Phase 2: Enhanced Relevance Scoring ✅ (Ready to Implement)

### Files to Modify
- `scripts/relevance_scoring.py` - Add enhanced scoring methods
- OR create `scripts/enhanced_relevance_scoring.py` - New enhanced scorer

### Changes Needed

1. **Add multi-dimensional scoring**
   - Clinical Relevance (0-40)
   - Study Quality (0-30)
   - Novelty/Impact (0-20)
   - Actionability (0-10)

2. **Add value categories**
   - High value (≥80)
   - Medium-high (70-79)
   - Medium (60-69)
   - Low (40-59)
   - Very low (<40)

3. **Update article storage**
   - Store score breakdown
   - Store value category
   - Store priority level

### Expected Impact
- **Before**: Only 3 articles with score ≥70
- **After**: 50-200 high-value articles (≥80), 100-300 medium-high (70-79)

---

## Phase 3: Better Reporting ✅ (Ready to Implement)

### Files to Create/Modify
- `scripts/generate_enhanced_report.py` - New reporting script
- `scripts/analyze_and_notify.py` - Update to use enhanced scoring

### Features to Add

1. **Summary Statistics**
   - Total articles found
   - Distribution by value category
   - Distribution by access type
   - Top articles list

2. **Value-Based Reports**
   - High-value articles report
   - Medium-high articles report
   - Paywalled high-value articles
   - Action items list

3. **Better Categorization**
   - By prediction model type
   - By risk factor type
   - By study design
   - By recency

### Expected Impact
- Clear identification of must-read articles
- Better prioritization for review
- Comprehensive literature overview

---

## Implementation Steps

### Step 1: Update Search Strategy (30 min)
1. ✅ Create `config/search_strategy.json` (done)
2. ⏳ Update `pubmed_scraper.py` to load and use comprehensive search
3. ⏳ Test search query manually in PubMed
4. ⏳ Update date range to 10 years

### Step 2: Implement Enhanced Scoring (1 hour)
1. ✅ Create `scripts/enhanced_relevance_scoring.py` (done)
2. ⏳ Update `pubmed_scraper.py` to use enhanced scorer
3. ⏳ Update article storage to include score breakdown
4. ⏳ Test scoring on sample articles

### Step 3: Update Reporting (1 hour)
1. ⏳ Create enhanced reporting script
2. ⏳ Update `analyze_and_notify.py`
3. ⏳ Generate value-based reports
4. ⏳ Test report generation

### Step 4: Testing (1 hour)
1. ⏳ Run comprehensive search (test mode, limit to 100)
2. ⏳ Verify enhanced scoring works
3. ⏳ Check report generation
4. ⏳ Review sample articles for accuracy

### Step 5: Full Implementation (2 hours)
1. ⏳ Run full comprehensive search
2. ⏳ Process all articles with enhanced scoring
3. ⏳ Generate comprehensive reports
4. ⏳ Review and validate results

---

## Testing Strategy

### Test 1: Search Query Validation
- Run comprehensive search query in PubMed web interface
- Verify it returns expected number of results
- Check that results are relevant

### Test 2: Scoring Validation
- Score 10 known high-value articles
- Score 10 known low-value articles
- Verify scores match expectations
- Check score breakdowns

### Test 3: Report Generation
- Generate reports with sample data
- Verify statistics are correct
- Check formatting and readability

### Test 4: End-to-End Test
- Run full scraper with enhanced search
- Process articles with enhanced scoring
- Generate reports
- Review results

---

## Rollout Plan

### Phase A: Development (Week 1)
- Implement enhanced search strategy
- Implement enhanced scoring
- Create enhanced reporting
- Test thoroughly

### Phase B: Staging (Week 2)
- Run on staging/test data
- Review results with doctor
- Adjust thresholds if needed
- Refine scoring algorithm

### Phase C: Production (Week 3)
- Deploy to production
- Run initial comprehensive search
- Generate reports
- Monitor for issues

---

## Success Metrics

### Search Coverage
- ✅ Find 1,000+ articles (vs current ~100)
- ✅ Cover 10-year period (vs current 5 years)
- ✅ Include MeSH terms and synonyms

### Value Identification
- ✅ Identify 50+ high-value articles (vs current 3)
- ✅ Better distribution across value categories
- ✅ Clear prioritization for review

### Reporting Quality
- ✅ Clear summary statistics
- ✅ Value-based categorization
- ✅ Actionable insights

---

## Risk Mitigation

### Risk 1: Too Many Articles
- **Mitigation**: Use incremental updates after initial run
- **Mitigation**: Filter by date (only new articles weekly)

### Risk 2: Scoring Too Strict/Lenient
- **Mitigation**: Test on known articles first
- **Mitigation**: Allow threshold adjustment
- **Mitigation**: Provide score breakdowns for transparency

### Risk 3: Performance Issues
- **Mitigation**: Process in batches
- **Mitigation**: Use rate limiting
- **Mitigation**: Cache results

---

## Next Steps

1. **Review this plan** with the doctor
2. **Get approval** for implementation
3. **Start Phase 1** (Enhanced Search Strategy)
4. **Test and iterate**
5. **Deploy to production**

---

## Questions to Address

1. **Date Range**: 10 years or keep 5 years?
2. **Initial Search**: Run comprehensive search once, then incremental?
3. **Scoring Thresholds**: Are the proposed thresholds (80/70/60/40) appropriate?
4. **Reporting Frequency**: Weekly reports or on-demand?
5. **Article Limit**: Any limit on articles processed per run?

