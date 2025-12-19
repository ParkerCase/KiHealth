#!/usr/bin/env python3
"""
Tests for Xata database integration
"""

import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.xata_client import XataClient


class TestXataIntegration:
    """Test Xata database operations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = XataClient()
    
    def test_client_initialization(self):
        """Test that client initializes correctly"""
        assert self.client is not None
        assert self.client.table_name == 'pubmed_articles'
    
    def test_query_structure(self):
        """Test query method returns list"""
        # This will return empty if Xata is not configured, but should not crash
        results = self.client.query_articles(limit=10)
        assert isinstance(results, list), "Should return a list"
    
    def test_get_paywalled_articles_structure(self):
        """Test get_paywalled_articles returns list"""
        results = self.client.get_paywalled_articles(threshold=70)
        assert isinstance(results, list), "Should return a list"
    
    def test_get_high_relevance_articles_structure(self):
        """Test get_high_relevance_articles returns list"""
        results = self.client.get_high_relevance_articles(threshold=70)
        assert isinstance(results, list), "Should return a list"
    
    @pytest.mark.skip(reason="Requires actual Xata credentials")
    def test_insert_article(self):
        """Test article insertion (requires Xata credentials)"""
        test_article = {
            'pmid': '99999999',
            'title': 'Test Article',
            'abstract': 'This is a test abstract.',
            'journal': 'Test Journal',
            'relevance_score': 50,
            'access_type': 'open_access',
            'processing_status': 'processed',
            'created_at': datetime.now().isoformat()
        }
        
        result = self.client.insert_article(test_article)
        # Should not crash even if credentials are missing
        assert isinstance(result, bool), "Should return boolean"

