# ASReview LAB - Save and Resume Guide

## ✅ Yes! ASReview Saves Your Progress Automatically

**Great news**: ASReview **automatically saves** your progress as you screen articles. You can stop and resume anytime!

## How It Works

### Automatic Saving
- ASReview saves your project **after every article** you label
- Your progress is stored in the ASReview project file
- **No manual save needed** - it's automatic!

### Resume Anytime
1. **Stop screening** - Just close the browser/tab
2. **Come back later** - Run `asreview lab` again
3. **Open your project** - Click on your project name
4. **Continue screening** - Pick up exactly where you left off

## Step-by-Step: Save and Resume

### Starting a Session
```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
asreview lab
```

1. Open your project (or create new one)
2. Start screening articles
3. Label articles as Relevant/Irrelevant
4. **Progress saves automatically** after each label

### Stopping Mid-Session
- **Just close the browser tab** - That's it!
- Or click "Exit" / "Close Project"
- **Your progress is saved automatically**

### Resuming Later
```bash
asreview lab
```

1. Open ASReview web interface
2. You'll see your project listed
3. Click on your project name
4. Click "Continue Reviewing" or "Resume"
5. **You'll see exactly where you left off**

## Project Storage

ASReview stores your project in:
```
~/.asreview/projects/
```

Or in your project directory if you specified one.

## What Gets Saved

- ✅ All articles you've labeled (Relevant/Irrelevant)
- ✅ Your screening progress (which articles you've seen)
- ✅ AI model state (learned from your decisions)
- ✅ Project settings and configuration

## Working in Chunks

### Recommended Approach

**Session 1** (1 hour):
- Screen 100-200 articles
- Stop and close browser
- Progress saved automatically

**Session 2** (1 hour, next day):
- Open ASReview
- Resume your project
- Continue from where you left off
- Screen another 100-200 articles

**Session 3** (1 hour):
- Resume again
- Continue screening
- Complete remaining articles

### Benefits of Chunking

- ✅ **No pressure** - Work at your own pace
- ✅ **No data loss** - Everything saved automatically
- ✅ **AI improves** - Model gets better with each session
- ✅ **Flexible** - Screen 50 articles or 500, your choice

## Progress Tracking

ASReview shows you:
- **Total articles**: 4,671
- **Screened**: X articles
- **Remaining**: Y articles
- **Relevant found**: Z articles

You can see your progress at any time!

## Export Anytime

You can export your results **at any point**:
- After 100 articles
- After 500 articles
- After completing all

The export includes:
- All articles you've screened
- Your labels (Relevant/Irrelevant)
- Progress information

## Tips for Chunking

1. **Set a goal per session**: "I'll screen 200 articles today"
2. **Stop when tired**: Don't force it - quality over quantity
3. **Resume fresh**: Better decisions when you're alert
4. **Check progress**: See how many you've done
5. **Export periodically**: Backup your results

## Example Workflow

**Day 1** (2 hours):
- Start project
- Screen 300 articles
- Close browser
- ✅ Progress saved

**Day 2** (1 hour):
- Open ASReview
- Resume project
- Screen 200 more articles
- Close browser
- ✅ Progress saved

**Day 3** (1 hour):
- Resume project
- Screen final articles
- Export results
- ✅ Complete!

## Troubleshooting

**"I can't find my project"**:
- Check: `~/.asreview/projects/`
- Or look in ASReview web interface project list

**"Progress seems lost"**:
- ASReview saves after each label
- Check project file modification date
- Should update after each article

**"Want to start fresh"**:
- Create a new project
- Or delete old project and start over

## Summary

✅ **Yes, ASReview works in chunks!**
- Saves automatically after each article
- Resume anytime
- No data loss
- Work at your own pace
- Screen 50 or 500 articles per session

**You're in complete control** - stop and resume whenever you need!
