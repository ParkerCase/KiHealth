# Deployment Guide

## Pre-Deployment Checklist

### 1. GitHub Repository Setup

**No database setup required!** Articles are stored in `data/articles/` as JSON files, automatically version-controlled by Git.

1. **Create Repository**: Create a new GitHub repository (or use existing)
2. **Push Code**: Push this codebase to your repository

**No secrets needed!** The system uses file-based storage (100% free).

### 3. Local Testing

Before enabling the daily schedule, test manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (see README.md)
# Edit .env with your credentials

# Test PubMed scraper
python scripts/pubmed_scraper.py

# Test analysis and notifications
python scripts/analyze_and_notify.py

# Run tests
pytest tests/ -v
```

### 4. First Manual Run

1. Go to GitHub Actions tab
2. Select "PubMed OA Literature Mining" workflow
3. Click "Run workflow" → "Run workflow"
4. Monitor the run for errors
5. Check:
   - ✅ Workflow completes successfully
   - ✅ Xata database has new articles
   - ✅ Logs are generated
   - ✅ LATEST_FINDINGS.md is created/updated

### 5. Enable Daily Schedule

After 1 week of successful manual runs:

1. The workflow is already configured with daily schedule (6 AM UTC)
2. No action needed - it will run automatically
3. Monitor first few automated runs

## Post-Deployment Monitoring

### Week 1: Daily Checks

- [ ] Check GitHub Actions runs daily
- [ ] Verify articles are being added to Xata
- [ ] Review relevance scores (should be reasonable)
- [ ] Check for error logs
- [ ] Verify notifications are working (if configured)

### Week 2-4: Weekly Reviews

- [ ] Review LATEST_FINDINGS.md weekly
- [ ] Check Xata database growth
- [ ] Review paywalled article alerts
- [ ] Adjust relevance threshold if needed
- [ ] Review extracted predictive factors

### Ongoing: Monthly Reviews

- [ ] Review system performance
- [ ] Check rate limit usage
- [ ] Update keywords if needed
- [ ] Review and adjust scoring weights
- [ ] Archive old logs if needed

## Troubleshooting

### Workflow Fails Immediately

**Check:**
- GitHub Secrets are configured correctly
- Xata API key has correct permissions
- Database URL format is correct

**Solution:**
- Verify secrets in repository settings
- Test Xata connection locally
- Check Xata API status

### No Articles Found

**Check:**
- PubMed API is accessible
- Search query syntax is correct
- Date filters are appropriate

**Solution:**
- Test PubMed search manually
- Adjust date range if needed
- Check for API rate limiting

### Articles Not Stored in Xata

**Check:**
- Xata API key permissions
- Table schema matches expected format
- Network connectivity

**Solution:**
- Verify API key has write permissions
- Check table column types
- Review Xata API logs

### Low Relevance Scores

**Check:**
- Keywords in config/keywords.json
- Scoring algorithm weights
- Sample articles

**Solution:**
- Add missing keywords
- Adjust scoring weights
- Review sample articles manually

### PDF Downloads Failing

**Check:**
- PDF URLs are accessible
- Network connectivity
- File permissions

**Solution:**
- Some publishers block automated downloads
- This is expected for some articles
- System will continue with abstract-only analysis

## Performance Optimization

### If Processing Takes Too Long

1. Reduce `MAX_ARTICLES_PER_RUN` in .env
2. Increase `REQUEST_DELAY` in scripts
3. Process in batches

### If Rate Limits Hit

1. Increase delays between requests
2. Reduce articles per run
3. Split into multiple workflow runs

## Security Best Practices

1. ✅ Never commit `.env` file
2. ✅ Use GitHub Secrets for all credentials
3. ✅ Rotate API keys periodically
4. ✅ Monitor API usage
5. ✅ Review logs for sensitive data

## Rollback Plan

If issues occur:

1. **Disable Schedule**: Comment out schedule in workflow file
2. **Fix Issues**: Address problems in code
3. **Test Locally**: Verify fixes work
4. **Manual Run**: Test via workflow_dispatch
5. **Re-enable**: Uncomment schedule after verification

## Support Resources

- **Xata Documentation**: https://xata.io/docs
- **PubMed API Docs**: https://www.ncbi.nlm.nih.gov/books/NBK25497/
- **Unpaywall API**: https://unpaywall.org/products/api
- **GitHub Actions Docs**: https://docs.github.com/en/actions

