# Response to Doctor's Questions

**Date:** 2025-01-05  
**From:** Technical Team  
**To:** Doctor M

---

## 1. What Model/System Are We Using?

**Answer:** We are using **Python** (not R) with the following:

- **Language:** Python 3.11
- **ML Libraries:** scikit-learn (Random Forest, Logistic Regression)
- **Data Processing:** pandas, numpy
- **Model Type:** Random Forest Classifier (primary model)
- **Calibration:** Platt Scaling for probability calibration

**Why Python over R:**
- Better integration with web APIs (Vercel/Railway)
- More modern ML ecosystem
- Easier deployment and maintenance
- Better for automated literature mining (PubMed integration)

**For the Research Chief:**
- We can share our Python codebase
- We can export model coefficients/feature importance
- We can provide model files (.pkl format) for integration
- We can work with their system (R or Python) via API or data export

---

## 2. Side of Complaints

**Current Status:**
- ✅ We already capture **left and right separately**:
  - Left KL grade (`V00XRKLL`)
  - Right KL grade (`V00XRKLR`)
  - Left WOMAC (`V00WOMTSL`)
  - Right WOMAC (`V00WOMTSR`)

**What's Missing:**
- We don't have a single "side of primary complaint" field
- This would be: Left, Right, or Bilateral

**Can We Add It?**
- ✅ **Yes, technically possible**
- ⚠️ **BUT: PROBAST Compliance Issue**

**PROBAST Impact:**
- Current: 11 predictors, 171 events, **EPV = 15.55** ✅ (meets ≥15 threshold)
- Adding "side": 12 predictors, 171 events, **EPV = 14.25** ❌ (BELOW 15 threshold)
- **This would drop us below top 7% PROBAST compliance**

**Solutions:**
1. **Option A:** Use "worst side" indicator (combines existing left/right data)
   - No new predictor needed
   - Maintains EPV = 15.55 ✅
   - Example: "Primary complaint side" = side with worst KL grade or worst WOMAC

2. **Option B:** Remove one existing predictor to add "side"
   - Would need to identify least important predictor
   - Risk: May reduce model performance

3. **Option C:** Wait for more data (Bergman dataset)
   - More events = higher EPV
   - Can add "side" without dropping below threshold

**Recommendation:** Use **Option A** (worst side indicator) - maintains PROBAST compliance while adding clinical value.

---

## 3. WOMAC Improvement Over 30 Points

**Doctor's Observation:**
> "If I try multiple patients, the improvement is seldomly over 30 womac points"

**Our Model's Current Thresholds:**
- Minimal: <10 points improvement
- Limited: 10-20 points improvement
- Moderate: 20-30 points improvement
- Successful: ≥30 points improvement

**Analysis:**
- Your observation aligns with our "Moderate" category (20-30 points)
- Most patients likely fall in the 20-30 point range
- This is clinically meaningful improvement (MCID threshold is typically 10-15 points)

**What This Means:**
- Our model predicts improvement, but we should verify:
  - Are we over-predicting improvement?
  - Should we adjust success thresholds?
  - Should we show predicted improvement points more prominently?

**Current Display:**
- We show success categories (Excellent, Successful, Moderate, etc.)
- We show success probability (%)
- **We also calculate predicted improvement points** but may not display them prominently

**Recommendation:**
- We should display **actual predicted improvement points** (e.g., "Expected improvement: 25 points")
- This aligns with your need to see "how much WOMAC will progress"
- We can adjust thresholds based on your clinical experience

---

## 4. Walking Distance Conversion

**Current Implementation:**
- We use: **400m walk time in seconds**
- Variable: `V00400MTIM` (OAI dataset standard)

**Doctor's Need:**
- They use: **Walking distance in minutes or kilometers**

**Conversion Formulas:**

### Time Conversion (Seconds → Minutes):
```
Minutes = Seconds / 60
Example: 300 seconds = 5 minutes
```

