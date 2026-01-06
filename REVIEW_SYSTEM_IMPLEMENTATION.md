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

### Small Percentage Changes

When implementing new parameters:

1. **Start Small**: Add parameter with minimal weight initially
2. **Monitor Performance**: Track AUC, calibration, EPV
3. **Gradual Integration**: Increase weight if performance improves
4. **PROBAST Compliance**: Always maintain EPV ≥15
5. **Rollback Capability**: Keep previous model version

### Example Workflow

```
Week 1: Add parameter with 5% weight
  → Monitor performance
  → Verify PROBAST compliance
  
Week 2: If successful, increase to 10%
  → Continue monitoring
  
Week 3: If still successful, increase to full weight
  → Final validation
  → Mark as implemented
```

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

