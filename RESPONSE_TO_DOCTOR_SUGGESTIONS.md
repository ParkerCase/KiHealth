# Response to Doctor's Suggestions - OAI Database Findings

## Summary

**What we found in OAI database regarding your suggestions:**

✅ **Available and feasible:**

- Side of complaints (right/left knee) - ✅ Already in model
- Compartment-specific severity scores (medial/lateral) - ✅ Available via OARSI scores

⚠️ **Available but limited:**

- Walking distance - ⚠️ Available (400m walk time) but lower correlation
- Surgery types - ⚠️ Partial/unicompartmental available (40 events) but insufficient for separate model

❌ **Not available in OAI:**

- Pain at rest (yes/no) - ❌ Not in OAI
- Pain at night (yes/no) - ❌ Not in OAI
- Osteotomy procedures - ❌ Not tracked separately
- Compartment-specific KL grades - ❌ Not available (but OARSI compartment scores are)

---

## Detailed Response to Each Suggestion

### 1. VAS Pain Scores

**Your comment:** "VAS is only noted after surgery and then still its hard to find... During non surgical trajectories, VAS is never asked."

**OAI finding:** ✅ **Agrees with your experience**

- OAI does NOT contain VAS pain scores
- We've already implemented VAS→WOMAC conversion for clinics that do collect VAS
- **Recommendation:** Skip VAS, use WOMAC or simpler alternatives

---

### 2. Pain at Rest (Yes/No) and Pain at Night (Yes/No)

**Your suggestion:** Use binary pain measures instead of VAS

**OAI finding:** ❌ **Not available in OAI**

- Searched all clinical data files
- No binary "pain at rest" or "pain at night" measures found
- OAI uses WOMAC pain subscale (0-20) instead

**Options:**

1. **Collect at Bergman Clinics** - Would need to add to data collection
2. **Use WOMAC pain subscale** - Already validated, simpler than total WOMAC (5 questions vs 24)
3. **Derive from WOMAC** - Could map WOMAC pain questions to approximate "pain at rest/night"

**Recommendation:** Use WOMAC pain subscale (0-20) - simpler than total WOMAC, still validated, and we can collect it prospectively.

---

### 3. Walking Distance (Meters)

**Your suggestion:** Max duration/steps of walking in meters

**OAI finding:** ⚠️ **Available but limited**

- **400m walk time** available (V00400MTIM)
- Completeness: 95.2%
- **Correlation with WOMAC:** r = 0.296 (moderate, not strong)
- Measured as time to complete 400m, not distance

**Options:**

1. **Use 400m walk time** - Available but moderate correlation
2. **Collect walking distance at Bergman** - More direct measure
3. **Skip for now** - Focus on higher-value predictors first

**Recommendation:** Can add 400m walk time if you collect it, but it's not a strong predictor (r=0.296). Would need to assess if it improves model.

---

### 4. Side of Complaints (Right/Left/Both)

**Your suggestion:** Add side of complaints

**OAI finding:** ✅ **Already in model**

- OAI tracks right and left knees separately
- Current model already uses:
  - `womac_r` / `womac_l` (right/left WOMAC)
  - `kl_r` / `kl_l` (right/left KL grade)
- **Status:** ✅ Already implemented

**Note:** Model handles bilateral OA by including both knees as separate predictors.

---

### 5. Surgery Types: Osteotomy, Hemi-Prosthesis, TKR

**Your suggestion:** Track 3 surgery types separately

**OAI finding:** ⚠️ **Partially available**

- ✅ **Total Knee Replacement (TKR):** 492 events, EPV = 49.2 ✅ **Sufficient**
- ⚠️ **Partial/Unicompartmental Replacement:** 40 events, EPV = 4.0 ❌ **Insufficient** (similar to hemi-prosthesis)
- ❌ **Osteotomy:** 0 events ❌ **Not tracked in OAI**

**EPV Analysis:**

- **TKR model:** ✅ Feasible (492 events, EPV = 49.2)
- **Hemi/Partial model:** ❌ Not feasible (40 events, EPV = 4.0, need 150+)
- **Osteotomy model:** ❌ Not feasible (0 events)

**Options:**

1. **Use TKR model only** (current approach) - ✅ Ready to deploy
2. **Collect osteotomy/hemi data at Bergman** - Need 150+ events each for separate models
3. **Combined "any surgery" model** - Would combine all procedures (more events, less specific)

**Recommendation:**

- **Short-term:** Use TKR model (validated, ready)
- **Medium-term:** Collect osteotomy/hemi outcomes at Bergman Clinics
- **Long-term:** Build procedure-specific models as data accumulates

---

### 6. KL Grade Location: Lateral/Medial/Patellofemoral

**Your suggestion:** Add location of KL findings (lateral/medial/patellofemoral) with severity at each location

**OAI finding:** ⚠️ **Partially available - OARSI compartment scores instead of KL**

**What OAI has:**

- ❌ **Compartment-specific KL grades:** Not available
- ✅ **OARSI compartment-specific scores:** Available for medial/lateral TF
  - Joint Space Narrowing (JSN): 99.5% complete
  - Osteophytes: 55.5% complete
  - Subchondral sclerosis: 43.0% complete
  - Other features: 43-55% complete
- ❌ **Patellofemoral compartment:** Not scored separately

**EPV Impact if Adding Compartment Scores:**

