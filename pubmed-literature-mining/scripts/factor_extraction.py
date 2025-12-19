#!/usr/bin/env python3
"""
Predictive Factor Extraction
Uses NLP and regex to extract predictive factors from article text.
"""

import os
import json
import logging
import re
from typing import Dict, List
from collections import defaultdict

logger = logging.getLogger(__name__)


class FactorExtractor:
    """Extracts predictive factors from article text"""
    
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
            
            self.factor_categories = self.config['predictive_factors']
            
            # Build factor keywords list
            self.factor_keywords = []
            for category, keywords in self.factor_categories.items():
                self.factor_keywords.extend(keywords)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Fallback to minimal config
            self.config = {}
            self.factor_categories = {}
            self.factor_keywords = []
    
    def extract_statistical_associations(self, text: str) -> List[Dict]:
        """
        Extract statistical associations using regex patterns
        
        Patterns:
        - "X was a predictor of Y (OR: Z, 95% CI: ...)"
        - "X associated with Y (p<0.05)"
        - "X predicted Y (AUC: Z)"
        - "X was independently associated with Y (HR: Z)"
        """
        factors = []
        
        # Pattern 1: OR with CI
        pattern1 = r'(\w+(?:\s+\w+)*)\s+(?:was|were)\s+(?:a|an|independent|significant)?\s*(?:predictor|risk\s+factor|associated)\s+(?:of|with)\s+([^()]+?)\s*\([^)]*(?:OR|odds\s+ratio|hazard\s+ratio|HR)[^)]*:?\s*([\d.]+)[^)]*\)'
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            factor = match.group(1).strip()
            outcome = match.group(2).strip()
            effect = match.group(3).strip()
            
            # Extract full context
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            
            factors.append({
                'factor': factor,
                'outcome': outcome,
                'effect_size': f"OR/HR: {effect}",
                'significance': 'p-value in context',
                'context': context
            })
        
        # Pattern 2: p-value associations
        pattern2 = r'(\w+(?:\s+\w+)*)\s+(?:was|were)\s+(?:significantly|independently)?\s*(?:associated|correlated|related)\s+with\s+([^,;.]+?)\s*[,\s]+(?:p\s*[<>=]\s*[\d.]+|p\s*=\s*[\d.]+)'
        matches = re.finditer(pattern2, text, re.IGNORECASE)
        for match in matches:
            factor = match.group(1).strip()
            outcome = match.group(2).strip()
            
            # Extract p-value
            p_match = re.search(r'p\s*[<>=]\s*([\d.]+)', match.group(0), re.IGNORECASE)
            p_value = p_match.group(1) if p_match else 'not specified'
            
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            
            factors.append({
                'factor': factor,
                'outcome': outcome,
                'effect_size': 'not specified',
                'significance': f"p<{p_value}",
                'context': context
            })
        
        # Pattern 3: AUC/ROC predictions
        pattern3 = r'(\w+(?:\s+\w+)*)\s+(?:predicted|prediction\s+of)\s+([^,;.]+?)\s*[,\s]+(?:AUC|area\s+under\s+curve|C-index)[\s:]+([\d.]+)'
        matches = re.finditer(pattern3, text, re.IGNORECASE)
        for match in matches:
            factor = match.group(1).strip()
            outcome = match.group(2).strip()
            auc = match.group(3).strip()
            
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() +100)
            context = text[start:end].strip()
            
            factors.append({
                'factor': factor,
                'outcome': outcome,
                'effect_size': f"AUC: {auc}",
                'significance': 'not specified',
                'context': context
            })
        
        return factors
    
    def extract_factor_mentions(self, text: str) -> List[str]:
        """Extract mentions of known predictive factors"""
        text_lower = text.lower()
        found_factors = []
        
        for category, keywords in self.factor_categories.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    # Capitalize first letter
                    factor_name = keyword.title() if keyword.islower() else keyword
                    if factor_name not in found_factors:
                        found_factors.append(factor_name)
        
        return found_factors
    
    def extract_predictive_factors(self, text: str) -> List[Dict]:
        """
        Extract all predictive factors from text
        
        Args:
            text: Article abstract or full text
            
        Returns:
            List of factor dictionaries
        """
        if not text:
            return []
        
        factors = []
        
        # Extract statistical associations
        statistical_factors = self.extract_statistical_associations(text)
        factors.extend(statistical_factors)
        
        # Extract factor mentions (for articles without clear statistical reporting)
        mentioned_factors = self.extract_factor_mentions(text)
        
        # If we found statistical associations, use those
        # Otherwise, create simple entries for mentioned factors
        if not statistical_factors and mentioned_factors:
            # Look for context around each mentioned factor
            for factor in mentioned_factors[:10]:  # Limit to top 10
                pattern = r'.{0,200}' + re.escape(factor.lower()) + r'.{0,200}'
                matches = re.finditer(pattern, text.lower())
                for match in list(matches)[:1]:  # Take first match
                    context = match.group(0).strip()
                    factors.append({
                        'factor': factor,
                        'outcome': 'knee osteoarthritis progression',
                        'effect_size': 'not specified',
                        'significance': 'mentioned in text',
                        'context': context
                    })
                    break
        
        # Remove duplicates (same factor + outcome combination)
        seen = set()
        unique_factors = []
        for factor in factors:
            key = (factor['factor'].lower(), factor.get('outcome', '').lower())
            if key not in seen:
                seen.add(key)
                unique_factors.append(factor)
        
        return unique_factors[:20]  # Limit to 20 factors per article

