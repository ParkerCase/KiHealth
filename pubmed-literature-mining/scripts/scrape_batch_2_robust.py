#!/usr/bin/env python3
"""
Robust Batch 2 Scraper - Continuous Operation
==============================================
Scrapes 5,000 NEW articles with robust error handling and progress tracking.
Designed to run continuously without stopping.
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Set, List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.literature_database import LiteratureDatabase
from scripts.pubmed_scraper import PubMedScraper
from scripts.probast_assessment import PROBASTAssessment

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_batch_2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_existing_pmids() -> Set[str]:
    """Get all existing PMIDs from database and JSON files"""
    existing_pmids = set()
    
    # 1. Get from SQLite database (PRIMARY SOURCE)
    # Use absolute path based on script location to avoid working directory issues
    try:
        script_dir = Path(__file__).parent.parent  # pubmed-literature-mining directory
        db_path = script_dir / "data" / "literature.db"
        
        # Ensure we have absolute path
        db_path = db_path.resolve()
        
        if not db_path.exists():
            logger.error(f"Database not found at {db_path}")
            # Try alternative locations
            alt_paths = [
                Path("pubmed-literature-mining/data/literature.db").resolve(),
                Path("data/literature.db").resolve(),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    db_path = alt_path
                    break
        
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all PMIDs from database
        cursor.execute('SELECT DISTINCT pmid FROM papers WHERE pmid IS NOT NULL')
        rows = cursor.fetchall()
        db_pmids = {str(row[0]) for row in rows if row[0] and str(row[0]).strip()}
        
        # If that didn't work, try simpler query
        if not db_pmids:
            cursor.execute('SELECT pmid FROM papers')
            rows = cursor.fetchall()
            db_pmids = {str(row[0]) for row in rows if row[0] and str(row[0]).strip()}
        
        existing_pmids.update(db_pmids)
        conn.close()
        logger.info(f"Found {len(db_pmids)} PMIDs in database at {db_path}")
    except Exception as e:
        logger.error(f"Error reading database: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. Get from JSON files (SECONDARY - for articles not yet in DB)
    try:
        articles_dir = Path(__file__).parent.parent / "data" / "articles"
        if articles_dir.exists():
            json_files = list(articles_dir.rglob("*.json"))
            json_count = 0
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        article = json.load(f)
                        if 'pmid' in article and article['pmid']:
                            existing_pmids.add(str(article['pmid']))
                            json_count += 1
                except Exception as e:
                    continue
            logger.info(f"Found {json_count} PMIDs in {len(json_files)} JSON files")
    except Exception as e:
        logger.warning(f"Error reading JSON files: {e}")
    
    logger.info(f"Total existing PMIDs: {len(existing_pmids)}")
    return existing_pmids


def save_progress(query_num: int, processed: int, new_count: int, target: int):
    """Save progress to file for recovery"""
    progress_file = Path(__file__).parent.parent / "data" / "scraping_progress.json"
    progress = {
        "query_num": query_num,
        "processed": processed,
        "new_count": new_count,
        "target": target,
        "timestamp": datetime.now().isoformat()
    }
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)


def scrape_new_articles_robust(target_count: int = 5000) -> Dict:
    """
    Robust scraper that runs continuously with error recovery
    """
    print("=" * 80)
    print("ROBUST BATCH 2 SCRAPING - CONTINUOUS OPERATION")
    print("=" * 80)
    
    # Get existing PMIDs
    print("\n1. CHECKING EXISTING ARTICLES...")
    existing_pmids = get_existing_pmids()
    initial_count = len(existing_pmids)
    
    # Also get initial database count for tracking
    try:
        script_dir = Path(__file__).parent.parent
        db_path = script_dir / "data" / "literature.db"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM papers')
        initial_db_count = cursor.fetchone()[0]
        conn.close()
    except:
        initial_db_count = 0
    
    print(f"   ✓ Found {initial_count} existing PMIDs")
    print(f"   ✓ Database currently has {initial_db_count} articles")
    print(f"   ✓ Goal: Add {target_count} NEW articles (target total: {initial_db_count + target_count})")
    
    # Initialize scraper
    print("\n2. INITIALIZING SCRAPER...")
    scraper = PubMedScraper()
    database = LiteratureDatabase()
    
    # Get database path for tracking
    script_dir = Path(__file__).parent.parent
    db_path = script_dir / "data" / "literature.db"
    
    # Search queries - BROADER QUERIES to find articles we haven't scraped yet
    # No date restrictions - we'll filter by relevance score later
    # These queries target different aspects to maximize coverage
    
    search_queries = [
        # Query 1: Basic knee OA + TKR/TKA (core topic - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND ("total knee replacement"[Title/Abstract] OR "total knee arthroplasty"[Title/Abstract] OR TKR[Title/Abstract] OR TKA[Title/Abstract] OR "knee replacement"[Title/Abstract] OR "knee arthroplasty"[Title/Abstract]) AND (English[Language])',
        
        # Query 2: Knee OA + progression (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (progression[Title/Abstract] OR "disease progression"[Title/Abstract] OR "structural progression"[Title/Abstract] OR "radiographic progression"[Title/Abstract]) AND (English[Language])',
        
        # Query 3: Knee OA + prediction/prognosis (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (prediction[Title/Abstract] OR prognostic[Title/Abstract] OR "predictive model"[Title/Abstract] OR "risk prediction"[Title/Abstract]) AND (English[Language])',
        
        # Query 4: Knee OA + risk factors (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND ("risk factor"[Title/Abstract] OR "predictor"[Title/Abstract] OR "prognostic factor"[Title/Abstract] OR "clinical factor"[Title/Abstract]) AND (English[Language])',
        
        # Query 5: Knee OA + outcome (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (outcome[Title/Abstract] OR "clinical outcome"[Title/Abstract] OR "surgical outcome"[Title/Abstract] OR "treatment outcome"[Title/Abstract]) AND (English[Language])',
        
        # Query 6: Knee OA + machine learning/AI (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND ("machine learning"[Title/Abstract] OR "artificial intelligence"[Title/Abstract] OR "deep learning"[Title/Abstract] OR "neural network"[Title/Abstract]) AND (English[Language])',
        
        # Query 7: Knee OA + cohort/registry (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (cohort[Title/Abstract] OR registry[Title/Abstract] OR "longitudinal"[Title/Abstract] OR "prospective"[Title/Abstract] OR "retrospective"[Title/Abstract]) AND (English[Language])',
        
        # Query 8: Knee OA + biomarker (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (biomarker[Title/Abstract] OR "biological marker"[Title/Abstract] OR serum[Title/Abstract] OR "blood marker"[Title/Abstract]) AND (English[Language])',
        
        # Query 9: Knee OA + imaging (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (imaging[Title/Abstract] OR "magnetic resonance"[Title/Abstract] OR MRI[Title/Abstract] OR "X-ray"[Title/Abstract] OR radiograph[Title/Abstract]) AND (English[Language])',
        
        # Query 10: Knee OA + validation (broader - no date restriction)
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (validation[Title/Abstract] OR "external validation"[Title/Abstract] OR "model validation"[Title/Abstract] OR "predictive model"[Title/Abstract]) AND (English[Language])',
        
        # Query 11: Recent articles only (2024-2025) - to catch newest
        f'("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (2024[PDAT]:2025[PDAT]) AND (English[Language])',
        
        # Query 12: Older articles (2015-2020) - likely haven't scraped these
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (2015[PDAT]:2020[PDAT]) AND (English[Language])',
        
        # Query 13: Very old articles (2010-2014) - definitely haven't scraped these
        '("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR "Osteoarthritis, Knee"[MeSH]) AND (2010[PDAT]:2014[PDAT]) AND (English[Language])',
    ]
    
    total_processed = 0
    total_errors = 0
    
    print(f"\n3. STARTING MULTI-QUERY SEARCH")
    print(f"   Target: {target_count} new articles")
    print(f"   Queries: {len(search_queries)}")
    print(f"   This will run continuously until target is reached\n")
    
    for i, query in enumerate(search_queries, 1):
        try:
                # Check progress - get actual database count (REFRESH from database)
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM papers')
                current_db_count = cursor.fetchone()[0]
                conn.close()
                new_count = current_db_count - initial_db_count
                # Force refresh to see actual count
                if new_count > 0:
                    print(f"   🎉 Database count increased! Now: {current_db_count} (was: {initial_db_count})")
            except Exception as e:
                logger.error(f"Error checking database count: {e}")
                current_pmids = get_existing_pmids()
                new_count = len(current_pmids) - initial_count
                current_db_count = len(current_pmids)
            
            if new_count >= target_count:
                print(f"\n{'='*80}")
                print(f"✅ TARGET REACHED!")
                print(f"{'='*80}")
                print(f"New articles added: {new_count} (target: {target_count})")
                print(f"Total articles now: {current_db_count} (started with: {initial_db_count})")
                break
            
            print(f"\n{'='*80}")
            print(f"QUERY {i}/{len(search_queries)}")
            print(f"{'='*80}")
            print(f"Current progress: {new_count} NEW articles added (target: {target_count})")
            print(f"Database: {current_db_count} total articles (started with: {initial_db_count})")
            print(f"Query: {query[:80]}...")
            
            # Search PubMed with rate limiting
            try:
                print(f"   Searching PubMed (this may take 30-60 seconds)...")
                # Use max_results=5000, no date_range_years (dates are in query if needed)
                pmids = scraper.search_pubmed(query, max_results=5000, date_range_years=None)
                # Add delay after search to respect rate limits
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error searching PubMed for query {i}: {e}")
                print(f"   ❌ Search failed: {e}")
                print(f"   Waiting 30 seconds before next query...")
                time.sleep(30)  # Wait longer on error
                continue
            
            if not pmids:
                print(f"   ⚠️  No articles found")
                continue
            
            print(f"   Found: {len(pmids)} PMIDs")
            
            # Filter duplicates BEFORE processing - check BOTH database AND JSON files
            # This matches what process_article() checks, so we don't process duplicates
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT pmid FROM papers WHERE pmid IS NOT NULL')
                current_db_pmids = {str(row[0]) for row in cursor.fetchall() if row[0]}
                conn.close()
                
                # ALSO check JSON files (process_article checks these too!)
                json_pmids = set()
                articles_dir = Path(__file__).parent.parent / "data" / "articles"
                if articles_dir.exists():
                    json_files = list(articles_dir.rglob("*.json"))
                    for json_file in json_files:
                        try:
                            with open(json_file, 'r') as f:
                                article = json.load(f)
                                if 'pmid' in article and article['pmid']:
                                    json_pmids.add(str(article['pmid']))
                        except:
                            continue
                
                # Combine both sources
                existing_pmids = current_db_pmids | json_pmids
                print(f"   ✓ Checked database: {len(current_db_pmids)} PMIDs")
                print(f"   ✓ Checked JSON files: {len(json_pmids)} PMIDs")
                print(f"   ✓ Total existing: {len(existing_pmids)} PMIDs")
            except Exception as e:
                logger.warning(f"Could not refresh PMID list: {e}")
            
            # Filter to ONLY new PMIDs - don't process duplicates at all
            new_pmids = [str(p) for p in pmids if str(p) not in existing_pmids]
            duplicate_count = len(pmids) - len(new_pmids)
            
            print(f"   📊 Results:")
            print(f"      Total found: {len(pmids)}")
            print(f"      Duplicates (skipping): {duplicate_count}")
            print(f"      NEW articles to process: {len(new_pmids)}")
            
            if not new_pmids:
                print(f"   ⚠️  All {len(pmids)} articles are duplicates - moving to next query immediately")
                print(f"   💡 This query found articles you already have. Trying next query...")
                continue
            
            # CRITICAL: Update existing_pmids set so we don't check these again
            existing_pmids.update(new_pmids)
            
            # Process ONLY new articles (duplicates already filtered out)
            print(f"   🚀 Processing {len(new_pmids)} NEW articles (duplicates already skipped)...")
            processed_this_query = 0
            errors_this_query = 0
            
            # Add delay before processing to respect rate limits
            time.sleep(1)
            
            for j, pmid in enumerate(new_pmids, 1):
                # Check if target reached - use database count
                if j % 50 == 0 or j == len(new_pmids):
                    try:
                        import sqlite3
                        # Force a fresh connection to see committed changes
                        conn = sqlite3.connect(str(db_path))
                        # Ensure we see committed data
                        conn.isolation_level = None  # Autocommit mode
                        cursor = conn.cursor()
                        cursor.execute('SELECT COUNT(*) FROM papers')
                        current_db_count = cursor.fetchone()[0]
                        conn.close()
                        new_count = current_db_count - initial_db_count
                        if new_count > 0:
                            print(f"   🎉 Database count increased! Now: {current_db_count} (was: {initial_db_count})")
                    except Exception as e:
                        logger.error(f"Error checking database count: {e}")
                        current_pmids = get_existing_pmids()
                        new_count = len(current_pmids) - initial_count
                        current_db_count = len(current_pmids)
                    
                    print(f"   📈 Progress: {new_count} NEW articles added, processed {j}/{len(new_pmids)} from this query")
                    print(f"   📊 Database: {current_db_count} total (target: {initial_db_count + target_count})")
                    
                    if new_count >= target_count:
                        print(f"   ✅ Target reached!")
                        break
                
                # Process article - these are confirmed NEW (duplicates already filtered)
                # We already checked they don't exist, so process directly
                try:
                    # Process the article - it's confirmed NEW
                    success = scraper.process_article(pmid)
                    if success:
                        processed_this_query += 1
                        total_processed += 1
                        if j % 10 == 0:
                            print(f"      ✓ Processed {j}/{len(new_pmids)}: {processed_this_query} successful")
                    else:
                        errors_this_query += 1
                        total_errors += 1
                except KeyboardInterrupt:
                    print(f"\n⚠️  Interrupted by user")
                    raise
                except Exception as e:
                    errors_this_query += 1
                    total_errors += 1
                    logger.error(f"Error processing {pmid}: {e}")
                    # Continue processing - don't stop on errors
                    continue
                
                # Small delay to avoid rate limiting
                if j % 10 == 0:
                    time.sleep(0.3)
                elif j % 50 == 0:
                    time.sleep(1)
            
            # Update existing PMIDs for next query
            existing_pmids = get_existing_pmids()
            
            # Final count for this query - use database count
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM papers')
                current_db_count = cursor.fetchone()[0]
                conn.close()
                new_count = current_db_count - initial_db_count
            except:
                current_pmids = get_existing_pmids()
                new_count = len(current_pmids) - initial_count
                current_db_count = len(current_pmids)
            
            print(f"   ✅ Query {i} complete: {processed_this_query} new articles processed")
            print(f"   Total NEW articles added: {new_count} (target: {target_count})")
            print(f"   Database: {current_db_count} total articles (started with: {initial_db_count})")
            print(f"   Errors this query: {errors_this_query}")
            
            # Save progress
            save_progress(i, total_processed, new_count, target_count)
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Interrupted by user")
            current_pmids = get_existing_pmids()
            new_count = len(current_pmids) - initial_count
            print(f"Progress saved: {new_count} new articles")
            break
        except Exception as e:
            logger.error(f"Error in query {i}: {e}", exc_info=True)
            print(f"   ❌ Query {i} failed: {e}")
            print(f"   Continuing to next query...")
            continue
    
    # Final summary - use database count
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM papers')
        final_db_count = cursor.fetchone()[0]
        conn.close()
        final_new_count = final_db_count - initial_db_count
    except:
        final_pmids = get_existing_pmids()
        final_new_count = len(final_pmids) - initial_count
        final_db_count = len(final_pmids)
    
    print(f"\n{'='*80}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*80}")
    print(f"Started with: {initial_db_count} articles")
    print(f"New articles ADDED: {final_new_count}")
    print(f"Target was: {target_count}")
    print(f"Final total: {final_db_count} articles")
    print(f"Total processed: {total_processed}")
    print(f"Total errors: {total_errors}")
    print(f"{'='*80}\n")
    
    return {
        "success": True,
        "new_articles": final_new_count,
        "target": target_count,
        "total_processed": total_processed,
        "total_errors": total_errors,
        "timestamp": datetime.now().isoformat()
    }


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("BATCH 2 SCRAPING - ROBUST VERSION")
    print("="*80)
    print(f"Target: 5,000 new articles")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log file: scraping_batch_2.log")
    print("="*80)
    
    result = scrape_new_articles_robust(target_count=5000)
    
    # Save final report
    report_path = Path(__file__).parent.parent / "data" / f"batch_2_scraping_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nReport saved: {report_path}")
    print("="*80)


if __name__ == "__main__":
    main()
