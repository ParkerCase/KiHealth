# Article Flagging Framework

## Overview

The Article Flagging Framework determines which articles should be flagged for review based on multiple criteria. This ensures that high-value, actionable articles are prioritized for doctor review.

## How Articles Are Flagged

### Flagging Criteria

Articles are flagged for review if they meet **any** of the following criteria:

#### 1. High Priority (Score ≥ 80)
- **Description**: Must-read, actionable, high-quality articles
- **Flags**: `high_value`, `must_review`
- **Action**: Review immediately

#### 2. Medium-High Priority (Score 70-79)
- **Description**: Very relevant, good quality
- **Flags**: `medium_high`, `should_review`
- **Action**: Review soon

#### 3. Paywalled High-Value (Score ≥ 80, Paywalled)
- **Description**: High-value paywalled articles that may need access
- **Flags**: `paywalled`, `high_value`, `consider_access`
- **Action**: Consider obtaining access

#### 4. Recent High-Value (Score ≥ 70, < 1 year old)
- **Description**: Recent high-value articles
- **Flags**: `recent`, `high_value`, `priority`
- **Action**: Review for latest findings

#### 5. Large Sample Size (n ≥ 500, Score ≥ 60)
- **Description**: Large sample size studies
- **Flags**: `large_sample`, `high_quality`
- **Action**: Review for robust evidence

#### 6. Systematic Review (Systematic Review/Meta-analysis, Score ≥ 60)
- **Description**: Systematic reviews and meta-analyses
- **Flags**: `systematic_review`, `comprehensive`
- **Action**: Review for comprehensive overview

#### 7. Novel Findings (Novelty Score ≥ 15, Overall Score ≥ 70)
- **Description**: Articles with novel findings
- **Flags**: `novel`, `high_impact`
- **Action**: Review for new insights

#### 8. Actionable (Actionability Score ≥ 7, Overall Score ≥ 70)
- **Description**: Articles with actionable insights
- **Flags**: `actionable`, `clinical_applicable`
- **Action**: Review for clinical application

## Relevance Scoring Breakdown

Each article receives a multi-dimensional score:

### Clinical Relevance (0-40 points)
- **High (30-40)**: Directly predicts TKR/progression, actionable
- **Medium (20-29)**: Related to progression, may be useful
- **Low (10-19)**: OA-related but not progression-focused
- **Very Low (0-9)**: Minimally relevant

### Study Quality (0-30 points)
- **Study Design** (15 pts): Systematic review (15), Cohort (12), RCT (10), Case-control (8), Cross-sectional (5)
- **Sample Size** (10 pts): >1000 (10), 500-1000 (8), 100-500 (5), <100 (2)
- **Follow-up Duration** (5 pts): >5 years (5), 2-5 years (3), <2 years (1)

### Novelty/Impact (0-20 points)
- **Journal Impact** (10 pts): Top-tier (10), Mid-tier (7), Other (3)
- **Recency** (5 pts): <1 year (5), 1-2 years (3), 2-5 years (1)
- **Novel Findings** (5 pts): New factors, new methods, significant results

### Actionability (0-10 points)
- **Modifiable Factors** (5 pts): Identifies factors that can be changed
- **Clinical Applicability** (5 pts): Results can be used in practice

**Total Score**: 0-100

## Value Categories

Based on total score:

- **High Value (80-100)**: Must-read, actionable, high-quality
- **Medium-High Value (70-79)**: Very relevant, good quality
- **Medium Value (60-69)**: Relevant, may be useful
- **Low Value (40-59)**: Somewhat relevant, lower quality
- **Very Low Value (0-39)**: Minimally relevant or poor quality

## Priority Levels

Articles are assigned priority levels for review:

- **High Priority**: Score ≥ 80, or has `must_review` flag
- **Medium-High Priority**: Score 70-79, or has `should_review` flag
- **Medium Priority**: Score 60-69
- **Low Priority**: Score 40-59
- **Very Low Priority**: Score < 40

## Review Priority Calculation

Articles are sorted by a **priority score** that combines:
- Base relevance score
- +20 for `must_review` flag
- +10 for `consider_access` flag (paywalled high-value)
- +5 for `recent` flag
- +5 for `novel` flag
- +5 for `actionable` flag

## Usage

### In Code

```python
from scripts.article_flagging import ArticleFlaggingFramework

framework = ArticleFlaggingFramework()

# Check if article should be flagged
should_flag, flags, reason = framework.should_flag_for_review(article)

# Get flagging summary for all articles
summary = framework.get_flagging_summary(articles)

# Get prioritized review list
prioritized = framework.get_review_priority_list(articles)
```

### In Reports

The framework automatically generates:
- **Flagging Summary**: Counts by priority type
- **Prioritized List**: Articles sorted by priority score
- **Flag Details**: Which flags each article has and why

## Configuration

Flagging criteria can be customized in `config/flagging_criteria.json`:

```json
{
  "high_priority": {
    "min_score": 80,
    "description": "Must-read, actionable, high-quality articles",
    "flags": ["high_value", "must_review"],
    "action": "Review immediately"
  },
  ...
}
```

## Expected Results

### Typical Distribution

For 1,000 articles:
- **High Priority (≥80)**: 50-200 articles (5-20%)
- **Medium-High (70-79)**: 100-300 articles (10-30%)
- **Medium (60-69)**: 200-500 articles (20-50%)
- **Low (40-59)**: 300-800 articles (30-80%)
- **Very Low (<40)**: Remaining articles

### Flagging Rate

Typically **20-40%** of articles will be flagged for review, with:
- **5-10%** high priority (must review)
- **10-20%** medium-high priority (should review)
- **5-10%** other flags (paywalled, recent, etc.)

## Benefits

1. **Prioritization**: Focus on most valuable articles first
2. **Comprehensive**: Multiple criteria ensure nothing important is missed
3. **Transparent**: Clear reasons for flagging
4. **Customizable**: Criteria can be adjusted
5. **Actionable**: Clear action items for each flag type

## Examples

### Example 1: High-Value Article
- **Score**: 85
- **Flags**: `high_value`, `must_review`
- **Reason**: "High-value article (score: 85)"
- **Action**: Review immediately

### Example 2: Paywalled High-Value
- **Score**: 82
- **Access**: Paywalled
- **Flags**: `paywalled`, `high_value`, `consider_access`
- **Reason**: "High-value paywalled article (score: 82)"
- **Action**: Consider obtaining access

### Example 3: Recent Novel Finding
- **Score**: 75
- **Age**: 6 months
- **Novelty Score**: 18
- **Flags**: `recent`, `high_value`, `priority`, `novel`, `high_impact`
- **Reason**: "Recent high-value article (180 days old); Novel findings (novelty score: 18)"
- **Action**: Review for latest findings and new insights

## Maintenance

The framework is designed to be:
- **Robust**: Handles missing data gracefully
- **Extensible**: Easy to add new criteria
- **Testable**: Clear logic for testing
- **Documented**: Well-documented code and config

## Questions?

See `DOCTOR_QUESTIONS_ANSWERED.md` for more details on how articles are evaluated and flagged.

