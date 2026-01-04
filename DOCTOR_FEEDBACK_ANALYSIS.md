# Doctor Feedback Analysis - Key Issues & Recommendations

**Date:** 2025-01-XX  
**From:** Doctor M (Orthopedic Surgeon)  
**Context:** User testing feedback on DOC platform

---

## Summary of Doctor's Feedback

### 1. **Articles Question** ✅ Simple
- Doctor is offering to send full-text of paywalled articles
- **Action:** Confirm if you want them, and how to receive (email, shared folder, etc.)

### 2. **UI/UX Issues** ⚠️ **CRITICAL - Needs Immediate Attention**

#### **A. Information Hierarchy Problem**
**Current State:**
- Results start with "Average Risk" (unclear what this means)
- Shows "High Risk Patients" count without clear definition
- Expected WOMAC/function/pain progress is buried in Stage 2

**Doctor's Need:**
> "If I were an orthopaedic surgeon using the system, I would like to know the expected amount of progress in WOMAC / function / pain mostly. So that would mean that this result should be the first thing you see imo."

**Issue:** The most clinically relevant information (expected improvement) is not prominent enough.

#### **B. Missing Key Information**
**Current State:**
- Shows success categories (Excellent, Successful, etc.)
- Shows success probability (%)
- Shows yes/no for surgical success

**Doctor's Need:**
> "For surgical success (the main thing): it shows yes / no if the surgery will be a success. I think that is an important parameter. Is it possible to show how much WOMAC will progress? If not 30 how much then? And if over 30, how much then?"

**Issue:** The system calculates predicted WOMAC improvement points (`_womac_improvement`) but **doesn't display them** to the user. The doctor wants to see:
- **Actual predicted improvement points** (e.g., "Expected improvement: 35 points")
- **Not just categories** (e.g., "Successful Outcome")

#### **C. Unclear Risk Definitions**
**Current State:**
- Shows "Average Risk" without explanation
- Shows "High Risk" without threshold definition

**Doctor's Need:**
> "It is not clear to me what that risk consists of. It shows as well something about high risk. When is a patient high risk?"

**Issue:** Risk categories need clear definitions and thresholds.

#### **D. Complex/Unclear Graphs**
**Current State:**
- Multiple charts (risk distribution, ROC curves, etc.)
- Technical validation metrics

**Doctor's Need:**
> "The graphs in what we display now are quite hard to understand. Maybe think about removing them? Or make them more practical."

**Issue:** Charts are too technical for clinical use.

### 3. **Project Summary for Monday Meeting** ✅ Confirmation Needed
Doctor is asking if their summary is accurate:
- Making prediction model of TKR
- Using OAI data
- Gathering parameters from expanding Pubmed studies
- Future: add LROI data
- Then: add chance and effect size for non-surgical treatment options

---

## Technical Analysis

### What the System Currently Does

1. **Model 1 (Risk Prediction):**
   - Predicts probability of needing TKR within 4 years
   - Shows: Average Risk, High Risk count, Risk categories

2. **Model 2 (Outcome Prediction):**
   - Predicts WOMAC improvement after TKA
   - Calculates: `_womac_improvement` (actual points)
   - Converts to: Success categories and probabilities
   - **Problem:** The actual improvement points are NOT displayed in the UI

### What's Missing

1. **Predicted WOMAC Improvement Points** - The system has this data (`_womac_improvement`) but doesn't show it
2. **Clear Risk Definitions** - Thresholds for "High Risk" are not explained
3. **Prominent Outcome Display** - Expected improvement should be FIRST thing shown
4. **Simplified Visualizations** - Charts are too technical

---

## Recommended Changes (Priority Order)

### **PRIORITY 1: Show Actual Predicted Improvement Points**

**Location:** Individual patient outcome cards + summary

**Change:**
- Display: **"Expected Improvement: 35 points"** (or whatever the prediction is)
- Show this prominently, not just categories
- Answer the doctor's question: "If not 30, how much then? And if over 30, how much then?"

**Implementation:**
- The data exists: `patient._womac_improvement` is already calculated
- Just needs to be displayed in the UI

### **PRIORITY 2: Restructure Information Hierarchy**

**Change:**
- **Move expected improvement to the TOP** of results
- Show per-patient: "Expected WOMAC improvement: X points"
- Show summary: "Average expected improvement: X points"
- Move risk scores to secondary position

