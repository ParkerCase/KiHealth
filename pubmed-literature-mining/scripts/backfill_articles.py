#!/usr/bin/env python3
"""
Backfill script to re-process articles that are missing details.
This will fetch full details for articles that were stored without proper information.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.google_sheets_storage import get_storage_client
from scripts.pubmed_scraper import PubMedScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_articles_missing_details(storage, threshold: int = 70):
    """
    Find articles that are missing details (title, journal, etc.)
    
    Args:
        storage: Storage client
        threshold: Minimum relevance score to consider
        
    Returns:
        List of PMIDs that need backfilling
    """
    missing_details = []
    
    try:
        # Get all paywalled articles above threshold
        paywalled = storage.get_paywalled_articles(threshold=threshold)
        
        for article in paywalled:
            pmid = article.get('pmid')
            title = article.get('title', '')
            journal = article.get('journal', '')
            
            # Check if details are missing
            if not title or title == 'No title' or not journal or journal == 'Unknown Journal':
                missing_details.append(pmid)
                logger.info(f"Found article {pmid} missing details: title='{title}', journal='{journal}'")
    
    except Exception as e:
        logger.error(f"Error finding articles with missing details: {e}")
    
    return missing_details


def backfill_articles(pmids: list = None, threshold: int = 70):
    """
    Backfill articles with missing details
    
    Args:
        pmids: List of PMIDs to backfill (if None, finds all missing)
        threshold: Minimum relevance score
    """
    storage = get_storage_client()
    scraper = PubMedScraper()
    
    # If no PMIDs provided, find articles missing details
    if pmids is None:
        logger.info("Finding articles with missing details...")
        pmids = find_articles_missing_details(storage, threshold)
        logger.info(f"Found {len(pmids)} articles with missing details")
    
    if not pmids:
        logger.info("No articles need backfilling!")
        return
    
    logger.info(f"Starting backfill for {len(pmids)} articles...")
    
    success_count = 0
    error_count = 0
    
    for i, pmid in enumerate(pmids, 1):
        logger.info(f"[{i}/{len(pmids)}] Processing PMID {pmid}...")
        try:
            # Process article (will update if exists, create if not)
            success = scraper.process_article(pmid)
            if success:
                success_count += 1
                logger.info(f"✅ Successfully backfilled PMID {pmid}")
            else:
                error_count += 1
                logger.warning(f"⚠️ Failed to backfill PMID {pmid}")
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Error processing PMID {pmid}: {e}")
    
    logger.info("=" * 80)
    logger.info(f"Backfill complete!")
    logger.info(f"  ✅ Success: {success_count}")
    logger.info(f"  ❌ Errors: {error_count}")
    logger.info(f"  📊 Total: {len(pmids)}")
    logger.info("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill articles with missing details')
    parser.add_argument(
        '--pmids',
        nargs='+',
        help='Specific PMIDs to backfill (space-separated)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=70,
        help='Minimum relevance score for paywalled articles (default: 70)'
    )
    parser.add_argument(
        '--all-missing',
        action='store_true',
        help='Backfill all articles with missing details'
    )
    
    args = parser.parse_args()
    
    if args.pmids:
        backfill_articles(pmids=args.pmids, threshold=args.threshold)
    elif args.all_missing:
        backfill_articles(threshold=args.threshold)
    else:
        parser.print_help()
        print("\nUse --all-missing to backfill all articles with missing details")
        print("Or provide specific PMIDs with --pmids")

