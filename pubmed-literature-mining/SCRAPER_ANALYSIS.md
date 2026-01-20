# Scraper Analysis: Are We Finding New Articles?

## The Reality Check

### What PubMed Has:
- **Total knee OA articles**: ~24,210
- **2024-2025 articles**: ~5,237
- **Articles matching our queries**: Varies by query (380-5,237)

### What We Have:
- **Total in database**: 4,674 articles
- **2024-2025 articles**: Only 61 articles
- **Coverage**: ~19% of total PubMed articles

## The Problem

**Our queries are TOO NARROW and TOO RECENT-focused:**

1. **Date restriction**: We're only searching 2024-2025, missing ~19,000 older articles
2. **Overly specific terms**: Terms like "patient reported outcome", "biomarker", "genetic" are too narrow
3. **We're missing 80% of available articles!**

## What's Happening

The scraper IS working, but:
- It finds articles from PubMed
- Most are duplicates because we've already scraped the recent/specific ones
- We're NOT searching the broader pool of ~19,000 older articles

## The Solution

We need to:
1. **Remove date restrictions** for broader searches
2. **Use simpler, broader queries** to find articles we haven't scraped
3. **Search older articles** (2010-2023) that we likely haven't covered
4. **Use MeSH terms** to find more articles

## Recommendation

Change the search strategy to:
- Search ALL years (not just 2024-2025)
- Use broader terms initially
- Then filter by relevance score after scraping
- This will find the ~19,000 articles we're missing
