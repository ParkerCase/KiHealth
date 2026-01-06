#!/usr/bin/env python3
"""
Analysis and Notification System
Analyzes processed articles and creates GitHub notifications (issues, commits, annotations).
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.google_sheets_storage import get_storage_client
from scripts.article_flagging import ArticleFlaggingFramework
from scripts.review_manager import ReviewManager, ReviewStatus

load_dotenv()

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analyze_and_notify.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NotificationSystem:
    """Handles GitHub-based notifications"""
    
    def __init__(self):
        self.storage = get_storage_client()  # Google Sheets if available, else file storage
        self.relevance_threshold = int(os.getenv('RELEVANCE_THRESHOLD', '70'))
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('GITHUB_REPO_OWNER')
        self.repo_name = os.getenv('GITHUB_REPO_NAME')
        self.flagging_framework = ArticleFlaggingFramework()  # New flagging framework
        self.review_manager = ReviewManager()  # Review and approval workflow
    
    def get_paywalled_articles(self, threshold: int = 0) -> List[Dict]:
        """Get paywalled articles above relevance threshold
        
        Default threshold is 0 to show all paywalled articles.
        Use threshold=70 to show only high-relevance paywalled articles.
        """
        return self.storage.get_paywalled_articles(threshold=threshold)
    
    def detect_factor_patterns(self, threshold: int = 5) -> Dict[str, List[Dict]]:
        """
        Detect when 5+ articles mention the same predictive factor
        
        Args:
            threshold: Minimum number of articles mentioning a factor
            
        Returns:
            Dictionary mapping factor names to lists of articles
        """
        # Get all high-relevance articles
        articles = self.storage.get_high_relevance_articles(threshold=self.relevance_threshold)
        
        factor_articles = defaultdict(list)
        
        for article in articles:
            factors = article.get('predictive_factors', [])
            if not isinstance(factors, list):
                continue
            
            for factor_data in factors:
                if isinstance(factor_data, dict):
                    factor_name = factor_data.get('factor', '').lower()
                    if factor_name:
                        factor_articles[factor_name].append(article)
        
        # Filter to factors mentioned in threshold+ articles
        significant_factors = {
            factor: articles
            for factor, articles in factor_articles.items()
            if len(articles) >= threshold
        }
        
        return significant_factors
    
    def detect_potential_new_parameters(self, threshold: int = 5) -> Dict[str, List[Dict]]:
        """
        Detect factors that could be new model parameters
        
        Compares extracted factors against current model parameters and flags
        novel factors that appear in multiple high-quality studies.
        
        Current model parameters:
        - Age, Sex, BMI, Race, Cohort
        - WOMAC Total Right/Left
        - KL Grade Right/Left
        - Family History
        - Walking Distance (400m walk time)
        
        Args:
            threshold: Minimum number of articles mentioning a factor
            
        Returns:
            Dictionary mapping potential new parameter names to lists of articles
        """
        # Current model parameters (normalized for comparison)
        current_params = {
            'age', 'sex', 'gender', 'bmi', 'body mass index', 'race', 'ethnicity',
            'cohort', 'womac', 'kellgren-lawrence', 'kl grade', 'kl score',
            'family history', 'walking distance', '400m walk', 'walk time',
            'knee replacement', 'tkr', 'tka', 'arthroplasty'
        }
        
        # Get all high-relevance articles
        articles = self.storage.get_high_relevance_articles(threshold=self.relevance_threshold)
        
        potential_params = defaultdict(list)
        
        for article in articles:
            factors = article.get('predictive_factors', [])
            if not isinstance(factors, list):
                continue
            
            for factor_data in factors:
                if isinstance(factor_data, dict):
                    factor_name = factor_data.get('factor', '').lower().strip()
                    if not factor_name:
                        continue
                    
                    # Check if this factor is already in the model
                    is_current_param = any(
                        current_param in factor_name or factor_name in current_param
                        for current_param in current_params
                    )
                    
                    # If it's a new factor and appears in high-quality studies, flag it
                    if not is_current_param:
                        # Check if it's a statistically significant predictor
                        effect_size = factor_data.get('effect_size', '')
                        significance = factor_data.get('significance', '')
                        
                        # Only include if there's statistical evidence
                        has_evidence = (
                            'p' in significance.lower() or
                            'or' in effect_size.lower() or
                            'hr' in effect_size.lower() or
                            'auc' in effect_size.lower() or
                            'odds ratio' in effect_size.lower()
                        )
                        
                        if has_evidence:
                            potential_params[factor_name].append(article)
        
        # Filter to factors mentioned in threshold+ articles
        significant_new_params = {
            factor: articles
            for factor, articles in potential_params.items()
            if len(articles) >= threshold
        }
        
        return significant_new_params
    
    def create_github_issue(self, title: str, body: str, labels: List[str] = None) -> bool:
        """
        Create a GitHub issue
        
        Args:
            title: Issue title
            body: Issue body (markdown)
            labels: List of label names
            
        Returns:
            True if successful
        """
        if not all([self.github_token, self.repo_owner, self.repo_name]):
            logger.warning("GitHub credentials not configured, skipping issue creation")
            # Print issue content for manual creation
            print("\n" + "="*80)
            print("GITHUB ISSUE (Manual Creation Required)")
            print("="*80)
            print(f"Title: {title}")
            print(f"\nBody:\n{body}")
            if labels:
                print(f"\nLabels: {', '.join(labels)}")
            print("="*80 + "\n")
            return False
        
        try:
            import requests
            
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'title': title,
                'body': body,
                'labels': labels or []
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            issue_data = response.json()
            logger.info(f"Created GitHub issue #{issue_data['number']}: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return False
    
    def create_paywalled_alert(self, articles: List[Dict]) -> bool:
        """Create GitHub issue for paywalled articles"""
        if len(articles) < 5:
            logger.info(f"Only {len(articles)} paywalled articles, skipping alert")
            return False
        
        # Sort by relevance score
        articles_sorted = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Filter to high-relevance for the alert (but we found all paywalled articles)
        high_relevance_paywalled = [a for a in articles_sorted if a.get('relevance_score', 0) >= self.relevance_threshold]
        
        body = '## Paywalled Articles\n\n'
        body += f'**{len(articles_sorted)} total paywalled articles** found.\n'
        body += f'**{len(high_relevance_paywalled)} high-relevance articles** (score ≥ {self.relevance_threshold}):\n\n'
        
        # Show top 20 high-relevance paywalled articles
        for i, article in enumerate(high_relevance_paywalled[:20], 1):  # Top 20
            body += f'### {i}. {article.get("title", "No title")}\n'
            body += f'- **Journal:** {article.get("journal", "Unknown")}\n'
            body += f'- **Relevance Score:** {article.get("relevance_score", 0)}/100\n'
            
            doi = article.get("doi", "")
            if doi:
                body += f'- **DOI:** https://doi.org/{doi}\n'
            
            pmid = article.get("pmid", "")
            if pmid:
                body += f'- **PubMed:** https://pubmed.ncbi.nlm.nih.gov/{pmid}/\n'
            
            factors = article.get("predictive_factors", [])
            if factors and isinstance(factors, list):
                factor_names = [f.get("factor", "") for f in factors[:5] if isinstance(f, dict)]
                if factor_names:
                    body += f'- **Key Factors:** {", ".join(factor_names)}\n'
            
            abstract = article.get("abstract", "")
            if abstract:
                # Truncate long abstracts
                abstract_short = abstract[:500] + "..." if len(abstract) > 500 else abstract
                body += f'\n<details><summary>Abstract</summary>\n\n{abstract_short}\n\n</details>\n\n'
        
        body += '\n---\n\n'
        body += '**Action Required:** Download PDFs via institutional access\n\n'
        body += f'**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        
        title = f'📚 {len(articles_sorted)} High-Priority Paywalled Articles ({datetime.now().strftime("%Y-%m-%d")})'
        labels = ['pubmed-alert', 'paywalled-articles', 'action-required']
        
        return self.create_github_issue(title, body, labels)
    
    def create_factor_pattern_alert(self, factor_patterns: Dict[str, List[Dict]]) -> bool:
        """Create GitHub issue for significant factor patterns"""
        if not factor_patterns:
            return False
        
        body = '## Predictive Factor Pattern Detected\n\n'
        body += f'**{len(factor_patterns)} factors** mentioned in 5+ high-relevance articles:\n\n'
        
        # Sort by number of articles
        sorted_factors = sorted(
            factor_patterns.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for factor_name, articles in sorted_factors[:10]:  # Top 10 factors
            body += f'### {factor_name.title()}\n'
            body += f'**Mentioned in {len(articles)} articles:**\n\n'
            
            for article in articles[:5]:  # Top 5 articles per factor
                title = article.get("title", "No title")
                score = article.get("relevance_score", 0)
                pmid = article.get("pmid", "")
                
                body += f'- [{title}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) (Score: {score}/100)\n'
            
            body += '\n'
        
        body += '\n---\n\n'
        body += f'**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        
        title = f'🔍 Predictive Factor Patterns Detected ({datetime.now().strftime("%Y-%m-%d")})'
        labels = ['pubmed-alert', 'factor-patterns', 'analysis']
        
        return self.create_github_issue(title, body, labels)
    
    def create_new_parameter_alert(self, potential_params: Dict[str, List[Dict]]) -> bool:
        """Create GitHub issue for potential new model parameters"""
        if not potential_params:
            return False
        
        body = '## 🆕 Potential New Model Parameters Detected\n\n'
        body += '**⚠️ IMPORTANT:** These factors are NOT automatically added to the model. '
        body += 'They require manual review, validation, and PROBAST compliance verification before integration.\n\n'
        body += f'**{len(potential_params)} potential new parameters** identified in 5+ high-relevance articles:\n\n'
        
        # Sort by number of articles
        sorted_params = sorted(
            potential_params.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for param_name, articles in sorted_params[:15]:  # Top 15 potential parameters
            body += f'### {param_name.title()}\n'
            body += f'**Mentioned in {len(articles)} articles:**\n\n'
            
            # Show evidence from top articles
            for article in articles[:5]:  # Top 5 articles per parameter
                title = article.get("title", "No title")
                score = article.get("relevance_score", 0)
                pmid = article.get("pmid", "")
                
                # Extract factor details if available
                factors = article.get('predictive_factors', [])
                factor_details = None
                for f in factors:
                    if isinstance(f, dict) and f.get('factor', '').lower() == param_name:
                        factor_details = f
                        break
                
                body += f'- [{title}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) (Score: {score}/100)\n'
                if factor_details:
                    effect = factor_details.get('effect_size', '')
                    sig = factor_details.get('significance', '')
                    if effect or sig:
                        body += f'  - Evidence: {effect} {sig}\n'
            
            body += '\n'
        
        body += '\n---\n\n'
        body += '## Review Checklist\n\n'
        body += 'Before considering integration:\n'
        body += '- [ ] Verify factor is not already in model (check synonyms)\n'
        body += '- [ ] Confirm data availability in OAI or clinical practice\n'
        body += '- [ ] Verify statistical significance across multiple studies\n'
        body += '- [ ] Check EPV compliance (≥15 events per variable)\n'
        body += '- [ ] Assess clinical accessibility (routinely available)\n'
        body += '- [ ] Evaluate multicollinearity with existing predictors\n'
        body += '- [ ] Review PROBAST compliance impact\n'
        body += '- [ ] Test model performance with new parameter\n'
        body += '- [ ] Validate on external dataset\n\n'
        body += f'**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        
        title = f'🆕 Potential New Model Parameters ({datetime.now().strftime("%Y-%m-%d")})'
        labels = ['pubmed-alert', 'new-parameters', 'model-enhancement', 'requires-review']
        
        return self.create_github_issue(title, body, labels)
    
    def create_workflow_annotations(self, paywalled_articles: List[Dict], factor_patterns: Dict):
        """Create GitHub Actions workflow annotations"""
        if paywalled_articles:
            count = len(paywalled_articles)
            print(f"::notice title=Paywalled Articles::{count} high-priority articles require download")
            
            for article in paywalled_articles[:3]:  # Top 3
                title = article.get("title", "Unknown")[:50]
                score = article.get("relevance_score", 0)
                doi = article.get("doi", "")
                print(f"::notice title={title}::Relevance: {score}/100 - DOI: {doi}")
        
        if factor_patterns:
            print(f"::notice title=Factor Patterns::{len(factor_patterns)} factors detected in multiple articles")
    
    def generate_daily_summary(self) -> str:
        """Generate markdown summary of daily findings with flagging framework"""
        try:
            # Get all articles for flagging analysis
            all_articles = self.storage.get_all_articles()
            logger.info(f"Analyzing {len(all_articles)} articles for flagging")
            
            # Get flagging summary
            flagging_summary = self.flagging_framework.get_flagging_summary(all_articles)
            
            # Get prioritized review list
            prioritized = self.flagging_framework.get_review_priority_list(all_articles)
            
            # Get traditional metrics
            articles = self.storage.get_high_relevance_articles(threshold=self.relevance_threshold)
            # Get ALL paywalled articles (threshold=0), not just high-relevance ones
            paywalled = self.get_paywalled_articles(threshold=0)
            factor_patterns = self.detect_factor_patterns(threshold=5)
            
            summary = f"""# PubMed Daily Summary - {datetime.now().strftime("%Y-%m-%d")}

