#!/usr/bin/env python3
"""
PROBAST (Prediction model Risk Of Bias Assessment Tool) Assessment Module
Assesses prediction model studies across 4 domains to maintain top 7% PROBAST compliance.

PROBAST Domains:
1. Participants (Selection bias)
2. Predictors (Measurement bias)
3. Outcome (Measurement bias)
4. Analysis (Statistical bias)

Only papers scoring "Low Risk" on all 4 domains (or 3 Low + 1 Moderate with justification)
are used in the model to maintain PROBAST compliance.
"""

import os
import json
import logging
from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class PROBASTRiskLevel(Enum):
    """PROBAST risk levels"""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    UNCLEAR = "Unclear"


class PROBASTAssessment:
    """PROBAST assessment for prediction model studies"""
    
    def __init__(self):
        self.domain_questions = {
            "domain_1_participants": [
                "Were appropriate data sources used?",
                "Were all eligible participants included?",
                "Were participants selected without regard to outcome?",
                "Were predictors measured at the same time or before outcome?"
            ],
            "domain_2_predictors": [
                "Were predictors defined and assessed in a similar way for all participants?",
                "Were predictors assessed without knowledge of outcome?",
                "Were all predictors available at the time the model was intended to be used?"
            ],
            "domain_3_outcome": [
                "Was the outcome defined and determined in a similar way for all participants?",
                "Was the outcome determined without knowledge of predictor information?",
                "Was the outcome determined appropriately?"
            ],
            "domain_4_analysis": [
                "Were there a reasonable number of participants with the outcome?",
                "Were continuous variables handled appropriately?",
                "Were all enrolled participants included in the analysis?",
                "Were selection of predictors based on univariable analysis avoided?",
                "Were complexities in the data accounted for?",
                "Were model performance measures evaluated appropriately?"
            ]
        }
    
    def assess_article(self, article: Dict, manual_assessment: Optional[Dict] = None) -> Dict:
        """
        Assess an article using PROBAST criteria
        
        Args:
            article: Article dictionary with metadata
            manual_assessment: Optional manual assessment override
            
        Returns:
            Dictionary with PROBAST scores for each domain
        """
        if manual_assessment:
            # Use manual assessment if provided
            return {
                "domain_1_participants": manual_assessment.get("domain_1", "Unclear"),
                "domain_2_predictors": manual_assessment.get("domain_2", "Unclear"),
                "domain_3_outcome": manual_assessment.get("domain_3", "Unclear"),
                "domain_4_analysis": manual_assessment.get("domain_4", "Unclear"),
                "overall_risk": self._calculate_overall_risk(manual_assessment),
                "assessment_date": datetime.now().isoformat(),
                "assessment_method": "manual"
            }
        
        # Automated assessment based on article metadata
        assessment = {
            "domain_1_participants": self._assess_domain_1(article),
            "domain_2_predictors": self._assess_domain_2(article),
            "domain_3_outcome": self._assess_domain_3(article),
            "domain_4_analysis": self._assess_domain_4(article),
            "assessment_date": datetime.now().isoformat(),
            "assessment_method": "automated"
        }
        
        assessment["overall_risk"] = self._calculate_overall_risk(assessment)
        
        return assessment
    
    def _assess_domain_1(self, article: Dict) -> str:
        """Assess Domain 1: Participants"""
        # Check study design
        study_type = article.get("study_type", "").lower()
        abstract = article.get("abstract", "").lower()
        title = article.get("title", "").lower()
        
        # High risk indicators
        if any(term in abstract or term in title for term in ["case report", "case series", "case-control"]):
            return PROBASTRiskLevel.HIGH.value
        
        # Low risk indicators
        if any(term in abstract or term in title for term in [
            "cohort", "prospective", "retrospective cohort", "longitudinal",
            "population-based", "registry", "database"
        ]):
            # Check for appropriate selection
            if any(term in abstract for term in ["consecutive", "all eligible", "population-based"]):
                return PROBASTRiskLevel.LOW.value
            return PROBASTRiskLevel.MODERATE.value
        
        return PROBASTRiskLevel.UNCLEAR.value
    
    def _assess_domain_2(self, article: Dict) -> str:
        """Assess Domain 2: Predictors"""
        abstract = article.get("abstract", "").lower()
        
        # High risk indicators
        if any(term in abstract for term in ["retrospective", "chart review", "self-reported"]):
            # But check if predictors were measured before outcome
            if "before" in abstract or "baseline" in abstract:
                return PROBASTRiskLevel.MODERATE.value
            return PROBASTRiskLevel.HIGH.value
        
        # Low risk indicators
        if any(term in abstract for term in [
            "prospectively", "standardized", "validated", "blinded assessment"
        ]):
            return PROBASTRiskLevel.LOW.value
        
        return PROBASTRiskLevel.MODERATE.value
    
    def _assess_domain_3(self, article: Dict) -> str:
        """Assess Domain 3: Outcome"""
        abstract = article.get("abstract", "").lower()
        
        # Check for clear outcome definition
        outcome_terms = [
            "total knee replacement", "tkr", "tka", "arthroplasty",
            "womac", "koos", "pain score", "functional outcome"
        ]
        
        has_clear_outcome = any(term in abstract for term in outcome_terms)
        
        if not has_clear_outcome:
            return PROBASTRiskLevel.UNCLEAR.value
        
        # Check for blinded outcome assessment
        if any(term in abstract for term in ["blinded", "independent assessor", "adjudicated"]):
            return PROBASTRiskLevel.LOW.value
        
        # Check for objective outcome (TKR is objective)
        if any(term in abstract for term in ["tkr", "tka", "arthroplasty", "surgery"]):
            return PROBASTRiskLevel.LOW.value
        
        return PROBASTRiskLevel.MODERATE.value
    
    def _assess_domain_4(self, article: Dict) -> str:
        """Assess Domain 4: Analysis"""
        abstract = article.get("abstract", "").lower()
        
        # Check sample size
        sample_size = self._extract_sample_size(abstract)
        if sample_size:
            if sample_size < 100:
                return PROBASTRiskLevel.HIGH.value
            elif sample_size < 200:
                return PROBASTRiskLevel.MODERATE.value
        
        # Check for appropriate statistical methods
        stat_terms = [
            "multivariable", "multivariate", "logistic regression", "cox regression",
            "calibration", "discrimination", "auc", "c-statistic", "harrell's c"
        ]
        
        has_appropriate_stats = any(term in abstract for term in stat_terms)
        
        if not has_appropriate_stats:
            return PROBASTRiskLevel.MODERATE.value
        
        # Check for validation
        if any(term in abstract for term in ["validation", "internal validation", "external validation", "bootstrap"]):
            return PROBASTRiskLevel.LOW.value
        
        # Check for events per variable
        if "epv" in abstract or "events per variable" in abstract:
            epv_match = self._extract_epv(abstract)
            if epv_match and epv_match >= 15:
                return PROBASTRiskLevel.LOW.value
        
        return PROBASTRiskLevel.MODERATE.value
    
    def _extract_sample_size(self, text: str) -> Optional[int]:
        """Extract sample size from text"""
        import re
        
        # Common patterns: "n=1234", "n 1234", "1234 patients", "1234 participants"
        patterns = [
            r'\bn\s*[=:]\s*(\d+)',
            r'\b(\d+)\s+patients',
            r'\b(\d+)\s+participants',
            r'\b(\d+)\s+subjects'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None
    
    def _extract_epv(self, text: str) -> Optional[float]:
        """Extract Events Per Variable (EPV) from text"""
        import re
        
        patterns = [
            r'epv\s*[=:]\s*(\d+\.?\d*)',
            r'events\s+per\s+variable\s*[=:]\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s+events\s+per\s+variable'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        
        return None
    
    def _calculate_overall_risk(self, assessment: Dict) -> str:
        """
        Calculate overall PROBAST risk level
        
        Rules:
        - All 4 domains = Low → Overall = Low
        - 3 Low + 1 Moderate (with justification) → Overall = Low
        - Any High → Overall = High
        - Otherwise → Overall = Moderate
        """
        domains = [
            assessment.get("domain_1_participants", "Unclear"),
            assessment.get("domain_2_predictors", "Unclear"),
            assessment.get("domain_3_outcome", "Unclear"),
            assessment.get("domain_4_analysis", "Unclear")
        ]
        
        # Count risk levels
        low_count = domains.count(PROBASTRiskLevel.LOW.value)
        moderate_count = domains.count(PROBASTRiskLevel.MODERATE.value)
        high_count = domains.count(PROBASTRiskLevel.HIGH.value)
        
        # Any high risk = overall high
        if high_count > 0:
            return PROBASTRiskLevel.HIGH.value
        
        # All low = overall low
        if low_count == 4:
            return PROBASTRiskLevel.LOW.value
        
        # 3 low + 1 moderate = low (with justification)
        if low_count == 3 and moderate_count == 1:
            # Check if justification exists
            justification = assessment.get("justification", "")
            if justification:
                return PROBASTRiskLevel.LOW.value
            return PROBASTRiskLevel.MODERATE.value
        
        # Otherwise moderate
        return PROBASTRiskLevel.MODERATE.value
    
    def is_usable_for_model(self, assessment: Dict) -> bool:
        """
        Determine if article can be used in model based on PROBAST assessment
        
        Only articles with:
        - All 4 domains = Low Risk
        - OR 3 domains Low + 1 Moderate (with justification)
        """
        overall_risk = assessment.get("overall_risk", "Unclear")
        return overall_risk == PROBASTRiskLevel.LOW.value


if __name__ == "__main__":
    # Test assessment
    assessor = PROBASTAssessment()
    
    test_article = {
        "title": "Predictors of Total Knee Replacement in Knee Osteoarthritis: A Prospective Cohort Study",
        "abstract": "We conducted a prospective cohort study of 500 patients with knee osteoarthritis. Baseline predictors including age, BMI, WOMAC scores, and KL grades were measured. Outcomes were total knee replacement (TKR) at 5 years. Multivariable Cox regression was used with internal validation via bootstrap. EPV was 18.5.",
        "study_type": "Cohort Study"
    }
    
    assessment = assessor.assess_article(test_article)
    print(json.dumps(assessment, indent=2))
    print(f"\nUsable for model: {assessor.is_usable_for_model(assessment)}")