- Current: 10 predictors, EPV = 42.5 ✅
- Adding 2 JSN scores (medial + lateral): 12 predictors, EPV = 35.4 ✅ **Still ≥ 15**
- Adding JSN + Osteophytes (4 variables): 14 predictors, EPV = 30.4 ✅ **Still ≥ 15**
- **Can add while maintaining top 7% quality**

**Options:**

1. **Use OARSI JSN scores** (medial/lateral) - ✅ 99.5% complete, maintains top 7%
2. **Add OARSI osteophytes** - ⚠️ 55.5% complete, still maintains top 7%
3. **Collect compartment KL grades at Bergman** - Would need to add to data collection
4. **Use overall KL grade only** (current) - ✅ Validated, sufficient

**Recommendation:**

- ✅ **Add OARSI JSN scores** (medial + lateral) - High completeness (99.5%), maintains top 7%
- ⚠️ **Consider OARSI osteophytes** - Moderate completeness (55.5%), still maintains top 7%
- ❌ **Skip other OARSI features** - Lower completeness (43%)

---

## EPV Feasibility Summary

| Addition                 | Predictors | EPV  | Status    | Recommendation            |
| ------------------------ | ---------- | ---- | --------- | ------------------------- |
| **Current model**        | 10         | 42.5 | ✅ Top 7% | Keep as baseline          |
| **+ 2 JSN scores**       | 12         | 35.4 | ✅ Top 7% | **RECOMMENDED**           |
| **+ JSN + Osteophytes**  | 14         | 30.4 | ✅ Top 7% | **RECOMMENDED**           |
| **+ All OARSI features** | 24         | 17.7 | ✅ Top 7% | Possible but many missing |

**Conclusion:** ✅ **Can add compartment scores while maintaining top 7% quality**

---

## Recommended Model Changes

### ✅ **Immediate (Can implement now):**

1. **Add OARSI JSN scores (medial + lateral)**

   - Variables: `V00XRJSM` (medial), `V00XRJSL` (lateral)
   - Completeness: 99.5%
   - EPV impact: 12 predictors, EPV = 35.4 ✅
   - **Status:** ✅ **FEASIBLE - Maintains top 7%**

2. **Consider adding OARSI osteophytes (medial + lateral)**
   - Variables: `V00XROSTM` (medial), `V00XROSTL` (lateral)
   - Completeness: 55.5%
   - EPV impact: 14 predictors, EPV = 30.4 ✅
   - **Status:** ✅ **FEASIBLE - Maintains top 7%** (but need missing data strategy)

### 📋 **Future (Require data collection at Bergman):**

1. **Pain at rest/night (yes/no)**

   - Not in OAI
   - Would need to add to Bergman data collection
   - Could potentially derive from WOMAC pain subscale

2. **Osteotomy procedures**

   - Not in OAI
   - Would need to track at Bergman
   - Need 150+ events for separate model

3. **Compartment-specific KL grades**
   - Not in OAI
   - OARSI compartment scores are available instead
   - Could collect KL grades at Bergman if preferred

---

## What to Tell the Doctor

### Email Response Points:

1. **VAS:** ✅ Agree - OAI doesn't have VAS either. We've implemented VAS→WOMAC conversion for clinics that do collect it, but understand Bergman doesn't.

2. **Pain at rest/night (yes/no):** ❌ Not in OAI. Options:

   - Use WOMAC pain subscale (0-20, 5 questions) - simpler than total WOMAC
   - Collect binary pain measures at Bergman if preferred

3. **Walking distance:** ⚠️ Available (400m walk time) but correlation is moderate (r=0.296). Can add if you collect it, but not a strong predictor.

4. **Side of complaints:** ✅ Already in model - we track right/left knees separately.

5. **Surgery types:** ⚠️ OAI has TKR (492 events) and partial/unicompartmental (40 events, insufficient). Osteotomy not tracked. Recommendation: Use TKR model now, collect osteotomy/hemi data at Bergman for future models.

6. **KL grade location:** ⚠️ OAI doesn't have compartment-specific KL grades, but **DOES have OARSI compartment scores**:
   - Medial/lateral JSN: 99.5% complete ✅
   - Medial/lateral osteophytes: 55.5% complete
   - **Can add while maintaining top 7% quality** (EPV stays ≥ 15)
   - Patellofemoral not scored separately

**Bottom line:** We can add OARSI compartment scores (JSN + osteophytes) to the model while maintaining top 7% methodological quality. For other suggestions (pain at rest/night, osteotomy, compartment KL grades), we'd need to collect that data at Bergman Clinics.

---

## Implementation Priority

### High Priority (Can do now):

1. ✅ Add OARSI JSN scores (medial + lateral) - 99.5% complete
2. ✅ Side of complaints - Already implemented

### Medium Priority (Consider):

1. ⚠️ Add OARSI osteophytes - 55.5% complete, need missing data strategy
2. ⚠️ Add walking distance - Moderate correlation, if you collect it

### Low Priority (Require data collection):

1. 📋 Pain at rest/night - Not in OAI, would need Bergman data
2. 📋 Osteotomy - Not in OAI, would need Bergman data (150+ events)
3. 📋 Compartment KL grades - Not in OAI, OARSI scores available instead

---

## Files Generated

- `RESPONSE_TO_DOCTOR_SUGGESTIONS.md` - This document
- `XRAY_METAANALYSIS_OARSI_REPORT.md` - Detailed OARSI findings
- `SURGERY_TYPE_FEASIBILITY.md` - Surgery type analysis