## Overview

- **Total Articles:** {len(all_articles)}
- **Flagged for Review:** {flagging_summary['flagged_count']} ({flagging_summary['flagging_rate']:.1f}%)
- **High-Relevance Articles:** {len(articles)} (score ≥ {self.relevance_threshold})
- **Paywalled Articles:** {len(paywalled)}
- **Factor Patterns Detected:** {len(factor_patterns)}

## Articles Flagged for Review

### Priority Breakdown

- **High Priority (Must Review):** {flagging_summary['priority_counts']['high_priority']}
- **Medium-High Priority (Should Review):** {flagging_summary['priority_counts']['medium_high_priority']}
- **Paywalled High-Value:** {flagging_summary['priority_counts']['paywalled_high_value']}
- **Recent High-Value:** {flagging_summary['priority_counts']['recent_high_value']}
- **Large Sample Studies:** {flagging_summary['priority_counts']['large_sample']}
- **Systematic Reviews:** {flagging_summary['priority_counts']['systematic_review']}
- **Novel Findings:** {flagging_summary['priority_counts']['novel_findings']}
- **Actionable Insights:** {flagging_summary['priority_counts']['actionable']}

### Top Priority Articles for Review

"""
            
            # Add top 20 prioritized articles
            for i, item in enumerate(prioritized[:20], 1):
                article = item['article']
                summary += f"{i}. **{article.get('title', 'No title')[:80]}**\n"
                summary += f"   - Score: {article.get('relevance_score', 0)}/100\n"
                summary += f"   - Flags: {', '.join(item['flags'])}\n"
                summary += f"   - Reason: {item['reason']}\n"
                summary += f"   - Access: {article.get('access_type', 'unknown')}\n"
                summary += f"   - [PubMed](https://pubmed.ncbi.nlm.nih.gov/{article.get('pmid', '')}/)\n\n"
            
            summary += "\n## Top Paywalled Articles\n\n"
            
            for i, article in enumerate(sorted(paywalled, key=lambda x: x.get('relevance_score', 0), reverse=True)[:10], 1):
                summary += f"{i}. **{article.get('title', 'No title')}** (Score: {article.get('relevance_score', 0)}/100)\n"
                summary += f"   - {article.get('journal', 'Unknown')}\n"
                summary += f"   - DOI: {article.get('doi', 'N/A')}\n\n"
            
            if factor_patterns:
                summary += "\n## Significant Factor Patterns\n\n"
                sorted_factors = sorted(factor_patterns.items(), key=lambda x: len(x[1]), reverse=True)
                for factor, articles_list in sorted_factors[:5]:
                    summary += f"- **{factor.title()}**: Mentioned in {len(articles_list)} articles\n"
            
            return summary
        except Exception as e:
            logger.error(f"Error generating enhanced summary: {e}", exc_info=True)
            # Fallback to basic summary
            articles = self.storage.get_high_relevance_articles(threshold=self.relevance_threshold)
            # Get ALL paywalled articles (threshold=0), not just high-relevance ones
            paywalled = self.get_paywalled_articles(threshold=0)
            return f"""# PubMed Daily Summary - {datetime.now().strftime("%Y-%m-%d")}

