# Quick Start: Article Flagging Framework

## Overview

The Article Flagging Framework automatically identifies which articles should be reviewed based on multiple criteria. This ensures high-value, actionable articles are prioritized.

## How It Works

### Automatic Flagging

Articles are **automatically flagged** during processing if they meet any of these criteria:

1. **High Priority** (Score ≥ 80): Must review immediately
2. **Medium-High Priority** (Score 70-79): Should review soon  
3. **Paywalled High-Value** (Score ≥ 80, Paywalled): Consider obtaining access
4. **Recent High-Value** (Score ≥ 70, < 1 year old): Latest findings
5. **Large Sample** (n ≥ 500, Score ≥ 60): Robust evidence
6. **Systematic Review** (Score ≥ 60): Comprehensive overview
7. **Novel Findings** (Novelty ≥ 15, Score ≥ 70): New insights
8. **Actionable** (Actionability ≥ 7, Score ≥ 70): Clinical application

### What You'll See

In `LATEST_FINDINGS.md` and reports, you'll see:

```
## Articles Flagged for Review

### Priority Breakdown
- High Priority (Must Review): 15
- Medium-High Priority (Should Review): 42
- Paywalled High-Value: 8
- Recent High-Value: 23
- Large Sample Studies: 12
- Systematic Reviews: 5
- Novel Findings: 18
- Actionable Insights: 31

### Top Priority Articles for Review

1. **Article Title** (Score: 85/100)
   - Flags: high_value, must_review
   - Reason: High-value article (score: 85)
   - Access: open_access
   - [PubMed Link]
```

## Relevance Scoring

Each article gets a score 0-100 based on:

- **Clinical Relevance** (0-40): How directly it predicts TKR/progression
- **Study Quality** (0-30): Design, sample size, follow-up
- **Novelty/Impact** (0-20): Journal quality, recency, novel findings
- **Actionability** (0-10): Modifiable factors, clinical applicability

## Value Categories

- **High Value (80-100)**: Must-read, actionable
- **Medium-High (70-79)**: Very relevant
- **Medium (60-69)**: Relevant
- **Low (40-59)**: Somewhat relevant
- **Very Low (0-39)**: Minimally relevant

## Priority Levels

Articles are sorted by **priority score**:
- Base relevance score
- +20 for `must_review` flag
- +10 for `consider_access` flag
- +5 for `recent`, `novel`, or `actionable` flags

## Expected Results

For 1,000 articles:
- **200-400 articles flagged** (20-40%)
- **50-200 high priority** (5-20%)
- **100-300 medium-high priority** (10-30%)

## Configuration

Flagging criteria can be adjusted in `config/flagging_criteria.json`:

```json
{
  "high_priority": {
    "min_score": 80,
    "description": "Must-read, actionable, high-quality articles",
    "flags": ["high_value", "must_review"],
    "action": "Review immediately"
  }
}
```

## No Action Required

The system **automatically flags articles** during processing. You just need to:

1. Check `LATEST_FINDINGS.md` after each run
2. Review prioritized articles
3. Focus on high-priority articles first

## Questions?

See `ARTICLE_FLAGGING_FRAMEWORK.md` for complete documentation.

