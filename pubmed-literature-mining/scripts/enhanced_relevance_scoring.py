#!/usr/bin/env python3
"""
Enhanced Relevance Scoring Algorithm
Multi-dimensional scoring system for better article value assessment.
"""

import os
import json
import logging
import re
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EnhancedRelevanceScorer:
    """Enhanced relevance scoring with multi-dimensional assessment"""
    
    def __init__(self):
        # Load keywords configuration
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            config_path = os.path.join(project_root, 'config', 'keywords.json')
            
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            self.keywords = self.config['high_value_keywords']
            self.study_designs = self.config['study_designs']
            self.top_tier_journals = self.config['top_tier_journals']
            self.mid_tier_journals = self.config['mid_tier_journals']
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {}
            self.keywords = {}
            self.study_designs = {}
            self.top_tier_journals = []
            self.mid_tier_journals = []
    
    def calculate_clinical_relevance_score(self, article: Dict) -> int:
        """
        Calculate clinical relevance score (0-40 points)
        
        High (30-40): Directly predicts TKR/progression, actionable
        Medium (20-29): Related to progression, may be useful
        Low (10-19): OA-related but not progression-focused
        Very Low (0-9): Minimally relevant
        """
        text = f"{article.get('title', '')} {article.get('abstract', '')}".lower()
        score = 0
        
        # Direct prediction terms (high value)
        direct_prediction_terms = [
            'predict tkr', 'predict total knee', 'predict arthroplasty',
            'prognostic model', 'prediction model', 'risk prediction',
            'predict progression', 'predict surgery', 'predict replacement'
        ]
        for term in direct_prediction_terms:
            if term in text:
                score += 5
        
        # Progression/outcome terms (medium value)
        progression_terms = [
            'progression', 'total knee replacement', 'tkr', 'tka',
            'arthroplasty', 'joint replacement', 'surgical intervention'
        ]
        progression_count = sum(1 for term in progression_terms if term in text)
        score += min(progression_count * 2, 15)
        
        # Prediction/prognosis terms (medium value)
        prediction_terms = [
            'predictor', 'risk factor', 'prognostic', 'prognosis',
            'forecast', 'outcome prediction'
        ]
        prediction_count = sum(1 for term in prediction_terms if term in text)
        score += min(prediction_count * 2, 10)
        
        # OA-related but not progression (low value)
        if 'osteoarthritis' in text or 'knee oa' in text:
            score += 5
        
        return min(score, 40)
    
    def calculate_study_quality_score(self, article: Dict) -> int:
        """
        Calculate study quality score (0-30 points)
        - Study Design (15 pts)
        - Sample Size (10 pts)
        - Follow-up Duration (5 pts)
        """
        score = 0
        text = f"{article.get('title', '')} {article.get('abstract', '')}".lower()
        
        # Study Design (15 points max)
        if any(term in text for term in self.study_designs.get('systematic_review', [])):
            score += 15
        elif any(term in text for term in self.study_designs.get('cohort_study', [])):
            score += 12
        elif any(term in text for term in self.study_designs.get('rct', [])):
            score += 10
        elif any(term in text for term in self.study_designs.get('case_control', [])):
            score += 8
        elif any(term in text for term in self.study_designs.get('cross_sectional', [])):
            score += 5
        
        # Sample Size (10 points max)
        patterns = [
            r'\b(\d{1,3}(?:,\d{3})*)\s*(?:patients?|subjects?|participants?|individuals?|cases?)',
            r'n\s*=\s*(\d{1,3}(?:,\d{3})*)',
            r'sample\s+size\s+(?:of\s+)?(\d{1,3}(?:,\d{3})*)',
        ]
        
        max_size = 0
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    size = int(match.replace(',', ''))
                    max_size = max(max_size, size)
                except ValueError:
                    continue
        
        if max_size >= 1000:
            score += 10
        elif max_size >= 500:
            score += 8
        elif max_size >= 100:
            score += 5
        elif max_size > 0:
            score += 2
        
        # Follow-up Duration (5 points max)
        followup_patterns = [
            r'(?:follow[-\s]?up|followed|over)\s+([0-9.]+)\s*(?:years?|yrs?)',
            r'([0-9.]+)\s*(?:year|yr)\s*(?:follow[-\s]?up|follow)',
        ]
        
        max_followup = 0
        for pattern in followup_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    years = float(match)
                    max_followup = max(max_followup, years)
                except ValueError:
                    continue
        
        if max_followup >= 5:
            score += 5
        elif max_followup >= 2:
            score += 3
        elif max_followup > 0:
            score += 1
        
        return min(score, 30)
    
    def calculate_novelty_impact_score(self, article: Dict) -> int:
        """
        Calculate novelty/impact score (0-20 points)
        - Journal Impact (10 pts)
        - Recency (5 pts)
        - Novel Findings (5 pts)
        """
        score = 0
        
        # Journal Impact (10 points max)
        journal = article.get('journal', '').lower()
        if any(top_journal in journal for top_journal in self.top_tier_journals):
            score += 10
        elif any(mid_journal in journal for mid_journal in self.mid_tier_journals):
            score += 7
        else:
            score += 3  # Default: peer-reviewed
        
        # Recency (5 points max)
        pub_date = article.get('publication_date', '')
        if pub_date:
            try:
                # Try to parse date
                if isinstance(pub_date, str):
                    # Handle various date formats
                    pub_year = None
                    if len(pub_date) >= 4:
                        pub_year = int(pub_date[:4])
                    
                    if pub_year:
                        current_year = datetime.now().year
                        years_ago = current_year - pub_year
                        
                        if years_ago < 1:
                            score += 5
                        elif years_ago < 2:
                            score += 3
                        elif years_ago < 5:
                            score += 1
            except:
                pass
        
        # Novel Findings (5 points max)
        text = f"{article.get('title', '')} {article.get('abstract', '')}".lower()
        novel_indicators = [
            'novel', 'new', 'first', 'previously unreported',
            'innovative', 'breakthrough', 'significant finding'
        ]
        if any(indicator in text for indicator in novel_indicators):
            score += 3
        
        # Significant results
        if re.search(r'p\s*[<>=]\s*0\.0[0-5]', text) or 'highly significant' in text:
            score += 2
        
        return min(score, 20)
    
    def calculate_actionability_score(self, article: Dict) -> int:
        """
        Calculate actionability score (0-10 points)
        - Modifiable Factors (5 pts)
        - Clinical Applicability (5 pts)
        """
        score = 0
        text = f"{article.get('title', '')} {article.get('abstract', '')}".lower()
        
        # Modifiable Factors (5 points max)
        modifiable_terms = [
            'bmi', 'body mass index', 'weight', 'exercise', 'physical activity',
            'strength', 'muscle', 'gait', 'walking', 'lifestyle', 'intervention',
            'treatment', 'therapy', 'rehabilitation'
        ]
        modifiable_count = sum(1 for term in modifiable_terms if term in text)
        score += min(modifiable_count * 1, 5)
        
        # Clinical Applicability (5 points max)
        clinical_terms = [
            'clinical', 'practice', 'guideline', 'recommendation',
            'screening', 'assessment', 'diagnosis', 'management'
        ]
        if any(term in text for term in clinical_terms):
            score += 3
        
        # Actionable language
        actionable_terms = ['should', 'recommend', 'consider', 'suggest', 'indicate']
        if any(term in text for term in actionable_terms):
            score += 2
        
        return min(score, 10)
    
    def calculate_relevance_score(self, article: Dict) -> Tuple[int, Dict]:
        """
        Calculate overall relevance score using multi-dimensional approach
        
        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        clinical = self.calculate_clinical_relevance_score(article)
        quality = self.calculate_study_quality_score(article)
        novelty = self.calculate_novelty_impact_score(article)
        actionability = self.calculate_actionability_score(article)
        
        total_score = clinical + quality + novelty + actionability
        
        breakdown = {
            'clinical_relevance': clinical,
            'study_quality': quality,
            'novelty_impact': novelty,
            'actionability': actionability,
            'total_score': total_score
        }
        
        return total_score, breakdown
    
    def get_value_category(self, score: int) -> str:
        """Get value category based on score"""
        if score >= 80:
            return 'high_value'
        elif score >= 60:
            return 'medium_value'
        elif score >= 40:
            return 'low_value'
        else:
            return 'very_low_value'
    
    def get_priority_level(self, score: int) -> str:
        """Get priority level for review"""
        if score >= 80:
            return 'high_priority'
        elif score >= 70:
            return 'medium_high_priority'
        elif score >= 60:
            return 'medium_priority'
        elif score >= 40:
            return 'low_priority'
        else:
            return 'very_low_priority'

