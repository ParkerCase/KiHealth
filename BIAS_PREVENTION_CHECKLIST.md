# Bias Prevention Checklist - Track Your Progress

## Phase 1: Data Preparation ✓

- [x] Downloaded correct OAI data (ASCII format)
- [x] Explored all datasets
- [x] Confirmed data availability (>90% coverage for key variables)
- [ ] Defined outcome variable clearly
- [ ] Calculated event rate
- [ ] Selected predictor variables
- [ ] Merged datasets (no duplicates)
- [ ] Calculated EPV ratio (≥15 required)
- [ ] Analyzed missing data patterns
- [ ] Created data dictionary

**CHECKPOINT 1: After completing these, paste to Claude:**
"Data preparation complete. EPV ratio: [X]. Missing data: [Y%] for WOMAC, [Z%] for KL grade. Ready for review."

---

## Phase 2: Preprocessing ⬜

- [ ] Handled missing data (imputation, NOT deletion)
- [ ] Documented imputation method
- [ ] Validated imputation (distributions check)
- [ ] Scaled continuous variables (StandardScaler)
- [ ] Encoded categorical variables (one-hot or ordinal)
- [ ] Created train/test split (80/20, stratified)
- [ ] Verified split quality (outcome balance)
- [ ] No data leakage (test set isolated)
- [ ] Saved preprocessing pipeline

**CHECKPOINT 2: After completing these, paste to Claude:**
"Preprocessing complete. Train/test split: [N_train]/[N_test]. Outcome prevalence: [X%] train, [Y%] test. Imputation method: [method]. Ready for review."

---

## Phase 3: Model Development ⬜

- [ ] Trained baseline logistic regression
- [ ] Performed 5-fold stratified cross-validation
- [ ] Documented hyperparameters
- [ ] Limited max_depth to prevent overfitting
- [ ] Set min_samples_split/leaf to prevent overfitting
- [ ] Trained Random Forest with GridSearchCV
- [ ] Trained XGBoost with GridSearchCV
- [ ] Saved all models
- [ ] Cross-validation SD < 0.05 (stable performance)

**CHECKPOINT 3: After completing these, paste to Claude:**
"Model training complete. RF CV AUC: [mean ± SD]. XGBoost CV AUC: [mean ± SD]. Hyperparameters: [list]. Ready for review."

---

## Phase 4: Model Evaluation ⬜

- [ ] Calculated AUC on test set (>0.75 target)
- [ ] Created ROC curve
- [ ] Calculated Brier score (<0.20 target)
- [ ] Created calibration plot
- [ ] Performed Hosmer-Lemeshow test
- [ ] Calculated sensitivity, specificity, PPV, NPV
- [ ] Generated confusion matrix
- [ ] Feature importance analysis
- [ ] SHAP values (optional but good)
- [ ] Clinical interpretation of features

**CHECKPOINT 4: After completing these, paste to Claude:**
"Evaluation complete. Test AUC: [X]. Brier score: [Y]. Calibration: [good/poor]. Top 3 features: [list]. Ready for review."

---

## Phase 5: PROBAST Compliance ⬜

- [ ] Documented all inclusion/exclusion criteria
- [ ] Documented all data sources
- [ ] Documented missing data handling
- [ ] Documented all predictors (how measured)
- [ ] Documented outcome definition
- [ ] Documented statistical analysis plan
- [ ] Completed PROBAST checklist (all 20 questions)
- [ ] Risk of bias assessment (aim: LOW)
- [ ] Methods section written (publication-ready)

**CHECKPOINT 5: After completing these, paste to Claude:**
"PROBAST compliance check complete. Attach: PROBAST checklist, methods section. Ready for final review."

---

## Phase 6: External Validation Plan ⬜

- [ ] Documented validation strategy
- [ ] Identified validation cohort (Bergman Clinics or LROI)
- [ ] Prepared model for deployment
- [ ] Created clinical interface prototype
- [ ] Tested interface with example patients
- [ ] Prepared presentation for Dr. Moen

**FINAL CHECKPOINT: Paste to Claude:**
"Model complete. Final performance: AUC=[X], Brier=[Y], EPV=[Z]. PROBAST risk: [LOW/UNCLEAR/HIGH]. Ready for Dr. Moen review."

---

## BIAS RED FLAGS (Stop immediately if you see these)

🚩 **EPV ratio < 10** → STOP. Reduce predictors or use 4-year outcome
🚩 **Missing data >30% in key variable** → STOP. Exclude that variable
🚩 **Test AUC < 0.65** → STOP. Model not useful, rethink approach
🚩 **Train AUC 0.95, Test AUC 0.70** → STOP. Severe overfitting
🚩 **Calibration plot way off diagonal** → STOP. Model not calibrated
🚩 **Cross-val SD > 0.10** → STOP. Unstable model
🚩 **Using test set for any decisions** → STOP. Data leakage

If you hit ANY red flag, paste to Claude immediately with details.
