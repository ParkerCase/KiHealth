# Automated Learning Safety Mechanisms

## Overview

This document describes the safety mechanisms in place to ensure that the automated literature mining system **never automatically modifies the prediction model** without explicit human review and validation.

## Core Safety Principles

### 1. **Read-Only Model Access**
- ✅ The literature mining system has **NO access** to modify model files
- ✅ Model files (`models/*.pkl`) are **never automatically updated**
- ✅ All model changes require **manual intervention** and **explicit approval**

### 2. **Notification-Only System**
- ✅ The system **only creates notifications** (GitHub issues, summaries)
- ✅ All findings are **flagged for review**, not automatically integrated
- ✅ Human review is **required** before any model changes

### 3. **Validation Requirements**
- ✅ All potential new parameters must pass **PROBAST compliance checks**
- ✅ Statistical validation required (EPV ≥15, significance testing)
- ✅ Clinical validation required (data availability, accessibility)
- ✅ External validation required before deployment

## Current Model Parameters (Protected)

The following parameters are currently in the model and will **not** be flagged as "new":

- Age
- Sex/Gender
- BMI (Body Mass Index)
- Race/Ethnicity
- Cohort (Progression/Incidence)
- WOMAC Total (Right/Left)
- KL Grade (Kellgren-Lawrence, Right/Left)
- Family History
- Walking Distance (400m walk time)

## Automated Detection Process

### Step 1: Literature Mining (Weekly)
- System searches PubMed for new OA/TKR studies
- Extracts predictive factors from abstracts and full-text
- Calculates relevance scores (0-100)
- Flags articles with score ≥70

### Step 2: Factor Extraction
- NLP-based extraction of predictive factors
- Statistical associations identified (OR, HR, p-values)
- Factors compared against current model parameters

### Step 3: New Parameter Detection
- Factors **not** in current model are flagged
- Only factors with **statistical evidence** are considered
- Minimum threshold: 5+ high-relevance articles

### Step 4: Notification Creation
- GitHub issue created with potential new parameters
- Includes evidence, articles, and review checklist
- **NO automatic model updates**

## Review Checklist (Required Before Integration)

Before any new parameter can be added to the model:

- [ ] **Verify factor is not already in model** (check synonyms)
- [ ] **Confirm data availability** in OAI or clinical practice
- [ ] **Verify statistical significance** across multiple studies
- [ ] **Check EPV compliance** (≥15 events per variable)
- [ ] **Assess clinical accessibility** (routinely available)
- [ ] **Evaluate multicollinearity** with existing predictors
- [ ] **Review PROBAST compliance impact**
- [ ] **Test model performance** with new parameter
- [ ] **Validate on external dataset**

## Integration Workflow (Manual)

If a new parameter passes all checks:

1. **Data Preparation**
   - Extract variable from OAI dataset
   - Check completeness (>90% preferred)
   - Handle missing data appropriately

2. **Model Retraining**
   - Add parameter to feature set
   - Verify EPV ≥15
   - Retrain model with new parameter
   - Compare performance (AUC, calibration)

3. **Validation**
   - Internal validation (cross-validation)
   - External validation (if available)
   - PROBAST reassessment

4. **Deployment**
   - Update preprocessing pipeline
   - Update frontend form
   - Update documentation
   - Deploy to production

## Safety Guarantees

### ✅ What the System DOES:
- Searches PubMed automatically (weekly)
- Extracts predictive factors
- Flags potential new parameters
- Creates GitHub notifications
- Generates review summaries

### ❌ What the System DOES NOT DO:
- **Never** modifies model files automatically
- **Never** adds parameters without review
- **Never** deploys changes automatically
- **Never** bypasses validation requirements

## Monitoring and Alerts

### Weekly Reports
- `LATEST_FINDINGS.md` - Summary of all findings
- GitHub issues for:
  - Paywalled high-value articles
  - Factor patterns
  - **Potential new parameters** (NEW)

### Alert Thresholds
- **High Priority**: Score ≥80, 5+ articles
- **Medium Priority**: Score 70-79, 5+ articles
- **Review Required**: Any potential new parameter

## PROBAST Compliance

All new parameters must maintain:
- ✅ EPV ≥15 (events per variable)
- ✅ Low risk of bias
- ✅ Transparent predictor selection
- ✅ Clinical relevance
- ✅ Data availability

## Emergency Procedures

If the system detects a critical finding:

1. **Immediate Notification**: GitHub issue with `critical` label
2. **Review Priority**: Highest priority flag
3. **Validation Required**: All checks must pass
4. **No Automatic Action**: Still requires manual approval

## Audit Trail

All actions are logged:
- Literature searches (weekly)
- Factor extractions
- Notification creation
- Review status
- Integration decisions

## Contact

For questions about the automated learning system:
- Check `LATEST_FINDINGS.md` for latest findings
- Review GitHub issues tagged `new-parameters`
- Follow the review checklist before integration

---

**Last Updated:** 2025-01-XX  
**Status:** ✅ Active - Safety mechanisms in place  
**Next Review:** After first potential parameter detection

