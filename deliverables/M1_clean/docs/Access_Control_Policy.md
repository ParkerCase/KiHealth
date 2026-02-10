# Access Control Policy

**Project:** KiHealth Diabetes Prediction  
**Effective Date:** January 28, 2026  
**Policy Owner:** Parker Case, Stroom AI LLC

---

## Data Storage Location

All project data resides in **specific folders within the TL-KiHealth folder** (`Diabetes-KiHealth/TL-KiHealth/`):

| Folder | Contents |
|--------|----------|
| 2013-14-NHANES | NHANES 2013-2014 cycle |
| 2015-16-NHANES | NHANES 2015-2016 cycle |
| NIHANES | NHANES 2017-2020 and 2021-2023 cycles |
| NHANES-Diabetes | Diabetes Questionnaire (DIQ) files |
| CHNS | China Health and Nutrition Survey 2009 |
| Frankfurt | Pima Indians Diabetes Dataset |
| DiaBD | DiaBD dataset |

---

## Role-Based Access Control (RBAC)

### Defined Roles

**1. Project Lead (Parker Case - Stroom AI)**
- **Access Level:** Full read/write to all data and code
- **Permissions:** 
  - Can modify data, code, and documentation
  - Can add/remove datasets
  - Can export data for analysis
  - Can delete data
- **Authentication:** Password-protected systems, 2FA enabled
- **Justification:** Primary data scientist and contractor

**2. KiHealth Team (Jenna, Clifford, designated staff)**
- **Access Level:** Read-only access to processed data and documentation
- **Permissions:**
  - Can view unified datasets
  - Can download final reports
  - Can access documentation
  - Cannot modify data or code
- **Authentication:** Secure credentials via encrypted channel
- **Justification:** Project stakeholders and data owners

**3. External/Public**
- **Access Level:** None
- **Permissions:** No access to any project data
- **Justification:** Proprietary project

---

## Technical Controls

### Data Storage Security

**Local Development:**
- Password-protected laptop (macOS)
- FileVault full-disk encryption enabled
- Automatic screen lock (5 minutes)
- Regular system updates

**Code Repository:**
- Private GitHub repository
- Access limited to authorized users
- Two-factor authentication required
- Branch protection enabled

**File Sharing:**
- Encrypted file transfer only
- 1Password for credential sharing
- ProtonMail for sensitive communications
- No cloud storage of raw data (local only)

### Access Logging

- Git commit history tracks all code changes
- File modification logs maintained by OS
- Data export events documented in project log
- No automated audit logging (small team, manual tracking sufficient)

---

## Access Request Process

**For KiHealth team members:**
1. Submit request to Parker Case via secure email
2. Specify: which data, purpose, duration
3. Approval within 24 hours
4. Credentials shared via encrypted channel
5. Access documented in access log

**For external researchers:**
- Not applicable (project data is proprietary)
- Public datasets (NHANES, CHNS, Frankfurt, DiaBD) available from original sources

---

## Access Review & Audit

**Frequency:** Monthly access review  
**Responsibility:** Parker Case  
**Process:**
- Review active credentials
- Verify no unauthorized access attempts
- Update access log
- Revoke expired credentials

**Annual Review:**
- Complete security assessment
- Update access controls as needed
- Document any security incidents
- Review and update this policy

---

## Incident Response

**Unauthorized Access Detection:**
1. Immediately revoke compromised credentials
2. Assess scope of potential breach
3. Notify KiHealth within 24 hours
4. Document incident in security log
5. Implement additional controls as needed

See: Incident_Response_Plan.md for full procedures

---

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Next Review:** July 28, 2026
