# Complete Re-Analysis Plan - NO SHORTCUTS

**Date:** November 7, 2025
**Goal:** 100% accurate, comprehensive analysis using ALL available data

## What Was Wrong

1. ❌ Synthetic lethality interpretation BACKWARDS (positive Δ ≠ SL)
2. ❌ Only 237/1186 cell lines used (20% of data)
3. ❌ Expression correlation incomplete
4. ❌ Copy number analysis not done
5. ❌ Damaging mutations not used
6. ❌ False claims of completeness

## What Will Be Done - In Order

### Phase 1: Re-run Synthetic Lethality (CORRECTLY) - 2 hours
- [ ] Use ALL 1,186 DepMap cell lines (not just 237)
- [ ] Include BOTH hotspot AND damaging mutations
- [ ] Correct interpretation: NEGATIVE Δ = synthetic lethality
- [ ] Output: `synthetic_lethality_results_COMPLETE.csv`
- [ ] Validation: Check every result manually against DepMap portal

### Phase 2: Expression Correlation Analysis - 2 hours
- [ ] Load CCLE expression data for all 4 targets
- [ ] Correlate expression with dependency across ALL cell lines
- [ ] Identify cancer types with HIGH expression AND HIGH dependency
- [ ] Output: `expression_correlation_COMPLETE.csv`
- [ ] Create visualizations
- [ ] Validation: Verify correlation coefficients make sense

### Phase 3: Copy Number Analysis - 2 hours
- [ ] Load OmicsCNGeneWGS.csv
- [ ] Extract copy number for 4 targets across all cell lines
- [ ] Identify amplifications (CN > 0.5)
- [ ] Calculate impact on dependency scores
- [ ] Output: `copy_number_analysis_COMPLETE.csv`
- [ ] Validation: Check a few cell lines manually

### Phase 4: Experimental Validation Integration - 2 hours
- [ ] Load StarX experimental data (IC50 from 160 cell lines)
- [ ] Match with DepMap predictions
- [ ] Calculate validation_score per cancer type
- [ ] Output: `experimental_validation_COMPLETE.csv`
- [ ] Validation: Correlate predictions with actual results

### Phase 5: Comprehensive Integration - 2 hours
- [ ] Merge ALL evidence dimensions
- [ ] Recalculate overall scores with proper weights
- [ ] Generate final rankings with confidence tiers
- [ ] Output: `final_integrated_rankings_COMPLETE.csv`
- [ ] Validation: Top 10 must make biological sense

### Phase 6: Verification & Documentation - 1 hour
- [ ] Cross-check against DepMap portal for top hits
- [ ] Verify all numbers can be reproduced
- [ ] Document what data was used (percentages, sources)
- [ ] Create limitations section (what we still don't have)
- [ ] NO claims of completeness unless truly verified

## Success Criteria

✅ Can reproduce any number by going back to source data
✅ Synthetic lethality candidates have NEGATIVE effect sizes
✅ Used >90% of available DepMap data
✅ All planned analyses actually completed
✅ Results match DepMap portal spot checks
✅ Honest about limitations

## Estimated Time: 11 hours

**Starting NOW.**
