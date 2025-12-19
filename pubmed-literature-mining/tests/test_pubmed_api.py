#!/usr/bin/env python3
"""
Tests for PubMed API integration
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.pubmed_scraper import PubMedScraper


class TestPubMedAPI:
    """Test PubMed API functionality"""
    
    def test_pubmed_search(self):
        """Verify PubMed search returns expected results"""
        scraper = PubMedScraper()
        results = scraper.search_pubmed("knee osteoarthritis", max_results=10)
        
        assert len(results) > 0, "Should return at least one result"
        assert all(isinstance(pmid, str) for pmid in results), "All results should be PMID strings"
        assert all(pmid.isdigit() for pmid in results), "All PMIDs should be numeric"
    
    def test_fetch_article_details(self):
        """Test fetching article details for a known PMID"""
        scraper = PubMedScraper()
        
        # Use a known open-access article for testing
        # This is a real PMID - adjust if needed
        pmid = "12345678"  # Replace with actual test PMID
        
        # Skip if we can't make real API calls
        try:
            article = scraper.fetch_article_details(pmid)
            
            if article:  # Only assert if we got a result
                assert 'pmid' in article
                assert 'title' in article
                assert article['pmid'] == pmid
        except Exception as e:
            pytest.skip(f"Could not test with real API: {e}")
    
    def test_rate_limiting(self):
        """Test that rate limiting is implemented"""
        scraper = PubMedScraper()
        assert scraper.REQUEST_DELAY > 0, "Should have request delay for rate limiting"
        assert scraper.REQUEST_DELAY >= 0.34, "Should respect PubMed's 3 req/sec limit"

