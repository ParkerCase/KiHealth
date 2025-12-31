#!/usr/bin/env python3
"""
Export sorted paywalled articles list to logs directory.
This script prioritizes file storage (more reliable) and exports a detailed,
sorted list of all paywalled articles from best to least valuable.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.file_storage import FileStorage
from scripts.google_sheets_storage import GoogleSheetsStorage, HybridStorage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_all_paywalled_articles(threshold: int = 0) -> List[Dict]:
    """
    Get all paywalled articles from file storage (primary) and Google Sheets (secondary)
    
    Args:
        threshold: Minimum relevance score (default 0 to get all)
    
    Returns:
        List of paywalled article dictionaries, sorted by relevance score
    """
    articles = []
    existing_pmids = set()
    
    # Primary: File storage (most reliable, no quota issues)
    try:
        file_storage = FileStorage(data_dir='data/articles')
        file_articles = file_storage.get_paywalled_articles(threshold=threshold)
        articles.extend(file_articles)
        existing_pmids = {str(a.get('pmid', '')) for a in file_articles if a.get('pmid')}
        logger.info(f"✅ Found {len(file_articles)} paywalled articles in file storage")
    except Exception as e:
        logger.warning(f"Error getting articles from file storage: {e}")
    
    # Secondary: Google Sheets (may hit quota, but try anyway)
    try:
        # Check if Google Sheets credentials are available
        if os.getenv('GOOGLE_SHEET_ID') and os.getenv('GOOGLE_PRIVATE_KEY'):
            sheets_storage = GoogleSheetsStorage()
            sheets_articles = sheets_storage.get_paywalled_articles(threshold=threshold)
            
            # Merge, avoiding duplicates by PMID
            for article in sheets_articles:
                pmid = str(article.get('pmid', ''))
                if pmid and pmid not in existing_pmids:
                    articles.append(article)
                    existing_pmids.add(pmid)
            
            logger.info(f"✅ Found {len(sheets_articles)} paywalled articles in Google Sheets (added {len(articles) - len(file_articles)} new)")
        else:
            logger.info("⚠️  Google Sheets credentials not available, using file storage only")
    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'quota' in error_str.lower():
            logger.warning(f"⚠️  Google Sheets quota exceeded, using file storage only")
        else:
            logger.warning(f"⚠️  Error getting articles from Google Sheets: {e}")
    
    # Sort by relevance score (highest first)
    articles_sorted = sorted(
        articles,
        key=lambda x: (
            float(x.get('relevance_score', 0)) if x.get('relevance_score') else 0,
            x.get('title', '')  # Secondary sort by title for consistency
        ),
        reverse=True
    )
    
    logger.info(f"📊 Total unique paywalled articles: {len(articles_sorted)}")
    return articles_sorted


def export_to_logs(articles: List[Dict], output_dir: str = 'logs') -> Path:
    """
    Export sorted paywalled articles to a detailed log file
    
    Args:
        articles: List of article dictionaries (already sorted)
        output_dir: Directory to save log file
    
    Returns:
        Path to the created log file
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    log_file = output_path / 'paywalled_articles_sorted.log'
    
    lines = []
    lines.append("=" * 100)
    lines.append("PAYWALLED ARTICLES - SORTED BY RELEVANCE (BEST TO LEAST VALUABLE)")
    lines.append("=" * 100)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Articles: {len(articles)}")
    lines.append("")
    lines.append("=" * 100)
    lines.append("")
    
    # Summary statistics
    if articles:
        scores = [float(a.get('relevance_score', 0)) for a in articles if a.get('relevance_score')]
        if scores:
            lines.append("SUMMARY STATISTICS:")
            lines.append(f"  - Highest Score: {max(scores):.1f}/100")
            lines.append(f"  - Lowest Score: {min(scores):.1f}/100")
            lines.append(f"  - Average Score: {sum(scores)/len(scores):.1f}/100")
            lines.append(f"  - Articles with Score ≥ 70: {sum(1 for s in scores if s >= 70)}")
            lines.append(f"  - Articles with Score ≥ 50: {sum(1 for s in scores if s >= 50)}")
            lines.append(f"  - Articles with Score ≥ 30: {sum(1 for s in scores if s >= 30)}")
            lines.append("")
    
    lines.append("=" * 100)
    lines.append("DETAILED LIST (Sorted by Relevance Score - Highest First)")
    lines.append("=" * 100)
    lines.append("")
    
    # Detailed list
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'No title')
        pmid = article.get('pmid', 'N/A')
        score = article.get('relevance_score', 0)
        doi = article.get('doi', '')
        journal = article.get('journal', 'Unknown Journal')
        authors = article.get('authors', '')
        pub_date = article.get('publication_date', '')
        abstract = article.get('abstract', '')
        factors = article.get('predictive_factors', [])
        
        # Format score
        try:
            score_float = float(score) if score else 0.0
            score_str = f"{score_float:.1f}"
        except (ValueError, TypeError):
            score_str = str(score) if score else "0.0"
        
        lines.append(f"\n{'=' * 100}")
        lines.append(f"#{i} - RELEVANCE SCORE: {score_str}/100")
        lines.append(f"{'=' * 100}")
        lines.append(f"Title: {title}")
        lines.append(f"Journal: {journal}")
        lines.append(f"PMID: {pmid}")
        
        if doi:
            lines.append(f"DOI: {doi}")
            lines.append(f"DOI Link: https://doi.org/{doi}")
        
        lines.append(f"PubMed Link: https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
        
        if authors:
            # Truncate long author lists
            authors_str = authors if len(authors) <= 200 else authors[:200] + "..."
            lines.append(f"Authors: {authors_str}")
        
        if pub_date:
            lines.append(f"Publication Date: {pub_date}")
        
        # Predictive factors
        if factors and isinstance(factors, list):
            factor_names = []
            for f in factors:
                if isinstance(f, dict):
                    factor_name = f.get('factor', '')
                    if factor_name:
                        factor_names.append(factor_name)
                elif isinstance(f, str):
                    factor_names.append(f)
            
            if factor_names:
                lines.append(f"Predictive Factors ({len(factor_names)}): {', '.join(factor_names[:10])}")
                if len(factor_names) > 10:
                    lines.append(f"  ... and {len(factor_names) - 10} more")
        
        # Abstract (truncated)
        if abstract:
            abstract_short = abstract[:500] + "..." if len(abstract) > 500 else abstract
            lines.append(f"\nAbstract Preview:")
            lines.append(f"  {abstract_short}")
        
        lines.append("")
    
    # Write to file
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    logger.info(f"✅ Exported sorted paywalled articles list to: {log_file}")
    logger.info(f"   Total articles: {len(articles)}")
    
    return log_file


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Export sorted paywalled articles to logs')
    parser.add_argument(
        '--threshold',
        type=int,
        default=0,
        help='Minimum relevance score (default: 0 to show all paywalled articles)'
    )
    parser.add_argument(
        '--output-dir',
        default='logs',
        help='Output directory for log file (default: logs)'
    )
    
    args = parser.parse_args()
    
    logger.info("Starting paywalled articles export to logs...")
    logger.info(f"Relevance threshold: {args.threshold}")
    
    # Get all paywalled articles
    articles = get_all_paywalled_articles(threshold=args.threshold)
    
    if not articles:
        logger.warning("⚠️  No paywalled articles found!")
        return
    
    # Export to logs
    log_file = export_to_logs(articles, output_dir=args.output_dir)
    
    logger.info(f"✅ Export complete!")
    logger.info(f"   Log file: {log_file}")
    logger.info(f"   Articles exported: {len(articles)}")
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("EXPORT SUMMARY")
    print("=" * 80)
    print(f"✅ Exported {len(articles)} paywalled articles to: {log_file}")
    
    if articles:
        scores = [float(a.get('relevance_score', 0)) for a in articles if a.get('relevance_score')]
        if scores:
            print(f"\nScore Distribution:")
            print(f"  - Highest: {max(scores):.1f}/100")
            print(f"  - Lowest: {min(scores):.1f}/100")
            print(f"  - Average: {sum(scores)/len(scores):.1f}/100")
            print(f"  - High-relevance (≥70): {sum(1 for s in scores if s >= 70)}")
            print(f"  - Medium-relevance (50-69): {sum(1 for s in scores if 50 <= s < 70)}")
            print(f"  - Low-relevance (<50): {sum(1 for s in scores if s < 50)}")
    
    print("=" * 80)


if __name__ == "__main__":
    main()