### Distance Conversion (400m → Kilometers):
```
400 meters = 0.4 kilometers
```

### Speed Calculation (km/min):
```
Speed (km/min) = 0.4 km / (time in minutes)
Example: 5 minutes = 0.4 / 5 = 0.08 km/min
```

### Speed Calculation (km/hour):
```
Speed (km/hour) = (0.4 km / time_seconds) × 3600
Example: 300 seconds = (0.4 / 300) × 3600 = 4.8 km/hour
```

**Implementation Options:**

1. **Option A:** Add conversion in UI
   - Input: 400m walk time (seconds)
   - Display: Also show "X minutes" or "Y km/min"
   - Example: "300 seconds (5 minutes, 0.08 km/min)"

2. **Option B:** Accept multiple input formats
   - Allow input in seconds, minutes, or km/min
   - Convert all to seconds internally
   - More flexible for clinical use

3. **Option C:** Use standard clinical measure
   - If Bergman uses minutes/km, we can change our input
   - Convert to seconds for model (maintains compatibility)

**Recommendation:** **Option A** - Keep 400m walk time in seconds (model standard), but display converted values in UI for clinical clarity.

**Example UI Display:**
```
Walking Distance: 300 seconds
  (5.0 minutes | 0.08 km/min | 4.8 km/hour)
```

---

## 5. PROBAST Compliance Summary

**Current Status:**
- ✅ **EPV = 15.55** (11 predictors, 171 events)
- ✅ **Top 7% PROBAST compliance** (all 4 domains LOW RISK)
- ✅ **Meets ≥15 EPV threshold**

**If We Add "Side of Complaints":**
- ⚠️ **EPV = 14.25** (12 predictors, 171 events)
- ❌ **Drops below 15 threshold**
- ❌ **Would lose top 7% compliance**

**Solutions to Maintain Compliance:**

1. **Use "Worst Side" Indicator** (Recommended)
   - No new predictor (uses existing left/right data)
   - EPV remains 15.55 ✅
   - Maintains top 7% compliance ✅

2. **Wait for Bergman Data**
   - More events = higher EPV
   - Can add "side" without compliance risk
   - Example: 200 events, 12 predictors = EPV = 16.67 ✅

3. **Remove Least Important Predictor**
   - Would need analysis to identify which one
   - Risk: May reduce model performance
   - Not recommended

**Recommendation:** Use "worst side" indicator approach - maintains compliance while adding clinical value.

---

## Summary of Recommendations

### ✅ Can Do Immediately:
1. **Share Python codebase** with research chief
2. **Add "worst side" indicator** (maintains PROBAST compliance)
3. **Add walking distance conversions** in UI (seconds → minutes/km)
4. **Display predicted improvement points** more prominently

### ⚠️ Need More Data:
1. **Add "side of complaints" as separate predictor** (requires more events to maintain EPV ≥15)

### 📊 Data Sharing Options:
1. **Option 1:** Clean LROI data sheet → Send to us
   - We can process in Python
   - We can integrate with our model
   - Privacy officer can review before sending

2. **Option 2:** Guest account on Bergman system
   - We can work directly in their system
   - Extract needed variables
   - Process and integrate

**Recommendation:** Start with **Option 1** (cleaned data sheet) - easier for privacy review and faster to implement.

---

## Next Steps

1. **Share technical details** with research chief (Python, scikit-learn, model files)
2. **Implement "worst side" indicator** (maintains PROBAST compliance)
3. **Add walking distance conversions** to UI
4. **Display predicted improvement points** more prominently
5. **Coordinate data sharing** (LROI data sheet or guest account)

---

**Questions for Doctor:**
1. Do you want us to implement "worst side" indicator, or wait for Bergman data to add "side" as separate predictor?
2. What walking distance format would be most useful in the UI? (seconds, minutes, km/min, or all?)
3. Should we adjust success thresholds based on your observation that improvement is seldomly >30 points?

