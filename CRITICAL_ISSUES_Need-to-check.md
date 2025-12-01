# 🚨 CRITICAL ISSUES - Need-to-check.md

## ❌ **MUST FIX BEFORE CLIENT DELIVERY**

### 1. **KCNQ3 × TBK1 - DOES NOT EXIST**

**Mentioned in:**

- Line 38: "KCNQ3 × TBK1 (Δ = −0.218, p = 0.045, n = 5 mutants)"
- Line 46: "Notably, the KCNQ3 × TBK1 interaction in glioma"
- Line 53: "presence of actionable synthetic-lethality (KCNQ3 × TBK1)"
- Line 63: "KCNQ3 × TBK1 (glioma subset)"
- Line 96: "KCNQ3-mutant subset, TBK1 target"

**Reality:**

- ❌ **KCNQ3 mutation NOT in synthetic lethality dataset**
- ❌ **This interaction does not exist**
- ❌ **Cannot be verified or reproduced**

**Impact:** CRITICAL - Core finding that doesn't exist

**Fix:**

- Remove all KCNQ3 × TBK1 references
- Replace with verified glioma-related TBK1 hit:
  - **ARMH3 × TBK1** (mean_diff = -0.0493, p < 0.001, n = 3, glioma cell line: NMCG1)
  - Or use **SMAD2 × TBK1** (colorectal, but strong effect)

---

### 2. **GRM3 and AHNAK2 - ALSO NOT FOUND**

**Mentioned in:**

- Line 46: "TBK1 also interacts synthetically with SMAD2, GRM3, and AHNAK2 mutations"

**Reality:**

- ❌ **GRM3 × TBK1: NOT FOUND**
- ❌ **AHNAK2 × TBK1: NOT FOUND**
- ✅ **SMAD2 × TBK1: VERIFIED** (mean_diff = -0.2843, p = 0.092)

**Fix:**

- Remove GRM3 and AHNAK2 from this list
- Keep only verified interactions: SMAD2 × TBK1

---

### 3. **IC50 Count - MAJOR DISCREPANCY**

**Claim:** "160 IC50-tested cell lines"

**Reality:** Found 49 unique cell lines in available data

**Possible Explanations:**

1. Additional IC50 data sources not included
2. Different definition (e.g., includes replicates, multiple compounds)
3. Historical data that's been updated

**Fix:**

- Verify all IC50 sources are included
- If 160 is correct: identify missing sources
- If 49 is correct: update report to "~50 IC50-tested cell lines"
- Clarify definition: unique cell lines vs total tests

---

### 4. **Validated Cell Line Counts - UNDERSTATED**

**Claims:**

- AML: "3 validated lines" → **Actual: 5 validated**
- Glioma: "2 validated lines" → **Actual: 5 validated**

**Impact:** Actually strengthens validation claims (more is better!)

**Fix:**

- Update to reflect actual counts:
  - AML: "5 validated cell lines" (not 3)
  - Glioma: "5 validated cell lines" (not 2)

---

### 5. **Glioma Score - MINOR ROUNDING**

**Claim:** "score = 0.468"

**Actual:** 0.463

**Fix:** Update to 0.463 or use "~0.46"

---

## ⚠️ **RECOMMENDED FIXES**

### 6. **Missing Limitations Section**

- Weak dependency signals (mean ~ -0.09)
- Limited experimental validation overlap (~12-14%)
- Context-specific rather than pan-cancer dependencies
- Small sample sizes for some synthetic lethality hits

### 7. **Missing Data Quality Metrics**

- Data completeness percentages
- Missing data handling
- Quality control measures

### 8. **Missing Reproducibility Info**

- Software versions
- Data version/date stamps
- Script references

---

## ✅ **WHAT'S CORRECT**

- ✅ 1,186 DepMap cell lines
- ✅ 660 mutation–target combinations
- ✅ 106 true synthetic lethality hits
- ✅ 165 mutations tested
- ✅ AML rank 1, score 0.491, n=30
- ✅ Glioma rank 2, n=71
- ✅ STK17A AML = -0.062
- ✅ STK17B AML = -0.095
- ✅ NRAS × CLK4, CDC25A × CLK4, OLIG2 × MYLK4, SMAD2 × TBK1, LHCGR × MYLK4 - all verified
- ✅ ~12-14% overlap - verified

---

## 📋 **SUMMARY**

**Overall Accuracy:** ~85%

**Critical Issues:** 1 (KCNQ3 × TBK1)
**Major Issues:** 1 (IC50 count)
**Minor Issues:** 3 (validation counts, glioma score, missing mutations)

**Recommendation:** Fix critical and major issues before client delivery. The report is mostly accurate but contains one critical error (KCNQ3 × TBK1) that must be removed.
