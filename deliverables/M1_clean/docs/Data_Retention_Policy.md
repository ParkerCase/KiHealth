# Data Retention and Deletion Policy

**Project:** KiHealth Diabetes Prediction  
**Effective Date:** January 28, 2026  
**Policy Owner:** Parker Case, Stroom AI LLC

---

## Data Storage Location

All project data resides in **specific folders within the TL-KiHealth folder** (`Diabetes-KiHealth/TL-KiHealth/`): 2013-14-NHANES, 2015-16-NHANES, NIHANES, NHANES-Diabetes, CHNS, Frankfurt, DiaBD. Retention and deletion apply to data in these folders.

---

## Retention Periods

### During Active Contract

**Raw Data:**
- Retention: Throughout project duration
- Location: Local encrypted storage
- Backup: Weekly backups maintained

**Processed Data:**
- Retention: Throughout project duration
- Location: Local + outputs directory
- Backup: Version controlled via Git

**Models:**
- Retention: Throughout project duration + 1 year post-deployment
- Location: models/ directory
- Backup: Tagged releases in Git

**Code:**
- Retention: Throughout project duration + indefinitely (portfolio)
- Location: Private GitHub repository
- Backup: GitHub cloud backup

**Documentation:**
- Retention: Throughout project duration + 7 years (legal requirement)
- Location: docs/ directory + deliverables package
- Backup: Multiple copies (local, GitHub, client delivery)

---

### Post-Contract Retention

**Public Datasets (NHANES, CHNS, Frankfurt, DiaBD):**
- **Retention:** Indefinite
- **Justification:** Publicly available data, permitted by data use agreements
- **Use:** Portfolio, research, future projects
- **Location:** Archived separately from proprietary data

**KiHealth Proprietary Data:**
- **Retention:** 7 years post-contract (HIPAA/legal requirement)
- **Then:** Secure deletion per protocol below
- **Exceptions:** Aggregated de-identified results may be retained for portfolio

**Trained Models:**
- **Retention:** Per contract terms (KiHealth ownership)
- **Transfer:** Full model transfer to KiHealth at project completion
- **Deletion:** Stroom AI copies deleted upon transfer confirmation

**Analysis Code:**
- **Retention:** Indefinite (with proprietary data removed)
- **Justification:** Methodology demonstration for portfolio
- **Privacy:** All KiHealth-specific references removed

---

## Deletion Protocol

### Secure Deletion Standards

**Digital Files:**
- **Method:** 7-pass DoD 5220.22-M secure wipe
- **Tools:** macOS secure delete, shred command
- **Verification:** File recovery test (spot check)

**Cloud Storage** (if used):
- **Method:** Permanent deletion + empty trash
- **Verification:** Deletion confirmation email
- **Backups:** All backup copies deleted

**Physical Media** (if applicable):
- **Method:** Physical destruction or degaussing
- **Documentation:** Certificate of destruction

---

## Deletion Timeline

**Upon Contract Termination:**

| Day | Action |
|-----|--------|
| 1 | Stop all data processing, secure all data |
| 7 | Deliver final models and deliverables to KiHealth |
| 14 | Delete KiHealth proprietary data (if requested) |
| 30 | Provide written attestation of deletion to KiHealth |

**Upon KiHealth Deletion Request:**
- Immediate (within 48 hours)
- Written confirmation of deletion provided
- Audit log of deletion maintained

---

## Data Retention by Type

| Data Type | During Project | Post-Project | Deletion Method |
|-----------|----------------|--------------|-----------------|
| Public datasets (NHANES, CHNS) | ✅ Retained | ✅ Retained indefinitely | N/A (public data) |
| KiHealth methylation data | ✅ Retained | ⏱️ 7 years, then deleted | 7-pass secure wipe |
| Trained models | ✅ Retained | ➡️ Transferred to KiHealth | Deleted after transfer |
| Code (ETL, models) | ✅ Retained | ✅ Retained (sanitized) | Proprietary refs removed |
| Documentation | ✅ Retained | ✅ 7 years | Standard deletion |
| Analysis results | ✅ Retained | ✅ Aggregated only | PHI removed |

---

## Backup Strategy

### Development Phase Backups

**Daily Backups:**
- Method: macOS Time Machine
- Location: Local encrypted external drive
- Retention: 30 days rolling

**Weekly Backups:**
- Method: Git push to GitHub
- Location: Private repository
- Retention: Indefinite (code only, no data)

**Monthly Backups:**
- Method: Full project archive
- Location: Encrypted external drive
- Retention: Until project completion + 30 days

### Backup Security

**Encryption:**
- All backups encrypted at rest
- FileVault (macOS), AES-256 encryption
- Encrypted external drives

**Physical Security:**
- External drives stored in locked location
- No cloud backups of proprietary data
- Backup drives deleted after project completion

---

## Exceptions

**Portfolio Use:**
- De-identified aggregated results: Retained
- Code samples (sanitized): Retained
- Methodology documentation: Retained
- Client-specific details: Removed

**Legal Requirements:**
- Tax/contract records: 7 years (IRS requirement)
- Work product documentation: 7 years (legal standard)

---

## Annual Review

**Frequency:** Annually on January 1  
**Process:**
1. Review all retained data
2. Delete data past retention period
3. Update retention schedule
4. Document deletions in log

---

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Next Review:** January 28, 2027