**Current Flow:**
1. Risk scores (Average Risk, High Risk)
2. Outcome predictions (buried in Stage 2)

**New Flow:**
1. **Expected improvement** (WOMAC/function/pain) ← **FIRST**
2. Surgical success probability
3. Risk scores (secondary)

### **PRIORITY 3: Clarify Risk Definitions**

**Add:**
- Tooltip/help text explaining "Average Risk" = average probability of needing TKR
- Clear threshold: "High Risk = ≥X% probability of needing TKR within 4 years"
- Brief explanation of what "risk" means in this context

### **PRIORITY 4: Simplify or Remove Complex Graphs**

**Options:**
1. **Remove** technical validation charts (ROC curves, calibration plots)
2. **Simplify** to only show:
   - Distribution of expected improvements (bar chart)
   - Simple risk distribution (if needed)
3. **Move** technical metrics to "Advanced" or "Developer" section

### **PRIORITY 5: Improve Individual Patient Display**

**Current patient card shows:**
- Surgery Risk
- Expected Outcome (category)
- Success Probability

**Should also show:**
- **Predicted WOMAC Improvement: X points** ← **ADD THIS**
- Clear indication: "≥30 points = Successful" or "<30 points = X points expected"

---

## Code Changes Needed

### File: `DOC_Validator_Vercel/public/static/js/main.js`

**Function: `displayFilteredPatients()` (line ~1604)**

**Current:**
```javascript
<div style="font-size: 0.85rem; color: #64748b; margin-bottom: 4px;">Expected Outcome</div>
<div style="font-size: 1.1rem; font-weight: 600; color: ${colors.text}; margin-bottom: 8px;">
  ${patient.success_category}
</div>
```

**Add:**
```javascript
${patient._womac_improvement !== undefined ? `
  <div style="font-size: 0.9rem; color: #2d3748; margin-bottom: 8px; font-weight: 600;">
    Expected Improvement: <span style="color: ${colors.text}; font-size: 1.2rem;">${patient._womac_improvement.toFixed(1)} points</span>
  </div>
  ${patient._womac_improvement >= 30 ? `
    <div style="font-size: 0.8rem; color: #059669; margin-top: 4px;">✓ Meets success threshold (≥30 points)</div>
  ` : `
    <div style="font-size: 0.8rem; color: #dc2626; margin-top: 4px;">Below success threshold (needs ${(30 - patient._womac_improvement).toFixed(1)} more points)</div>
  `}
` : ''}
```

**Function: `displayOutcomeResults()` (line ~654)**

**Add summary metric:**
```javascript
// Add after success rate metric
const avgImprovement = outcomes.patient_outcomes?.reduce((sum, p) => sum + (p._womac_improvement || 0), 0) / (outcomes.n_analyzed || 1);

html += `<div class="metric-card outcome-card highlight-card">
  <div class="metric-value">${avgImprovement.toFixed(1)}</div>
  <div class="metric-label">Average Expected Improvement (points)</div>
</div>`;
```

### File: `DOC_Validator_Vercel/public/static/js/main.js`

**Function: `displayResults()` (line ~146)**

**Restructure to show outcomes first:**
- Move outcome section before risk section
- Or add prominent link/callout to outcomes

---

## Response to Doctor

### Articles
- Confirm if you want full-text articles
- Provide preferred method (email, shared folder, etc.)

### UI Changes
- Acknowledge all feedback
- Confirm you'll prioritize showing actual improvement points
- Explain timeline for changes

### Project Summary
- Confirm their summary is accurate
- Add any clarifications needed

---

## Implementation Checklist

- [ ] Add `_womac_improvement` display to patient cards
- [ ] Add average improvement to summary metrics
- [ ] Restructure results to show outcomes first
- [ ] Add risk definition tooltips/help text
- [ ] Simplify or remove complex graphs
- [ ] Test with sample data
- [ ] Update documentation

---

## Key Insight

**The doctor wants NUMBERS, not just categories.**

They want to know:
- "This patient will improve by 35 points" (not just "Successful Outcome")
- "This patient will improve by 22 points" (not just "Moderate Improvement")

The system already calculates these numbers - they just need to be displayed prominently.

