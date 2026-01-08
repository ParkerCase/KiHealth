# ASReview LAB - Simple Start/Stop/Resume Guide

## 🚀 How to START

### Step 1: Navigate to Directory
```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
```

### Step 2: Start ASReview
```bash
asreview lab
```

### Step 3: Browser Opens Automatically
- Browser should open to: `http://127.0.0.1:5000`
- If not, manually go to that URL

### Step 4: Create New Project (First Time Only)
1. Click **"New Project"** button
2. Name it: `Knee OA Literature Review`
3. Click **"Create"**

### Step 5: Upload Your Articles
1. Click **"Add Data"** or **"Import"** button
2. Select **"CSV"** format
3. Click **"Browse"** and select:
   ```
   /Users/parkercase/DOC/pubmed-literature-mining/data/asreview_export.csv
   ```
4. Click **"Upload"**

### Step 6: Configure Fields
- **Title field**: Select `title`
- **Abstract field**: Select `abstract`
- **Identifier field**: Select `pmid`
- Click **"Next"** or **"Continue"**

### Step 7: Start Screening
1. Click **"Start Reviewing"** or **"Begin Screening"**
2. Articles appear one at a time
3. Click **✅ Relevant** or **❌ Irrelevant** for each article
4. **Progress saves automatically after each label**

---

## ⏸️ How to STOP

### Option 1: Just Close Browser Tab
- Simply close the browser tab/window
- **Your progress is automatically saved!**
- No need to click anything special

### Option 2: Exit from ASReview
- Look for **"Exit"**, **"Close Project"**, or **"Back"** button
- Click it to return to project list
- Close browser tab

### Option 3: Stop Terminal Process
- In terminal, press `Ctrl + C`
- This stops the ASReview server
- **Your progress is still saved!**

**Important**: Your progress is saved automatically - you can't lose it!

---

## ▶️ How to RESUME

### Step 1: Start ASReview Again
```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
asreview lab
```

### Step 2: Browser Opens
- Go to: `http://127.0.0.1:5000` (if not automatic)

### Step 3: Open Your Project
1. You'll see your project listed: `Knee OA Literature Review`
2. Click on the project name
3. Click **"Continue Reviewing"** or **"Resume"**

### Step 4: Continue Screening
- You'll see exactly where you left off
- Next article to screen appears
- Continue labeling as before

---

## 📊 Check Your Progress

While screening, ASReview shows:
- **Total articles**: 4,671
- **Screened**: X articles (how many you've labeled)
- **Remaining**: Y articles (how many left)
- **Relevant**: Z articles (how many you marked relevant)

---

## 💡 Quick Reference

### Start Command
```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
asreview lab
```

### Stop
- Just close browser tab (progress auto-saved)

### Resume
- Run `asreview lab` again
- Click your project
- Click "Continue Reviewing"

### Export Results (Anytime)
1. In ASReview, click **"Export"** or **"Download Results"**
2. Choose **"CSV"** format
3. Save file (e.g., `asreview_results.csv`)

---

## 🎯 Example Workflow

**Monday 2pm** - Start:
```bash
asreview lab
```
- Create project, upload CSV
- Screen 200 articles
- Close browser tab
- ✅ Progress saved

**Tuesday 10am** - Resume:
```bash
asreview lab
```
- Open project
- Continue reviewing
- Screen 200 more articles
- Close browser tab
- ✅ Progress saved

**Wednesday 3pm** - Resume:
```bash
asreview lab
```
- Open project
- Continue reviewing
- Screen remaining articles
- Export results
- ✅ Complete!

---

## ⚠️ Troubleshooting

**"Can't find my project"**:
- Check project list in ASReview web interface
- Projects are saved in: `~/.asreview/projects/`

**"Browser doesn't open"**:
- Manually go to: `http://127.0.0.1:5000`

**"Port already in use"**:
- Another ASReview instance might be running
- Check terminal for different port number
- Or stop other instances first

**"Want to start completely fresh"**:
- Create a new project with different name
- Or delete old project first

---

## ✅ Summary

**START**: `asreview lab` → Create project → Upload CSV → Start screening

**STOP**: Just close browser tab (auto-saves)

**RESUME**: `asreview lab` → Open project → Continue reviewing

**That's it!** Simple and automatic. 🎉
