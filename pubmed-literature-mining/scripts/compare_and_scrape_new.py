#!/usr/bin/env python3
"""
Compare Monitoring Data with Database and Scrape New Articles

Compares articles from monitoringdata.csv (GitHub runs) with existing database,
identifies new articles, scrapes them, and updates final totals.
"""

import os
import sys
import pandas as pd
import sqlite3
from typing import List, Set, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.literature_database import LiteratureDatabase
from scripts.pubmed_scraper import PubMedScraper
from scripts.probast_assessment import PROBASTAssessment
from scripts.literature_quality_workflow import LiteratureQualityWorkflow


class CompareAndScrapeNew:
    """Compare monitoring data with database and scrape new articles"""
    
    def __init__(self):
        self.database = LiteratureDatabase()
        self.probast = PROBASTAssessment()
        self.workflow = LiteratureQualityWorkflow()
    
    def get_existing_pmids(self) -> Set[str]:
        """Get all existing PMIDs from database"""
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT pmid FROM papers')
        existing = {row[0] for row in cursor.fetchall()}
        
        conn.close()
        return existing
    
    def load_monitoring_data(self, csv_path: str) -> pd.DataFrame:
        """Load monitoring data CSV"""
        df = pd.read_csv(csv_path)
        
        # Normalize column names
        if 'PMID' in df.columns:
            df['pmid'] = df['PMID'].astype(str)
        elif 'pmid' in df.columns:
            df['pmid'] = df['pmid'].astype(str)
        else:
            raise ValueError("No PMID column found in monitoring data")
        
        return df
    
    def find_new_articles(self, monitoring_df: pd.DataFrame) -> pd.DataFrame:
        """Find articles in monitoring data that aren't in database"""
        existing_pmids = self.get_existing_pmids()
        
        # Get PMIDs from monitoring data
        monitoring_pmids = set(monitoring_df['pmid'].astype(str).unique())
        
        # Find new PMIDs
        new_pmids = monitoring_pmids - existing_pmids
        
        print(f"Existing articles in database: {len(existing_pmids)}")
        print(f"Articles in monitoring data: {len(monitoring_pmids)}")
        print(f"New articles to scrape: {len(new_pmids)}")
        
        # Filter monitoring data to only new articles
        new_df = monitoring_df[monitoring_df['pmid'].astype(str).isin(new_pmids)].copy()
        
        return new_df
    
    def scrape_new_articles(self, new_articles_df: pd.DataFrame) -> Dict:
        """Scrape new articles and add to database"""
        new_pmids = new_articles_df['pmid'].astype(str).tolist()
        
        print(f"\nScraping {len(new_pmids)} new articles...")
        
        stats = {
            'total_new': len(new_pmids),
            'successfully_scraped': 0,
            'failed': 0,
            'errors': []
        }
        
        scraper = PubMedScraper()
        
        for i, pmid in enumerate(new_pmids, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(new_pmids)}")
            
            try:
                # Process article
                success = scraper.process_article(pmid)
                
                if success:
                    stats['successfully_scraped'] += 1
                else:
                    stats['failed'] += 1
                    stats['errors'].append(f"PMID {pmid}: Processing failed")
            
            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f"PMID {pmid}: {str(e)}")
        
        # Now assess with PROBAST and mark usable
        print("\nAssessing new articles with PROBAST...")
        self._assess_and_mark_new_articles(new_pmids)
        
        return stats
    
    def _assess_and_mark_new_articles(self, pmids: List[str]):
        """Assess new articles with PROBAST and mark as usable if appropriate"""
        conn = sqlite3.connect(self.database.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        for pmid in pmids:
            try:
                # Get article from database
                cursor.execute('SELECT * FROM papers WHERE pmid = ?', (pmid,))
                row = cursor.fetchone()
                
                if not row:
                    continue
                
                article = self.database._row_to_dict(row)
                
                # Assess with PROBAST if not already assessed
                if not article.get('probast_risk'):
                    assessment = self.probast.assess_article(article)
                    
                    # Update database with assessment
                    cursor.execute('''
                    UPDATE papers 
                    SET probast_risk = ?,
                        probast_domain_1 = ?,
                        probast_domain_2 = ?,
                        probast_domain_3 = ?,
                        probast_domain_4 = ?,
                        assessment_date = datetime('now'),
                        assessment_method = 'automated'
                    WHERE pmid = ?
                    ''', (
                        assessment.get('overall_risk'),
                        assessment.get('domain_1_participants'),
                        assessment.get('domain_2_predictors'),
                        assessment.get('domain_3_outcome'),
                        assessment.get('domain_4_analysis'),
                        pmid
                    ))
                    
                    # Mark as usable if appropriate (using lenient criteria)
                    if self._is_usable_with_justification(assessment):
                        cursor.execute('''
                        UPDATE papers 
                        SET used_in_model = 1,
                            notes = 'Usable with justification: ' || 
                                    CASE 
                                        WHEN probast_risk = 'Low' THEN 'All domains Low Risk'
                                        WHEN probast_risk = 'Moderate' THEN '3+ Low domains or 2 Low + 2 Moderate'
                                        ELSE 'Reclassified as usable'
                                    END
                        WHERE pmid = ?
                        ''', (pmid,))
            except Exception as e:
                print(f"Warning: Error processing PMID {pmid}: {e}")
                continue
        
        conn.commit()
        conn.close()
    
    def _is_usable_with_justification(self, assessment: Dict) -> bool:
        """Check if article is usable with justification (same as fix_probast_system)"""
        if not assessment:
            return False
        
        domain_1 = (assessment.get("domain_1_participants", "") or "").lower()
        domain_2 = (assessment.get("domain_2_predictors", "") or "").lower()
        domain_3 = (assessment.get("domain_3_outcome", "") or "").lower()
        domain_4 = (assessment.get("domain_4_analysis", "") or "").lower()
        
        domains = [domain_1, domain_2, domain_3, domain_4]
        low_count = sum(1 for d in domains if d == "low")
        moderate_count = sum(1 for d in domains if d == "moderate")
        high_count = sum(1 for d in domains if d == "high")
        
        # All Low = Usable
        if low_count == 4:
            return True
        
        # 3 Low + 1 Moderate = Usable
        if low_count == 3 and moderate_count == 1:
            return True
        
        # 2 Low + 2 Moderate = Usable
        if low_count == 2 and moderate_count == 2:
            return True
        
        # No High Risk domains
        if high_count == 0:
            if low_count >= 1 and moderate_count >= 3:
                return True
        
        return False
    
    def generate_final_report(self) -> Dict:
        """Generate final comprehensive report with all totals"""
        from scripts.comprehensive_literature_report import ComprehensiveLiteratureReport
        
        reporter = ComprehensiveLiteratureReport()
        return reporter.get_all_metrics()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare and Scrape New Articles')
    parser.add_argument('--monitoring-csv', type=str, 
                       default='../data/monitoringdata.csv',
                       help='Path to monitoring data CSV')
    parser.add_argument('--dry-run', action='store_true',
                       help='Only identify new articles, do not scrape')
    
    args = parser.parse_args()
    
    comparer = CompareAndScrapeNew()
    
    print("=" * 80)
    print("COMPARING MONITORING DATA WITH DATABASE")
    print("=" * 80)
    
    # Load monitoring data
    print(f"\nLoading monitoring data from: {args.monitoring_csv}")
    monitoring_df = comparer.load_monitoring_data(args.monitoring_csv)
    print(f"Loaded {len(monitoring_df)} articles from monitoring data")
    
    # Find new articles
    print("\nFinding new articles...")
    new_articles_df = comparer.find_new_articles(monitoring_df)
    
    if len(new_articles_df) == 0:
        print("\n✅ No new articles found. All articles already in database.")
    else:
        print(f"\n📋 New articles to scrape: {len(new_articles_df)}")
        print(f"\nSample new PMIDs:")
        print(new_articles_df['pmid'].head(10).tolist())
        
        if not args.dry_run:
            # Scrape new articles
            print("\n" + "=" * 80)
            print("SCRAPING NEW ARTICLES")
            print("=" * 80)
            stats = comparer.scrape_new_articles(new_articles_df)
            
            print(f"\n✅ Scraping complete:")
            print(f"   Successfully scraped: {stats['successfully_scraped']}")
            print(f"   Failed: {stats['failed']}")
            
            if stats['errors']:
                print(f"\n⚠️ Errors ({len(stats['errors'])}):")
                for error in stats['errors'][:10]:  # Show first 10
                    print(f"   {error}")
                if len(stats['errors']) > 10:
                    print(f"   ... and {len(stats['errors']) - 10} more")
        else:
            print("\n🔍 DRY RUN: Not scraping articles")
    
    # Generate final report
    print("\n" + "=" * 80)
    print("FINAL TOTALS")
    print("=" * 80)
    metrics = comparer.generate_final_report()
    
    print(f"\n📊 Final Statistics:")
    print(f"   Total Articles Looked At: {metrics['total_articles_looked_at']:,}")
    print(f"   Articles Used for Model: {metrics['articles_used_for_model']:,}")
    print(f"   Usage Rate: {(metrics['articles_used_for_model']/metrics['total_articles_looked_at']*100):.1f}%")
    print(f"   Open Access: {metrics['total_open_access']:,}")
    print(f"   Paywalled: {metrics['total_paywalled']:,}")
    print(f"\n✅ PROBAST Compliance:")
    print(f"   High Risk: {metrics['high_risk_count']} (should be 0)")
    print(f"   Moderate Risk: {metrics['probast_distribution'].get('Moderate', 0)}")
    print(f"   Low Risk: {metrics['probast_distribution'].get('Low', 0)}")
    print("=" * 80)
