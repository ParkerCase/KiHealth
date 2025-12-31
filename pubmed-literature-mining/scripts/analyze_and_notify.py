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
        
        body = '## High-Priority Paywalled Articles\n\n'
        body += f'**{len(articles_sorted)} articles** identified with relevance score ≥ {self.relevance_threshold}:\n\n'
        
        for i, article in enumerate(articles_sorted[:20], 1):  # Top 20
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
            paywalled = self.get_paywalled_articles(threshold=self.relevance_threshold)
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
            paywalled = self.get_paywalled_articles(threshold=self.relevance_threshold)
            return f"""# PubMed Daily Summary - {datetime.now().strftime("%Y-%m-%d")}

## Overview

- **High-Relevance Articles:** {len(articles)} (score ≥ {self.relevance_threshold})
- **Paywalled Articles:** {len(paywalled)}

*Note: Enhanced flagging analysis unavailable. Check logs for details.*
"""
    
    def run(self):
        """Main execution method"""
        logger.info("Starting analysis and notification")
        
        # Get paywalled articles
        paywalled_articles = self.get_paywalled_articles(threshold=self.relevance_threshold)
        logger.info(f"Found {len(paywalled_articles)} paywalled articles")
        
        # Detect factor patterns
        factor_patterns = self.detect_factor_patterns(threshold=5)
        logger.info(f"Found {len(factor_patterns)} significant factor patterns")
        
        # Create notifications
        if paywalled_articles:
            self.create_paywalled_alert(paywalled_articles)
        
        if factor_patterns:
            self.create_factor_pattern_alert(factor_patterns)
        
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

