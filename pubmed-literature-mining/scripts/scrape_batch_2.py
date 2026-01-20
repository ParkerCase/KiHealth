#!/usr/bin/env python3
"""
Scrape Batch 2: 5,000 New PubMed Articles
==========================================
Scrapes 5,000 NEW articles avoiding duplicates from batch 1.

CRITICAL: Checks existing database and JSON files to avoid duplicates.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Set, List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.literature_database import LiteratureDatabase
from scripts.pubmed_scraper import PubMedScraper
from scripts.probast_assessment import PROBASTAssessment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_existing_pmids() -> Set[str]:
    """Get all existing PMIDs from database and JSON files"""
    existing_pmids = set()
    
    # 1. Get from SQLite database
    try:
        db = LiteratureDatabase()
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT pmid FROM papers WHERE pmid IS NOT NULL')
        db_pmids = {row[0] for row in cursor.fetchall()}
        existing_pmids.update(db_pmids)
        conn.close()
        logger.info(f"Found {len(db_pmids)} PMIDs in database")
    except Exception as e:
        logger.warning(f"Error reading database: {e}")
    
    # 2. Get from JSON files
    try:
        articles_dir = Path(__file__).parent.parent / "data" / "articles"
        if articles_dir.exists():
            json_files = list(articles_dir.rglob("*.json"))
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        article = json.load(f)
                        if 'pmid' in article and article['pmid']:
                            existing_pmids.add(str(article['pmid']))
                except Exception as e:
                    continue
            logger.info(f"Found {len([f for f in json_files])} JSON files")
    except Exception as e:
        logger.warning(f"Error reading JSON files: {e}")
    
    logger.info(f"Total existing PMIDs: {len(existing_pmids)}")
    return existing_pmids


def scrape_new_articles(target_count: int = 5000) -> Dict:
    """
    Scrape new articles avoiding duplicates
    
    Args:
        target_count: Target number of new articles to scrape
    
    Returns:
        Dictionary with scraping results
    """
    print("=" * 80)
    print("BATCH 2: SCRAPING 5,000 NEW ARTICLES")
    print("=" * 80)
    
    # Get existing PMIDs
    print("\n1. CHECKING EXISTING ARTICLES...")
    existing_pmids = get_existing_pmids()
    print(f"   ✓ Found {len(existing_pmids)} existing articles in database")
    
    # Initialize scraper
    print("\n2. INITIALIZING SCRAPER...")
    scraper = PubMedScraper()
    probast = PROBASTAssessment()
    database = LiteratureDatabase()
    
    # Set max articles (will need to scrape more to account for duplicates and filtering)
    # Target: 5,000 new articles after PROBAST filtering
    # Use multiple search strategies to find NEW articles (not duplicates)
    scraper.max_articles = target_count * 3  # Scrape extra to account for duplicates
    
    print(f"   Target: {target_count} new articles")
    print(f"   Will scrape: {scraper.max_articles} articles (accounting for duplicates/filtering)")
    print(f"   Strategy: Multiple queries to find NEW articles")
    
    # Run scraper
    print("\n3. SCRAPING ARTICLES...")
    print("   This may take 30-60 minutes...")
    
    new_articles_count = 0
    skipped_duplicates = 0
    processed_count = 0
    
    try:
        # Use multiple search queries to find NEW articles
        # The comprehensive search finds mostly duplicates, so we'll use different strategies
        print("\n" + "="*80)
        print("STARTING MULTI-QUERY SEARCH")
        print("="*80)
        logger.info("Starting scrape...")
        logger.info(f"Scraper will check for duplicates against {len(existing_pmids)} existing PMIDs")
        
        # Multiple search queries designed to find NEW articles
        # These are broader than comprehensive search to find articles we don't have
        search_queries = [
            # Query 1: Broader TKR/TKA search (no prediction requirement)
            '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND ("total knee replacement"[Title/Abstract] OR "total knee arthroplasty"[Title/Abstract] OR TKR[Title/Abstract] OR TKA[Title/Abstract] OR "knee replacement"[Title/Abstract] OR "knee arthroplasty"[Title/Abstract]) AND (English[Language]) AND (Humans[Mesh])',
            
            # Query 2: Progression-focused (broader than comprehensive)
            '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (progression[Title/Abstract] OR "disease progression"[Title/Abstract] OR "structural progression"[Title/Abstract] OR "radiographic progression"[Title/Abstract] OR "symptom progression"[Title/Abstract]) AND (English[Language]) AND (Humans[Mesh])',
            
            # Query 3: Risk factors and predictors (broader)
            '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (predictor[Title/Abstract] OR "risk factor"[Title/Abstract] OR "prognostic factor"[Title/Abstract] OR "biomarker"[Title/Abstract] OR "clinical factor"[Title/Abstract]) AND (English[Language]) AND (Humans[Mesh])',
            
            # Query 4: Outcomes and prognosis
            '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (outcome[Title/Abstract] OR prognosis[Title/Abstract] OR "clinical outcome"[Title/Abstract] OR "patient outcome"[Title/Abstract] OR "surgical outcome"[Title/Abstract]) AND (English[Language]) AND (Humans[Mesh])',
            
            # Query 5: Very broad - just knee OA (to catch anything we missed)
            '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (English[Language]) AND (Humans[Mesh]) AND ("cohort study"[Publication Type] OR "prospective"[Title/Abstract] OR "retrospective"[Title/Abstract] OR "longitudinal"[Title/Abstract])',
        ]
        
        total_processed = 0
        for i, query in enumerate(search_queries):
            # Check if we've reached target
            new_existing_pmids = get_existing_pmids()
            new_count = len(new_existing_pmids) - len(existing_pmids)
            
            if new_count >= target_count:
                print(f"\n✅ Target reached! Found {new_count} new articles (target: {target_count})")
                logger.info(f"Target reached! Stopping queries.")
                break
            
            print(f"\n{'='*80}")
            print(f"QUERY {i+1}/{len(search_queries)}")
            print(f"{'='*80}")
            print(f"Query: {query[:100]}...")
            logger.info(f"Running query {i+1}/{len(search_queries)}: {query[:80]}...")
            
            # Get PMIDs from this query
            pmids = scraper.search_pubmed(query, max_results=5000, date_range_years=15)  # 15 years to find more
            
            if not pmids:
                logger.warning(f"No articles found with query {i+1}")
                print(f"   ⚠️  No articles found")
                continue
            
            print(f"   Found: {len(pmids)} PMIDs")
            logger.info(f"Found {len(pmids)} PMIDs, processing...")
            
            # Filter out known duplicates before processing (faster)
            new_pmids = [p for p in pmids if str(p) not in existing_pmids]
            print(f"   New (not in database): {len(new_pmids)} PMIDs")
            print(f"   Duplicates (skipping): {len(pmids) - len(new_pmids)} PMIDs")
            
            if not new_pmids:
                print(f"   ⚠️  All articles from this query are duplicates")
                continue
            
            # Process each NEW PMID
            processed_this_query = 0
            for j, pmid in enumerate(new_pmids):
                # Check progress periodically
                if j % 50 == 0 and j > 0:
                    new_existing_pmids = get_existing_pmids()
                    new_count = len(new_existing_pmids) - len(existing_pmids)
                    print(f"   Progress: {new_count} new articles (target: {target_count}), processed {j}/{len(new_pmids)} from this query")
                    
                    if new_count >= target_count:
                        print(f"   ✅ Target reached! Stopping processing.")
                        logger.info(f"Target reached! Stopping processing.")
                        break
                
                try:
                    # Process article (scraper checks for duplicates internally as backup)
                    if scraper.process_article(pmid):
                        processed_count += 1
                        processed_this_query += 1
                        total_processed += 1
                except Exception as e:
                    logger.error(f"Error processing {pmid}: {e}")
            
            # Check final count after this query
            new_existing_pmids = get_existing_pmids()
            new_count = len(new_existing_pmids) - len(existing_pmids)
            print(f"   ✅ Query {i+1} complete: {new_count} new articles total (target: {target_count})")
            print(f"   Processed from this query: {processed_this_query} new articles")
            logger.info(f"After query {i+1}: {new_count} new articles (target: {target_count})")
        
        # Final check
        new_existing_pmids = get_existing_pmids()
        new_count = len(new_existing_pmids) - len(existing_pmids)
        logger.info(f"Scraping completed. Total new articles: {new_count}, Total processed: {total_processed}")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        new_existing_pmids = get_existing_pmids()
        new_count = len(new_existing_pmids) - len(existing_pmids)
        return {
            "success": True,
            "interrupted": True,
            "new_articles": new_count,
            "skipped_duplicates": skipped_duplicates
        }
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        new_existing_pmids = get_existing_pmids()
        new_count = len(new_existing_pmids) - len(existing_pmids)
        return {
            "success": False,
            "error": str(e),
            "new_articles": new_count,
            "skipped_duplicates": skipped_duplicates
        }
    
    # Check how many new articles were actually added
    print("\n4. VERIFYING NEW ARTICLES...")
    new_existing_pmids = get_existing_pmids()
    new_count = len(new_existing_pmids) - len(existing_pmids)
    
    print(f"   ✓ New articles added: {new_count}")
    print(f"   ✓ Total articles now: {len(new_existing_pmids)}")
    
    # Get statistics on new articles
    import sqlite3
    conn = sqlite3.connect(database.db_path)
    cursor = conn.cursor()
    
    # Count by PROBAST risk
    cursor.execute('''
        SELECT probast_risk, COUNT(*) 
        FROM papers 
        WHERE date_added > datetime('now', '-1 day')
        GROUP BY probast_risk
    ''')
    probast_dist = dict(cursor.fetchall())
    
    # Count usable (Low/Moderate Risk with relevance >= 40)
    cursor.execute('''
        SELECT COUNT(*) 
        FROM papers 
        WHERE (probast_risk = 'Low' OR 
               (probast_risk = 'Moderate' AND 
                (SELECT COUNT(*) FROM (
                    SELECT 
                        CASE WHEN probast_domain_1 = 'Low' THEN 1 ELSE 0 END +
                        CASE WHEN probast_domain_2 = 'Low' THEN 1 ELSE 0 END +
                        CASE WHEN probast_domain_3 = 'Low' THEN 1 ELSE 0 END +
                        CASE WHEN probast_domain_4 = 'Low' THEN 1 ELSE 0 END
                ) WHERE papers.pmid = papers.pmid) >= 1))
        AND relevance_score >= 40
        AND date_added > datetime('now', '-1 day')
    ''')
    usable_count = cursor.fetchone()[0]
    
    conn.close()
    
    result = {
        "success": True,
        "target_count": target_count,
        "new_articles_added": new_count,
        "total_articles": len(new_existing_pmids),
        "probast_distribution": probast_dist,
        "usable_articles": usable_count,
        "timestamp": datetime.now().isoformat()
    }
    
    return result


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("BATCH 2 SCRAPING - STARTING")
    print("="*80)
    print(f"Target: 5,000 new articles")
    print(f"Current database: Checking...")
    
    # Check current count
    initial_pmids = get_existing_pmids()
    print(f"Starting with: {len(initial_pmids)} existing articles\n")
    
    result = scrape_new_articles(target_count=5000)
    
    print("\n" + "=" * 80)
    print("SCRAPING SUMMARY")
    print("=" * 80)
    print(f"\nNew articles added: {result.get('new_articles_added', 0)}")
    print(f"Total articles: {result.get('total_articles', 0)}")
    print(f"Usable articles (PROBAST + relevance ≥40): {result.get('usable_articles', 0)}")
    print(f"\nPROBAST Distribution:")
    for risk, count in result.get('probast_distribution', {}).items():
        print(f"  {risk}: {count}")
    
    # Save report
    report_path = Path(__file__).parent.parent / "data" / f"batch_2_scraping_report_{datetime.now().strftime('%Y%m%d')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nReport saved: {report_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
