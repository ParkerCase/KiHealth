#!/usr/bin/env python3
"""
Migrate articles from file storage to Google Sheets.
This will help move yesterday's articles that were saved to files into Google Sheets.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.file_storage import FileStorage
from scripts.google_sheets_storage import GoogleSheetsStorage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_articles():
    """Migrate all articles from file storage to Google Sheets"""
    
    # Check if Google Sheets credentials are available
    if not all([
        os.getenv('GOOGLE_SHEET_ID'),
        os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
        os.getenv('GOOGLE_PRIVATE_KEY')
    ]):
        logger.error("Google Sheets credentials not found!")
        logger.error("Set GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_EMAIL, and GOOGLE_PRIVATE_KEY")
        return
    
    file_storage = FileStorage()
    sheets_storage = GoogleSheetsStorage()
    
    # Get all articles from file storage
    logger.info("Loading articles from file storage...")
    articles_dir = Path('data/articles')
    
    if not articles_dir.exists():
        logger.warning("No articles directory found - nothing to migrate")
        return
    
    # Find all JSON files
    json_files = list(articles_dir.rglob('*.json'))
    
    # Filter out index.json
    article_files = [f for f in json_files if f.name != 'index.json']
    
    logger.info(f"Found {len(article_files)} article files to migrate")
    
    if len(article_files) == 0:
        logger.info("No articles to migrate")
        return
    
    success_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, article_file in enumerate(article_files, 1):
        try:
            # Load article from file
            with open(article_file, 'r') as f:
                article_data = json.load(f)
            
            pmid = article_data.get('pmid')
            if not pmid:
                logger.warning(f"Skipping file {article_file.name} - no PMID")
                skipped_count += 1
                continue
            
            # Check if already in Google Sheets
            existing = sheets_storage.get_article_by_pmid(pmid)
            if existing:
                # Check if Google Sheets version has better data
                has_details = (
                    existing.get('title') and 
                    existing.get('title') != 'No title' and
                    existing.get('journal') and
                    existing.get('journal') != 'Unknown Journal'
                )
                
                if has_details:
                    logger.info(f"[{i}/{len(article_files)}] Article {pmid} already in Google Sheets with details, skipping")
                    skipped_count += 1
                    continue
            
            # Insert/update in Google Sheets
            logger.info(f"[{i}/{len(article_files)}] Migrating PMID {pmid}...")
            success = sheets_storage.insert_article(article_data)
            
            if success:
                success_count += 1
                logger.info(f"✅ Migrated PMID {pmid}")
            else:
                error_count += 1
                logger.error(f"❌ Failed to migrate PMID {pmid}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"❌ Error processing {article_file.name}: {e}")
    
    logger.info("=" * 80)
    logger.info("MIGRATION COMPLETE")
    logger.info(f"  ✅ Success: {success_count}")
    logger.info(f"  ⏭️  Skipped: {skipped_count}")
    logger.info(f"  ❌ Errors: {error_count}")
    logger.info(f"  📊 Total: {len(article_files)}")
    logger.info("=" * 80)


if __name__ == "__main__":
    migrate_articles()

