#!/usr/bin/env python3
"""
Tests for relevance scoring algorithm
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.relevance_scoring import RelevanceScorer


class TestRelevanceScoring:
    """Test relevance scoring functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.scorer = RelevanceScorer()
    
    def test_relevance_scoring_high_relevance(self):
        """Verify scoring algorithm for high-relevance article"""
        high_relevance_article = {
            'title': 'Predictors of total knee replacement in knee osteoarthritis: A cohort study',
            'abstract': 'This prospective cohort study included 1500 patients with knee osteoarthritis. We assessed baseline KL grade, WOMAC scores, BMI, and other factors. Multivariable regression analysis identified BMI (OR: 1.8, p<0.001) and KL grade (OR: 2.5, p<0.001) as significant predictors of total knee replacement. The prediction model achieved an AUC of 0.85.',
            'journal': 'Arthritis & Rheumatology'
        }
        
        score = self.scorer.calculate_relevance_score(high_relevance_article)
        assert score >= 70, f"High-relevance article should score ≥70, got {score}"
        assert score <= 100, "Score should not exceed 100"
    
    def test_relevance_scoring_low_relevance(self):
        """Verify scoring for low-relevance article"""
        low_relevance_article = {
            'title': 'General medical study',
            'abstract': 'This is a study about something unrelated.',
            'journal': 'Unknown Journal'
        }
        
        score = self.scorer.calculate_relevance_score(low_relevance_article)
        assert score < 50, f"Low-relevance article should score <50, got {score}"
        assert score >= 0, "Score should not be negative"
    
    def test_keyword_counting(self):
        """Test keyword counting functionality"""
        text = "This study examines predictors of total knee replacement using WOMAC scores and KL grade."
        count = self.scorer.count_keywords(text)
        assert count > 0, "Should find keywords in relevant text"
    
    def test_study_design_scoring(self):
        """Test study design scoring"""
        # Test cohort study
        cohort_article = {
            'title': 'Cohort study of knee osteoarthritis',
            'abstract': 'This is a prospective cohort study.'
        }
        score = self.scorer.get_study_design_score(cohort_article)
        assert score == 15, f"Cohort study should score 15, got {score}"
        
        # Test systematic review
        review_article = {
            'title': 'Systematic review',
            'abstract': 'This is a systematic review and meta-analysis.'
        }
        score = self.scorer.get_study_design_score(review_article)
        assert score == 20, f"Systematic review should score 20, got {score}"
    
    def test_sample_size_scoring(self):
        """Test sample size scoring"""
        # Large sample
        large_sample = {
            'abstract': 'This study included 1500 patients with knee osteoarthritis.'
        }
        score = self.scorer.get_sample_size_score(large_sample)
        assert score == 15, f"Large sample (≥1000) should score 15, got {score}"
        
        # Medium sample
        medium_sample = {
            'abstract': 'We enrolled 500 participants in this study.'
        }
        score = self.scorer.get_sample_size_score(medium_sample)
        assert score == 10, f"Medium sample (500-999) should score 10, got {score}"
    
    def test_journal_scoring(self):
        """Test journal impact scoring"""
        # Top-tier journal
        top_journal = {
            'journal': 'New England Journal of Medicine'
        }
        score = self.scorer.get_journal_score(top_journal)
        assert score == 15, f"Top-tier journal should score 15, got {score}"
        
        # Mid-tier journal
        mid_journal = {
            'journal': 'Osteoarthritis and Cartilage'
        }
        score = self.scorer.get_journal_score(mid_journal)
        assert score == 10, f"Mid-tier journal should score 10, got {score}"