## Overview

- **High-Relevance Articles:** {len(articles)} (score ≥ {self.relevance_threshold})
- **Paywalled Articles:** {len(paywalled)} (all scores)

*Note: Enhanced flagging analysis unavailable. Check logs for details.*
"""
    
    def run(self):
        """Main execution method"""
        logger.info("Starting analysis and notification")
        
        # Get paywalled articles (use threshold=0 to show ALL paywalled articles)
        # The relevance_threshold is for high-relevance filtering, but we want all paywalled
        paywalled_articles = self.get_paywalled_articles(threshold=0)
        logger.info(f"Found {len(paywalled_articles)} paywalled articles (all scores)")
        
        # Detect factor patterns
        factor_patterns = self.detect_factor_patterns(threshold=5)
        logger.info(f"Found {len(factor_patterns)} significant factor patterns")
        
        # Detect potential new parameters (NEW)
        potential_params = self.detect_potential_new_parameters(threshold=5)
        logger.info(f"Found {len(potential_params)} potential new model parameters")
        
        # Create notifications
        if paywalled_articles:
            self.create_paywalled_alert(paywalled_articles)
        
        if factor_patterns:
            self.create_factor_pattern_alert(factor_patterns)
        
        # Create alert for potential new parameters (NEW)
        if potential_params:
            self.create_new_parameter_alert(potential_params)
            # Add to review queue for manual approval
            for param_name, articles in potential_params.items():
                # Create review item for each potential parameter
                review_data = {
                    'parameter_name': param_name,
                    'articles': articles[:10],  # Top 10 articles
                    'article_count': len(articles),
                    'pmid': articles[0].get('pmid', 'unknown') if articles else 'unknown',
                    'title': f"Potential New Parameter: {param_name}",
                    'relevance_score': max(a.get('relevance_score', 0) for a in articles) if articles else 0
                }
                self.review_manager.add_to_review_queue('new_parameter', review_data)
        
        # Add supporting evidence to review queue (articles that support current parameters)
        high_relevance_articles = self.storage.get_high_relevance_articles(threshold=self.relevance_threshold)
        for article in high_relevance_articles[:20]:  # Top 20 for review
            # Check if article supports current parameters
            factors = article.get('predictive_factors', [])
            if factors:
                review_data = {
                    'pmid': article.get('pmid', 'unknown'),
                    'title': article.get('title', 'No title'),
                    'relevance_score': article.get('relevance_score', 0),
                    'factors': factors,
                    'journal': article.get('journal', 'Unknown'),
                    'access_type': article.get('access_type', 'unknown')
                }
                self.review_manager.add_to_review_queue('supporting_evidence', review_data)
        
        # Create workflow annotations
        self.create_workflow_annotations(paywalled_articles, factor_patterns)
        
        # Generate daily summary
        try:
            summary = self.generate_daily_summary()
            os.makedirs('logs', exist_ok=True)
            with open('LATEST_FINDINGS.md', 'w') as f:
                f.write(summary)
            logger.info("Daily summary generated")
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            # Create minimal summary
            os.makedirs('logs', exist_ok=True)
            with open('LATEST_FINDINGS.md', 'w') as f:
                f.write(f"# PubMed Daily Summary - {datetime.now().strftime('%Y-%m-%d')}\n\nError generating summary. Check logs for details.\n")
        
        logger.info("Analysis and notification complete")


if __name__ == "__main__":
    notifier = NotificationSystem()
    notifier.run()

