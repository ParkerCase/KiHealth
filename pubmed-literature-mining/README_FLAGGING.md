# Article Flagging Framework - Quick Reference

## How Articles Are Flagged for Review

### Automatic Flagging Criteria

Articles are **automatically flagged** during processing if they meet **ANY** of these 8 criteria:

| Criteria | Threshold | Flags | Action |
|----------|-----------|-------|--------|
| **High Priority** | Score ≥ 80 | `high_value`, `must_review` | Review immediately |
| **Medium-High Priority** | Score 70-79 | `medium_high`, `should_review` | Review soon |
| **Paywalled High-Value** | Score ≥ 80 + Paywalled | `paywalled`, `high_value`, `consider_access` | Consider obtaining access |
| **Recent High-Value** | Score ≥ 70 + < 1 year old | `recent`, `high_value`, `priority` | Review for latest findings |
| **Large Sample** | n ≥ 500 + Score ≥ 60 | `large_sample`, `high_quality` | Review for robust evidence |
| **Systematic Review** | Systematic review + Score ≥ 60 | `systematic_review`, `comprehensive` | Review for comprehensive overview |
| **Novel Findings** | Novelty ≥ 15 + Score ≥ 70 | `novel`, `high_impact` | Review for new insights |
| **Actionable** | Actionability ≥ 7 + Score ≥ 70 | `actionable`, `clinical_applicable` | Review for clinical application |

### Relevance Scoring (0-100)

**Clinical Relevance (0-40)**
- High (30-40): Directly predicts TKR/progression
- Medium (20-29): Related to progression
- Low (10-19): OA-related but not progression-focused
- Very Low (0-9): Minimally relevant

**Study Quality (0-30)**
- Study Design (15): Systematic review (15), Cohort (12), RCT (10), Case-control (8), Cross-sectional (5)
- Sample Size (10): >1000 (10), 500-1000 (8), 100-500 (5), <100 (2)
- Follow-up (5): >5 years (5), 2-5 years (3), <2 years (1)

**Novelty/Impact (0-20)**
- Journal Impact (10): Top-tier (10), Mid-tier (7), Other (3)
- Recency (5): <1 year (5), 1-2 years (3), 2-5 years (1)
- Novel Findings (5): New factors, new methods, significant results

**Actionability (0-10)**
- Modifiable Factors (5): Identifies changeable factors
- Clinical Applicability (5): Results usable in practice

### Priority Calculation

Articles are sorted by **priority score**:
- Base relevance score
- +20 for `must_review` flag
- +10 for `consider_access` flag  
- +5 for `recent` flag
- +5 for `novel` flag
- +5 for `actionable` flag

### Expected Distribution

For 1,000 articles:
- **Flagged**: 200-400 articles (20-40%)
- **High Priority**: 50-200 articles (5-20%)
- **Medium-High**: 100-300 articles (10-30%)
- **Other Flags**: 50-100 articles (5-10%)

## Where to Find Flagged Articles

### 1. LATEST_FINDINGS.md

After each run, check `LATEST_FINDINGS.md` for:
- Flagging summary with counts
- Priority breakdown
- Top 20 prioritized articles
- Flag details and reasons

### 2. Google Sheets

Articles are stored with:
- `relevance_score`: 0-100
- `value_category`: high_value, medium_value, etc.
- `priority_level`: high_priority, medium_high_priority, etc.
- `relevance_score_breakdown`: Detailed scoring breakdown

### 3. Reports

The `analyze_and_notify.py` script generates:
- Flagging summary
- Prioritized review list
- Top articles by category

## Configuration

Flagging criteria can be customized in `config/flagging_criteria.json`.

Thresholds can be adjusted:
- `high_priority.min_score`: Default 80
- `medium_high_priority.min_score`: Default 70
- `recent_high_value.max_age_days`: Default 365
- `large_sample.min_sample_size`: Default 500

## No Manual Action Required

The system **automatically flags articles** during processing. You just need to:

1. ✅ Check `LATEST_FINDINGS.md` after each run
2. ✅ Review prioritized articles (start with high priority)
3. ✅ Focus on articles with `must_review` or `should_review` flags

## Questions?

- See `ARTICLE_FLAGGING_FRAMEWORK.md` for complete documentation
- See `DOCTOR_QUESTIONS_ANSWERED.md` for detailed explanations
- See `FINAL_DEPLOYMENT_SUMMARY.md` for implementation details

