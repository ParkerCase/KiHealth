# Literature Quality Metrics Explanation

## 📋 Quick Summary (For Documentation)

**Relevance Score (0-100):** Measures how relevant an article is to knee OA prediction models. Calculated from topic relevance (40%), study design (30%), sample size (15%), and outcome relevance (15%). Scores ≥40 are considered for model use.

**PROBAST Risk:** Overall assessment of study quality using the Prediction model Risk Of Bias Assessment Tool. We use only Low Risk or Moderate Risk (with justification) articles. High Risk articles are excluded.

**PROBAST Domain 1 - Participants:** Quality of study population selection (representativeness, inclusion criteria).

**PROBAST Domain 2 - Predictors:** Quality of predictor variable definition and measurement (timing, consistency, no data dredging).

**PROBAST Domain 3 - Outcome:** Quality of outcome definition and measurement (objectivity, validation, blinding).

**PROBAST Domain 4 - Analysis:** Quality of statistical methods and model development (EPV ≥15, proper validation, handling of missing data).

**Our Standards:** All used articles have relevance score ≥40, 0 High Risk articles used, Moderate Risk articles used only with justification, top 7% PROBAST quality maintained.

---

## 📖 Detailed Explanation

## Relevance Score (0-100)

**What it measures:** How relevant an article is to knee osteoarthritis prediction models.

**How it's calculated:** Multi-dimensional scoring system that evaluates:
- **Topic relevance** (40%): How well the article matches knee OA prediction research
- **Study design** (30%): Quality of methodology (prospective > retrospective > case-control)
- **Sample size** (15%): Larger studies score higher (≥100 participants = higher score)
- **Outcome relevance** (15%): Focus on TKA outcomes, pain, function, or OA progression

**Interpretation:**
- **≥40:** Relevant enough for model consideration
- **40-50:** Good relevance
- **50-60:** High relevance
- **60+:** Very high relevance

**Example:** An article with score 58 is highly relevant to knee OA prediction models.

---

## PROBAST Risk Assessment

**PROBAST** = **Prediction model Risk Of Bias Assessment Tool**

**Purpose:** Standardized tool to assess risk of bias in prediction model studies. Used to ensure only high-quality evidence is used in our model.

**Overall Risk Levels:**
- **Low Risk:** All four domains are Low Risk
- **Moderate Risk:** Mix of Low and Moderate Risk domains (with justification)
- **High Risk:** Any domain is High Risk (excluded from model)
- **Unclear Risk:** Insufficient information to assess

**Our Criteria for Use:**
- ✅ **0 High Risk** articles used (required)
- ✅ **Moderate Risk** articles used only with justification (e.g., 3 Low + 1 Moderate, or 2 Low + 2 Moderate)
- ✅ All used articles maintain **top 7% PROBAST quality**

---

## PROBAST Domain 1: Participants

**What it assesses:** Risk of bias related to study participants.

**Low Risk:**
- Participants clearly defined and appropriate for the research question
- Inclusion/exclusion criteria well-specified
- Representative sample of the target population

**Moderate Risk:**
- Some uncertainty about participant selection
- Minor issues with representativeness or criteria

**High Risk:**
- Participants not clearly defined
- Selection bias (e.g., convenience sampling without justification)
- Not representative of target population

**Example:** A study using only patients from a single hospital might be Moderate Risk if the hospital is representative, but High Risk if it's a specialized center not representative of general population.

---

## PROBAST Domain 2: Predictors

**What it assesses:** Risk of bias related to predictor variables (e.g., age, BMI, KL grade).

**Low Risk:**
- Predictors clearly defined and measured consistently
- Predictors measured before outcome (temporal relationship)
- No predictor selection based on outcome

**Moderate Risk:**
- Some uncertainty about predictor definition or measurement
- Minor issues with timing or selection

**High Risk:**
- Predictors not clearly defined
- Predictors measured after outcome (reverse causality)
- Predictor selection based on outcome (data dredging)

**Example:** A study using BMI measured at the time of surgery (Low Risk) vs. BMI measured after outcome is known (High Risk).

---

## PROBAST Domain 3: Outcome

**What it assesses:** Risk of bias related to the outcome being predicted (e.g., TKA, pain, function).

**Low Risk:**
- Outcome clearly defined and appropriate
- Outcome measured objectively or with validated tools
- Outcome assessors blinded to predictors (when applicable)

**Moderate Risk:**
- Some uncertainty about outcome definition or measurement
- Minor issues with objectivity or blinding

**High Risk:**
- Outcome not clearly defined
- Subjective outcome without validation
- Outcome assessors not blinded when they should be

**Example:** A study using validated WOMAC scores (Low Risk) vs. unvalidated patient-reported outcomes (Moderate/High Risk).

---

## PROBAST Domain 4: Analysis

**What it assesses:** Risk of bias in statistical analysis and model development.

**Low Risk:**
- Appropriate statistical methods
- Adequate sample size (EPV ≥15)
- No overfitting (proper validation)
- Missing data handled appropriately

**Moderate Risk:**
- Some uncertainty about statistical methods
- Minor issues with sample size or validation

**High Risk:**
- Inappropriate statistical methods
- Small sample size (EPV <15)
- Overfitting (no validation)
- Missing data not handled appropriately

**Example:** A study with 171 events and 11 predictors (EPV = 15.55, Low Risk) vs. a study with 50 events and 10 predictors (EPV = 5, High Risk).

---

## Summary for Team Documentation

**Relevance Score (0-100):** Measures how relevant an article is to knee OA prediction. Scores ≥40 are considered for model use.

**PROBAST Risk:** Overall assessment of study quality. We use only Low Risk or Moderate Risk (with justification) articles. High Risk articles are excluded.

**PROBAST Domains:**
1. **Participants:** Quality of study population selection
2. **Predictors:** Quality of predictor variable definition and measurement
3. **Outcome:** Quality of outcome definition and measurement
4. **Analysis:** Quality of statistical methods and model development

**Our Standards:**
- ✅ All used articles have relevance score ≥40
- ✅ 0 High Risk articles used
- ✅ Moderate Risk articles used only with justification
- ✅ Top 7% PROBAST quality maintained
