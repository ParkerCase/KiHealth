#!/usr/bin/env python3
"""
Tests for open access detection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.open_access_detector import OpenAccessDetector


class TestOpenAccessDetection:
    """Test open access detection functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.detector = OpenAccessDetector()
    
    def test_open_access_detection_structure(self):
        """Test that check_open_access returns expected structure"""
        result = self.detector.check_open_access("10.1371/journal.pone.0123456", pmid="12345678")
        
        assert isinstance(result, dict), "Should return a dictionary"
        assert 'is_open_access' in result, "Should include is_open_access field"
        assert 'pdf_url' in result, "Should include pdf_url field"
        assert 'source' in result, "Should include source field"
        assert isinstance(result['is_open_access'], bool), "is_open_access should be boolean"
    
    def test_no_doi(self):
        """Test handling of missing DOI"""
        result = self.detector.check_open_access("", pmid="12345678")
        assert result['is_open_access'] == False, "Should return False for missing DOI"
    
    def test_pdf_directory_creation(self):
        """Test that PDF directory is created"""
        assert os.path.exists(self.detector.pdf_dir), "PDF directory should exist"
    
    @pytest.mark.skip(reason="Requires actual API calls and may be rate-limited")
    def test_unpaywall_api(self):
        """Test Unpaywall API (skipped by default to avoid rate limits)"""
        # Known open access DOI
        result = self.detector.check_unpaywall("10.1371/journal.pone.0123456")
        if result:
            assert 'is_open_access' in result
            assert 'source' in result

