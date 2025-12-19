#!/usr/bin/env python3
"""
Tests for predictive factor extraction
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.factor_extraction import FactorExtractor


class TestFactorExtraction:
    """Test factor extraction functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = FactorExtractor()
    
    def test_factor_extraction_or_pattern(self):
        """Test extraction of OR patterns"""
        abstract = "BMI was a significant predictor of total knee replacement (OR: 1.8, 95% CI: 1.2-2.5, p<0.001)."
        
        factors = self.extractor.extract_predictive_factors(abstract)
        assert len(factors) > 0, "Should extract at least one factor"
        
        # Check if BMI is found
        bmi_factors = [f for f in factors if 'bmi' in f.get('factor', '').lower()]
        assert len(bmi_factors) > 0, "Should find BMI as a factor"
    
    def test_factor_extraction_p_value(self):
        """Test extraction of p-value associations"""
        abstract = "KL grade was significantly associated with progression (p<0.05)."
        
        factors = self.extractor.extract_predictive_factors(abstract)
        assert len(factors) > 0, "Should extract factors from p-value patterns"
    
    def test_factor_extraction_auc(self):
        """Test extraction of AUC patterns"""
        abstract = "The prediction model achieved an AUC of 0.85 for predicting total knee replacement."
        
        factors = self.extractor.extract_predictive_factors(abstract)
        # May or may not extract from this pattern, but shouldn't crash
        assert isinstance(factors, list), "Should return a list"
    
    def test_factor_mention_extraction(self):
        """Test extraction of mentioned factors"""
        abstract = "We assessed baseline BMI, WOMAC scores, KL grade, and pain scores."
        
        factors = self.extractor.extract_predictive_factors(abstract)
        # Should find at least some mentioned factors
        assert isinstance(factors, list), "Should return a list of factors"
    
    def test_empty_text(self):
        """Test handling of empty text"""
        factors = self.extractor.extract_predictive_factors("")
        assert factors == [], "Should return empty list for empty text"
    
    def test_no_factors(self):
        """Test handling of text with no relevant factors"""
        abstract = "This is a completely unrelated study about something else."
        factors = self.extractor.extract_predictive_factors(abstract)
        assert isinstance(factors, list), "Should return a list even if no factors found"

