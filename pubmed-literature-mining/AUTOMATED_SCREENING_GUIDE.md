# Automated Screening - No Manual Review Needed!

## 🎯 The Problem You Identified

You're right - manually reviewing 4,671 articles is not practical, especially as an engineer (not a doctor). 

## ✅ The Solution: Automated Pre-Filtering

**Good news**: We already have relevance scoring! The system automatically scores each article 0-100 based on:
- Clinical relevance
- Study quality  
- Novelty/impact
- Actionability

**You only need to review the HIGH-SCORING articles**, not all 4,671!

---

## 🚀 Automated Workflow (Recommended)

### Step 1: Check Automated Screening Results
```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
python scripts/automated_screening.py
```

This shows:
- How many articles are automatically relevant (score ≥70)
- How many need review (score 40-69)
- How many are automatically irrelevant (score <40)

### Step 2: Export Only High-Scoring Articles
```bash
python scripts/automated_screening.py --export --min-score 70 --max-articles 500
```

This creates: `data/asreview_filtered_export.csv`
- **Only 200-500 articles** (instead of 4,671!)
- **Already pre-filtered** by relevance score
- **Much more manageable** for review

### Step 3: Use Filtered List in ASReview
```bash
asreview lab
```

Then upload `data/asreview_filtered_export.csv` instead of the full file.

---

## 📊 What This Means

### Without Automation:
- ❌ Review 4,671 articles manually
- ❌ Read each abstract
- ❌ Make clinical decisions (you're an engineer!)
- ❌ Takes weeks

### With Automated Pre-Filtering:
- ✅ System automatically scores all 4,671 articles
- ✅ You only review top 200-500 high-scoring articles
- ✅ System already filtered out irrelevant ones
- ✅ Takes hours, not weeks

---

## 🎯 Three Options

### Option 1: Fully Automated (No Manual Review)
```bash
# Use only articles with score ≥70 automatically
python scripts/automated_screening.py --export --min-score 70 --max-articles 1000
```

**Result**: System uses top-scoring articles automatically. No ASReview needed.

### Option 2: Minimal Review (Recommended)
```bash
# Export top 200-500 articles for quick review
python scripts/automated_screening.py --export --min-score 70 --max-articles 500
```

**Result**: Review only 200-500 articles in ASReview (much more manageable!)

### Option 3: Full Review (If You Want)
```bash
# Use full 4,671 articles
# Upload data/asreview_export.csv to ASReview
```

**Result**: Review all articles (not recommended unless you have time)

---

## 💡 Recommended Approach

**For You (Engineer, Not Doctor):**

1. **Run automated screening**:
   ```bash
   python scripts/automated_screening.py
   ```

2. **Export filtered list**:
   ```bash
   python scripts/automated_screening.py --export --min-score 70 --max-articles 500
   ```

3. **Review only the filtered list** (200-500 articles):
   - Much more manageable
   - Already pre-filtered by relevance
   - System did the hard work

4. **Or skip ASReview entirely**:
   - Use articles with score ≥70 automatically
   - System already identified relevant ones
   - No manual review needed!

---

## 🔍 How Relevance Scoring Works

The system automatically scores each article based on:

1. **Clinical Relevance** (0-40 points):
   - Direct prediction terms (TKR, progression)
   - Outcome measures (WOMAC, KOOS)
   - Risk factors

2. **Study Quality** (0-30 points):
   - Study design (cohort, systematic review)
   - Sample size
   - Follow-up duration

3. **Novelty/Impact** (0-15 points):
   - Recent publications
   - High-impact journals
   - Novel findings

4. **Actionability** (0-15 points):
   - Clinical applicability
   - Practical insights

**Total Score: 0-100**

- **≥70**: Highly relevant (use automatically or quick review)
- **60-69**: Moderately relevant (review if time)
- **<60**: Less relevant (can skip)

---

## ✅ What You Should Do

**Recommended Workflow:**

```bash
# 1. Check what the system found
python scripts/automated_screening.py

# 2. Export top articles (if you want to review)
python scripts/automated_screening.py --export --min-score 70 --max-articles 500

# 3. Use filtered list in ASReview (optional)
asreview lab
# Upload: data/asreview_filtered_export.csv
```

**OR skip ASReview entirely:**
- System already identified relevant articles
- Use articles with score ≥70 automatically
- No manual review needed!

---

## 🎯 Bottom Line

**You DON'T have to review 4,671 articles!**

The system:
1. ✅ Automatically scores all articles
2. ✅ Identifies relevant ones (score ≥70)
3. ✅ Filters out irrelevant ones
4. ✅ You only review top 200-500 (or skip review entirely!)

**Much smarter approach!** 🚀
