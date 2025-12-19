#!/usr/bin/env python3
"""
Relevance Scoring Algorithm
Scores articles 0-100 based on keywords, study design, sample size, and journal impact.
"""

import os
import json
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class RelevanceScorer:
    """Calculates relevance scores for PubMed articles"""
    
    def __init__(self):
        # Load keywords configuration
        try:
            # Get project root directory (parent of scripts/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            config_path = os.path.join(project_root, 'config', 'keywords.json')
            
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            self.keywords = self.config['high_value_keywords']
            self.study_designs = self.config['study_designs']
            self.top_tier_journals = self.config['top_tier_journals']
            self.mid_tier_journals = self.config['mid_tier_journals']
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Fallback to minimal config
            self.config = {}
            self.keywords = {'predictive_factors': [], 'outcomes': [], 'imaging': [], 'symptoms': [], 'statistical': []}
            self.study_designs = {}
            self.top_tier_journals = []
            self.mid_tier_journals = []
    
    def count_keywords(self, text: str) -> int:
        """Count occurrences of high-value keywords in text"""
        if not text:
            return 0
        
        text_lower = text.lower()
        count = 0
        
        # Count keywords from each category
        for category, keywords in self.keywords.items():
            for keyword in keywords:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                count += matches
        
        return count
    
    def get_study_design_score(self, article: Dict) -> int:
        """
        Score based on study design (max 30 points)
        
        Returns:
            Score from 0-30
        """
        text = f"{article.get('title', '')} {article.get('abstract', '')}".lower()
        
        # Check for systematic review/meta-analysis first (highest score)
        for design_term in self.study_designs['systematic_review']:
            if design_term.lower() in text:
                return 20
        
        # Check for cohort study
        for design_term in self.study_designs['cohort_study']:
            if design_term.lower() in text:
                return 15
        
        # Check for RCT
        for design_term in self.study_designs['rct']:
            if design_term.lower() in text:
                return 15
        
        # Check for case-control
        for design_term in self.study_designs['case_control']:
            if design_term.lower() in text:
                return 10
        
        # Check for cross-sectional
        for design_term in self.study_designs['cross_sectional']:
            if design_term.lower() in text:
                return 5
        
        return 0
    
    def get_sample_size_score(self, article: Dict) -> int:
        """
        Score based on sample size (max 15 points)
        
        Returns:
            Score from 0-15
        """
        text = f"{article.get('abstract', '')}".lower()
        
        # Look for sample size patterns
        patterns = [
            r'\b(\d{1,3}(?:,\d{3})*)\s*(?:patients?|subjects?|participants?|individuals?|cases?)',
            r'n\s*=\s*(\d{1,3}(?:,\d{3})*)',
            r'sample\s+size\s+(?:of\s+)?(\d{1,3}(?:,\d{3})*)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:patients?|subjects?)\s+(?:were|included|enrolled)'
        ]
        
        max_size = 0
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Remove commas and convert to int
                try:
                    size = int(match.replace(',', ''))
                    max_size = max(max_size, size)
                except ValueError:
                    continue
        
        # Score based on size
        if max_size >= 1000:
            return 15
        elif max_size >= 500:
            return 10
        elif max_size >= 100:
            return 5
        elif max_size > 0:
            return 2
        else:
            return 0
    
    def get_journal_score(self, article: Dict) -> int:
        """
        Score based on journal impact (max 15 points)
        
        Returns:
            Score from 0-15
        """
        journal = article.get('journal', '').lower()
        
        if not journal:
            return 5  # Default for unknown journals
        
        # Check top-tier journals
        for top_journal in self.top_tier_journals:
            if top_journal.lower() in journal:
                return 15
        
        # Check mid-tier journals
        for mid_journal in self.mid_tier_journals:
            if mid_journal.lower() in journal:
                return 10
        
        # Default: peer-reviewed journal (assumed)
        return 5
    
    def calculate_relevance_score(self, article: Dict) -> int:
        """
        Calculate overall relevance score (0-100)
        
        Args:
            article: Dictionary with title, abstract, journal, etc.
            
        Returns:
            Score from 0-100
        """
        score = 0
        
        # Keyword matching (40 points max)
        text = f"{article.get('title', '')} {article.get('abstract', '')}"
        keyword_count = self.count_keywords(text)
        # Scale: each keyword worth up to 4 points, max 40
        keyword_score = min(keyword_count * 2, 40)  # Adjusted: 2 points per keyword
        score += keyword_score
        
        # Study design (30 points max)
        design_score = self.get_study_design_score(article)
        score += design_score
        
        # Sample size (15 points max)
        size_score = self.get_sample_size_score(article)
        score += size_score
        
        # Journal impact (15 points max)
        journal_score = self.get_journal_score(article)
        score += journal_score
        
        # Ensure score is between 0 and 100
        return min(max(score, 0), 100)

