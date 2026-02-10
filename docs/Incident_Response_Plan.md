# Data Breach Incident Response Plan

**Project:** KiHealth Diabetes Prediction  
**Effective Date:** January 28, 2026  
**Plan Owner:** Parker Case, Stroom AI LLC

---

## Data Storage Location

All project data resides in **specific folders within the TL-KiHealth folder** (`Diabetes-KiHealth/TL-KiHealth/`): 2013-14-NHANES, 2015-16-NHANES, NIHANES, NHANES-Diabetes, CHNS, Frankfurt, DiaBD. In the event of a breach, assess which of these folders or files were affected.

---

## Breach Definition

A data breach is defined as any of the following:

- Unauthorized access to project data or systems
- Accidental public exposure of data files
- Loss or theft of devices containing project data
- Malware or ransomware affecting data systems
- Improper data sharing with unauthorized parties
- Compromise of authentication credentials

---

## Response Protocol

### Phase 1: Immediate Response (Within 1 Hour)

**1. Contain the Breach**
- Revoke compromised credentials immediately
- Disconnect affected systems from network (if malware suspected)
- Secure all data copies (backup, move to secure location)
- Stop any ongoing data transfers

**2. Document the Incident**
- Timestamp of discovery
- Nature of breach (access, exposure, theft, malware)
- Scope of affected data (which datasets, how many records)
- How breach was discovered
- Initial assessment of cause

**3. Notify Project Lead**
- If discovered by team member, notify Parker Case immediately
- Contact via: parker@stroomai.com and [phone]

---

### Phase 2: Assessment & Notification (Within 24 Hours)

**1. Assess Scope & Impact**
- Determine number of records affected
- Identify types of data exposed (clinical, demographic, PHI)
- Evaluate duration of exposure
- Assess potential for harm or re-identification

**2. Notify KiHealth**
- Email: jenna@kihealth.com, clifford@kihealth.com
- Phone call for severe incidents
- Provide initial assessment:
  - What happened
  - What data was affected
  - Immediate actions taken
  - Estimated timeline for resolution

**3. Begin Remediation**
- Fix vulnerability that caused breach
- Recover or secure exposed data
- Change all authentication credentials
- Implement additional security controls

---

### Phase 3: Regulatory Notification (Within 72 Hours)

**Determine Notification Requirements:**

**If breach involves PHI and affects 500+ individuals:**
- Report to HHS Office for Civil Rights
- Submit via HHS breach portal: https://ocrportal.hhs.gov/ocr/breach/
- Notify affected individuals (if identifiable)
- Notify prominent media outlets (if required)

**If breach involves PHI and affects <500 individuals:**
- Document in breach log
- Include in annual report to HHS (if required)
- Notify individuals if re-identification risk exists

**If breach involves only de-identified data:**
- No regulatory notification required
- Internal documentation only
- Notify KiHealth per contract

**4. Written Report to KiHealth**
- Complete incident timeline
- Root cause analysis
- Data affected (specific datasets, variables)
- Remediation steps completed
- Preventive measures implemented
- Estimated risk to project

---

### Phase 4: Prevention & Review (Within 30 Days)

**1. Post-Incident Review**
- Conduct full security assessment
- Identify systemic vulnerabilities
- Review and update security controls

**2. Update Security Procedures**
- Modify access controls as needed
- Enhance monitoring/logging
- Update backup procedures
- Improve authentication requirements

**3. Team Training** (if applicable)
- Security awareness training
- Incident response drill
- Updated procedures documentation

**4. Policy Updates**
- Revise incident response plan
- Update access control policy
- Document lessons learned

---

## Contact Information

**Project Lead:**
- Name: Parker Case
- Email: parker@stroomai.com
- Phone: [contact number]

**KiHealth Contacts:**
- Jenna: jenna@kihealth.com
- Clifford: clifford@kihealth.com

**Regulatory:**
- HHS OCR Breach Portal: https://ocrportal.hhs.gov/ocr/breach/wizard_breach.jsf
- HHS OCR Phone: 1-800-368-1019

**System Security:**
- macOS Security: https://support.apple.com/mac/security
- GitHub Security: security@github.com

---

## Incident Log Template

| Date | Incident Type | Scope | Response Actions | Resolution Date | Lessons Learned |
|------|---------------|-------|------------------|-----------------|-----------------|
|      |               |       |                  |                 |                 |

---

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Next Review:** July 28, 2026
