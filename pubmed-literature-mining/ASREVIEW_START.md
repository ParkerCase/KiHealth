# How to Start ASReview LAB

## Correct Command

For ASReview version 2.2, use:

```bash
asreview lab
```

**NOT** `asreview web` (that's for older versions)

## Quick Start

```bash
cd /Users/parkercase/DOC/pubmed-literature-mining
asreview lab
```

This will:
1. Open your web browser automatically
2. Show the ASReview LAB interface
3. Usually at: `http://127.0.0.1:5000`

## If That Doesn't Work

Try:
```bash
python -m asreview lab
```

Or check version:
```bash
asreview --version
python -m asreview --version
```

## Alternative: Use ASReview Desktop App

If command line doesn't work:
1. Download ASReview Desktop from: https://asreview.nl/download/
2. Install the desktop app
3. Open it and import `data/asreview_export.csv`

## What You'll See

After starting ASReview:
1. **Welcome screen** with options
2. **"New Project"** button
3. Click it to create a new screening project
4. Upload `data/asreview_export.csv`

## Troubleshooting

**"web is not a valid subcommand"**:
- Use `asreview lab` instead of `asreview web`

**Browser doesn't open**:
- Manually go to: `http://127.0.0.1:5000`

**Port already in use**:
- ASReview will try another port (check terminal output)
- Or stop other ASReview instances

---

**Start command**: `asreview lab`
