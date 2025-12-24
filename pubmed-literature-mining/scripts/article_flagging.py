#!/usr/bin/env python3
"""
Article Flagging Framework
Determines which articles should be flagged for review based on multiple criteria.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ArticleFlaggingFramework:
    """Framework for determining which articles to flag for review"""
    
    def __init__(self):
        # Load flagging criteria from config if available
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            config_path = os.path.join(project_root, 'config', 'flagging_criteria.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.criteria = json.load(f)
            else:
                # Use default criteria
                self.criteria = self._get_default_criteria()
        except Exception as e:
            logger.warning(f"Could not load flagging criteria: {e}, using defaults")
            self.criteria = self._get_default_criteria()
    
    def _get_default_criteria(self) -> Dict:
        """Get default flagging criteria"""
        return {
            "high_priority": {
                "min_score": 80,
                "description": "Must-read, actionable, high-quality articles",
                "flags": ["high_value", "must_review"]
            },
            "medium_high_priority": {
                "min_score": 70,
                "max_score": 79,
                "description": "Very relevant, good quality",
                "flags": ["medium_high", "should_review"]
            },
            "paywalled_high_value": {
                "min_score": 80,
                "access_type": "paywalled",
                "description": "High-value paywalled articles that may need access",
                "flags": ["paywalled", "high_value", "consider_access"]
            },
            "recent_high_value": {
                "min_score": 70,
                "max_age_days": 365,
                "description": "Recent high-value articles",
                "flags": ["recent", "high_value", "priority"]
            },
            "large_sample": {
                "min_sample_size": 500,
                "min_score": 60,
                "description": "Large sample size studies",
                "flags": ["large_sample", "high_quality"]
            },
            "systematic_review": {
                "study_type": "systematic_review",
                "min_score": 60,
                "description": "Systematic reviews and meta-analyses",
                "flags": ["systematic_review", "comprehensive"]
            },
            "novel_findings": {
                "min_novelty_score": 15,
                "min_score": 70,
                "description": "Articles with novel findings",
                "flags": ["novel", "high_impact"]
            },
            "actionable": {
                "min_actionability_score": 7,
                "min_score": 70,
                "description": "Articles with actionable insights",
                "flags": ["actionable", "clinical_applicable"]
            }
        }
    
    def should_flag_for_review(self, article: Dict) -> Tuple[bool, List[str], str]:
        """
        Determine if an article should be flagged for review
        
        Args:
            article: Article dictionary with all metadata
            
        Returns:
            Tuple of (should_flag: bool, flags: List[str], reason: str)
        """
        flags = []
        reasons = []
        
        # Extract article data
        score = article.get('relevance_score', 0)
        value_category = article.get('value_category', '')
        priority_level = article.get('priority_level', '')
        access_type = article.get('access_type', '')
        score_breakdown = article.get('relevance_score_breakdown', {})
        publication_date = article.get('publication_date', '')
        
        # Check high priority (score >= 80)
        if score >= self.criteria['high_priority']['min_score']:
            flags.extend(self.criteria['high_priority']['flags'])
            reasons.append(f"High-value article (score: {score})")
        
        # Check medium-high priority (score 70-79)
        if (self.criteria['medium_high_priority']['min_score'] <= score < 
            self.criteria['medium_high_priority']['max_score']):
            flags.extend(self.criteria['medium_high_priority']['flags'])
            reasons.append(f"Medium-high value (score: {score})")
        
        # Check paywalled high-value
        if (access_type == 'paywalled' and 
            score >= self.criteria['paywalled_high_value']['min_score']):
            flags.extend(self.criteria['paywalled_high_value']['flags'])
            reasons.append(f"High-value paywalled article (score: {score})")
        
        # Check recent high-value
        if score >= self.criteria['recent_high_value']['min_score']:
            try:
                if publication_date:
                    pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
                    age_days = (datetime.now() - pub_date.replace(tzinfo=None)).days
                    if age_days <= self.criteria['recent_high_value']['max_age_days']:
                        flags.extend(self.criteria['recent_high_value']['flags'])
                        reasons.append(f"Recent high-value article ({age_days} days old)")
            except Exception as e:
                logger.debug(f"Could not parse publication date: {e}")
        
        # Check large sample size
        abstract = article.get('abstract', '').lower()
        import re
        sample_patterns = [
            r'\b(\d{1,3}(?:,\d{3})*)\s*(?:patients?|subjects?|participants?|individuals?|cases?)',
            r'n\s*=\s*(\d{1,3}(?:,\d{3})*)',
        ]
        max_sample = 0
        for pattern in sample_patterns:
            matches = re.findall(pattern, abstract)
            for match in matches:
                try:
                    size = int(match.replace(',', ''))
                    max_sample = max(max_sample, size)
                except ValueError:
                    continue
        
        if (max_sample >= self.criteria['large_sample']['min_sample_size'] and
            score >= self.criteria['large_sample']['min_score']):
            flags.extend(self.criteria['large_sample']['flags'])
            reasons.append(f"Large sample size (n={max_sample})")
        
        # Check systematic review
        if 'systematic review' in abstract or 'meta-analysis' in abstract:
            if score >= self.criteria['systematic_review']['min_score']:
                flags.extend(self.criteria['systematic_review']['flags'])
                reasons.append("Systematic review or meta-analysis")
        
        # Check novel findings
        novelty_score = score_breakdown.get('novelty_impact', 0)
        if (novelty_score >= self.criteria['novel_findings']['min_novelty_score'] and
            score >= self.criteria['novel_findings']['min_score']):
            flags.extend(self.criteria['novel_findings']['flags'])
            reasons.append(f"Novel findings (novelty score: {novelty_score})")
        
        # Check actionable
        actionability_score = score_breakdown.get('actionability', 0)
        if (actionability_score >= self.criteria['actionable']['min_actionability_score'] and
            score >= self.criteria['actionable']['min_score']):
            flags.extend(self.criteria['actionable']['flags'])
            reasons.append(f"Actionable insights (actionability score: {actionability_score})")
        
        # Determine if should flag
        should_flag = len(flags) > 0
        
        # Remove duplicates from flags
        flags = list(set(flags))
        
        # Create reason string
        reason = "; ".join(reasons) if reasons else "No specific criteria met"
        
        return should_flag, flags, reason
    
    def get_flagging_summary(self, articles: List[Dict]) -> Dict:
        """
        Get summary of flagged articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary with flagging summary
        """
        flagged = []
        flag_counts = {}
        priority_counts = {
            'high_priority': 0,
            'medium_high_priority': 0,
            'paywalled_high_value': 0,
            'recent_high_value': 0,
            'large_sample': 0,
            'systematic_review': 0,
            'novel_findings': 0,
            'actionable': 0
        }
        
        for article in articles:
            should_flag, flags, reason = self.should_flag_for_review(article)
            if should_flag:
                flagged.append({
                    'pmid': article.get('pmid'),
                    'title': article.get('title', 'No title')[:100],
                    'score': article.get('relevance_score', 0),
                    'flags': flags,
                    'reason': reason,
                    'access_type': article.get('access_type', 'unknown')
                })
                
                # Count flags
                for flag in flags:
                    flag_counts[flag] = flag_counts.get(flag, 0) + 1
                
                # Count by priority type
                if 'must_review' in flags:
                    priority_counts['high_priority'] += 1
                if 'should_review' in flags:
                    priority_counts['medium_high_priority'] += 1
                if 'consider_access' in flags:
                    priority_counts['paywalled_high_value'] += 1
                if 'priority' in flags and 'recent' in flags:
                    priority_counts['recent_high_value'] += 1
                if 'large_sample' in flags:
                    priority_counts['large_sample'] += 1
                if 'systematic_review' in flags:
                    priority_counts['systematic_review'] += 1
                if 'novel' in flags:
                    priority_counts['novel_findings'] += 1
                if 'actionable' in flags:
                    priority_counts['actionable'] += 1
        
        return {
            'total_articles': len(articles),
            'flagged_count': len(flagged),
            'flagging_rate': len(flagged) / len(articles) * 100 if articles else 0,
            'flagged_articles': flagged,
            'flag_counts': flag_counts,
            'priority_counts': priority_counts
        }
    
    def get_review_priority_list(self, articles: List[Dict]) -> List[Dict]:
        """
        Get prioritized list of articles for review
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of articles sorted by priority
        """
        prioritized = []
        
        for article in articles:
            should_flag, flags, reason = self.should_flag_for_review(article)
            if should_flag:
                # Calculate priority score (higher = more important)
                priority_score = article.get('relevance_score', 0)
                
                # Boost priority for certain flags
                if 'must_review' in flags:
                    priority_score += 20
                if 'consider_access' in flags:
                    priority_score += 10
                if 'recent' in flags:
                    priority_score += 5
                if 'novel' in flags:
                    priority_score += 5
                if 'actionable' in flags:
                    priority_score += 5
                
                prioritized.append({
                    'article': article,
                    'priority_score': priority_score,
                    'flags': flags,
                    'reason': reason
                })
        
        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized

