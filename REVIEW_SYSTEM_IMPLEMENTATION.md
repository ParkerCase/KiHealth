# Review System Implementation Guide

## Overview

The review system provides a **separate, unattached interface** for reviewing and approving literature findings before they impact the model. This ensures:

1. ✅ All findings go through manual review
2. ✅ Items can be marked as "proves current system"
3. ✅ New parameters can be approved incrementally
4. ✅ PROBAST compliance maintained (top 7%)
5. ✅ No automatic model changes

---

## How It Works

### 1. Automated Literature Mining (Background)

**Weekly Workflow:**
- Runs every Monday at 2 AM EST
- Searches PubMed for new OA/TKR studies
- Extracts predictive factors
- Compares against current model parameters

**What Gets Added to Review Queue:**
- **New Parameters**: Factors not in current model (5+ articles, statistical evidence)
- **Supporting Evidence**: High-relevance articles that support current parameters

### 2. Review Dashboard (Manual)

**Location:** `/review-dashboard.html` (separate from main validator)

**Features:**
- View all pending findings
- Filter by status, type, search
- Statistics dashboard
- One-click actions:
  - ✓ Proves Current System
  - 🆕 New Parameter
  - ✓ Approve for Implementation
  - ✗ Reject
  - ✓ Mark as Implemented

### 3. Approval Workflow

```
Pending Review
    ↓
[Decision: Proves Current OR New Parameter OR Reject]
    ↓
If New Parameter:
    ↓
[Approve for Implementation]
    ↓
[Manual Implementation with PROBAST Checks]
    ↓
[Mark as Implemented]
```

---

## Review Statuses

| Status | Description | Action Required |
|--------|-------------|-----------------|
| **Pending** | New finding, awaiting review | Review and categorize |
| **Proves Current** | Supports existing model | Archive, no action needed |
| **New Parameter** | Potential new predictor | Evaluate for implementation |
| **Approved** | Approved for implementation | Ready for model integration |
| **Rejected** | Not suitable for model | Archive with reason |
| **Implemented** | Successfully added to model | Tracked for monitoring |

---

## Implementation Process

### For "Proves Current System"

1. Click "✓ Proves Current System"
2. System marks as `proves_current`
3. No model changes required
4. Evidence archived for documentation

### For "New Parameter"

1. Click "🆕 New Parameter"
2. Review evidence (articles, statistics)
3. Complete PROBAST checklist:
   - [ ] Data availability in OAI/clinical practice
   - [ ] EPV ≥15 (events per variable)
   - [ ] Statistical significance
   - [ ] Clinical accessibility
   - [ ] No multicollinearity
4. If approved: Click "✓ Approve for Implementation"
5. Manual implementation:
   - Extract variable from OAI
   - Retrain model with new parameter
   - Verify EPV compliance
   - Test performance
   - Validate externally
6. Deploy incrementally (small percentage change)
7. Mark as "✓ Implemented"

---

## Incremental Updates

### Incremental Implementation Strategy

When implementing new parameters, the weight depends on the parameter type and evidence strength:

**Parameter Categories:**
- **High Confidence** (strong evidence, multiple studies, validated): Start at 0.5-1%
- **Medium Confidence** (moderate evidence, some validation): Start at 0.2-0.5%
- **Low Confidence** (preliminary evidence, needs validation): Start at 0.1-0.2%
- **Very Low Confidence** (exploratory, minimal evidence): Start at 0.05-0.1%

**Note:** The exact starting weight depends on:
- Number of supporting studies
- Quality of evidence (RCT vs. observational)
- Sample sizes in supporting studies
- Consistency across studies
- Clinical relevance and accessibility

**Incremental Steps:**
1. **Initial Implementation**: Add parameter with minimal weight (0.1-2% based on confidence)
2. **Monitor Performance**: Track AUC, calibration, EPV for 2-4 weeks
3. **Gradual Integration**: If successful, increase by 0.5-1% increments
4. **PROBAST Compliance**: Always maintain EPV ≥15
5. **Rollback Capability**: Keep previous model version

### Example Workflow (High Confidence Parameter)

```
Week 1-2: Add parameter with 0.5% weight
  → Monitor performance metrics (AUC, calibration, EPV)
  → Verify PROBAST compliance (EPV ≥15)
  → Check for adverse effects on other metrics
  
Week 3-4: If successful, increase to 0.8%
  → Continue monitoring
  → Validate calibration
  
Week 5-6: If still successful, increase to 1.2%
  → Extended validation
  → External validation if available
  
Week 7-8: If successful, increase to 1.5%
  → Final validation period
  
Week 9+: Gradually increase to target weight (if applicable, max 2-3%)
  → Final validation
  → Mark as implemented
```

### Example Workflow (Medium Confidence Parameter)

```
Week 1-3: Add parameter with 0.3% weight
  → Extended monitoring period
  → Verify no negative impact
  → Check EPV compliance
  
Week 4-6: If successful, increase to 0.5%
  → Continue careful monitoring
  
Week 7-9: If successful, increase to 0.7%
  → Extended validation
  
Week 10+: Very gradual increases (0.1-0.2% per increment)
  → Conservative approach
  → Mark as implemented only after extended validation
```

### Example Workflow (Low Confidence Parameter)

```
Week 1-4: Add parameter with 0.1% weight
  → Extended monitoring period (4 weeks minimum)
  → Verify no negative impact
  → Multiple validation checks
  
Week 5-8: If successful, increase to 0.2%
  → Continue careful monitoring
  
Week 9-12: If successful, increase to 0.3%
  → Extended validation period
  
Week 13+: Very gradual increases (0.05-0.1% per increment)
  → Very conservative approach
  → Mark as implemented only after 3+ months of validation
```

### Incremental Step Guidelines

- **Each increment**: 0.05-0.2% depending on confidence level
- **Monitoring period**: Minimum 2 weeks per increment
- **Maximum total weight**: Typically 2-3% for a single new parameter
- **Rollback threshold**: If any metric degrades >1%, rollback immediately

---

## API Endpoints

### GET `/api/review-data`
Returns review queue data:
```json
{
  "summary": {
    "total": 25,
    "pending": 8,
    "new_parameter": 3,
    "proves_current": 12,
    "approved": 2,
    "implemented": 0
  },
  "pending": [...],
  "new_parameters": [...],
  "approved": [...],
  "recent": [...]
}
```

### POST `/api/review-update`
Update review status:
```json
{
  "id": "new_parameter_20250105_123456_12345678",
  "status": "approved",
  "notes": "Approved after PROBAST verification",
  "approved_by": "doctor_name"
}
```

---

## File Structure

```
pubmed-literature-mining/
├── scripts/
│   ├── review_manager.py          # Review workflow management
│   ├── analyze_and_notify.py      # Adds findings to review queue
│   └── ...
├── data/
│   └── review_queue.json          # Review queue storage
└── ...

DOC_Validator_Vercel/
├── public/
│   └── review-dashboard.html      # Review dashboard UI
├── api/
│   ├── review-data.py             # GET review data
│   └── review-update.py           # POST update status
└── ...
```

---

## Safety Guarantees

### ✅ What Happens Automatically:
- Literature mining (weekly)
- Finding extraction
- Adding to review queue
- Creating GitHub issues

### ❌ What Requires Manual Approval:
- Marking as "proves current"
- Marking as "new parameter"
- Approving for implementation
- Model retraining
- Deployment

### 🔒 PROBAST Compliance:
- EPV ≥15 always maintained
- All changes validated
- External validation required
- Top 7% quality maintained

---

## Next Steps

1. **Deploy Review Dashboard**
   - Add to Vercel deployment
   - Set up API endpoints
   - Test with sample data

2. **First Review Cycle**
   - Wait for next weekly run
   - Review findings in dashboard
   - Test approval workflow

3. **Incremental Implementation**
   - Select first parameter to implement
   - Follow PROBAST checklist
   - Implement with small weight
   - Monitor and adjust

---

## Questions?

- **Review Dashboard**: `/review-dashboard.html`
- **Review Queue**: `pubmed-literature-mining/data/review_queue.json`
- **API Docs**: See endpoint files above
- **Safety Mechanisms**: `AUTOMATED_LEARNING_SAFETY_MECHANISMS.md`

---

**Status:** ✅ Implementation Complete  
**Last Updated:** 2025-01-XX

