#!/usr/bin/env python3
"""
Process All Monitoring Articles Through Full Workflow

Takes the 139 unique articles from GitHub monitoring, processes them through:
1. Scraping (if not already in database)
2. PROBAST assessment
3. Mark as usable if appropriate
4. Update totals
"""

import os
import sys
import pandas as pd
import sqlite3
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.literature_database import LiteratureDatabase
from scripts.pubmed_scraper import PubMedScraper
from scripts.probast_assessment import PROBASTAssessment


class ProcessMonitoringArticles:
    """Process monitoring articles through full workflow"""
    
    def __init__(self):
        self.database = LiteratureDatabase()
        self.probast = PROBASTAssessment()
        self.scraper = PubMedScraper()
    
    def get_monitoring_pmids(self, csv_path: str) -> List[str]:
        """Get unique PMIDs from monitoring CSV"""
        df = pd.read_csv(csv_path)
        unique_pmids = df['pmid'].astype(str).unique().tolist()
        return unique_pmids
    
    def get_existing_pmids(self) -> set:
        """Get all existing PMIDs from database"""
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT pmid FROM papers')
        existing = {row[0] for row in cursor.fetchall()}
        conn.close()
        return existing
    
    def scrape_new_articles(self, pmids: List[str]) -> Dict:
        """Scrape articles that aren't in database"""
        existing = self.get_existing_pmids()
        new_pmids = [p for p in pmids if p not in existing]
        
        print(f"Scraping {len(new_pmids)} new articles...")
        
        stats = {
            'total_new': len(new_pmids),
            'successfully_scraped': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, pmid in enumerate(new_pmids, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(new_pmids)}")
            
            try:
                success = self.scraper.process_article(pmid)
                if success:
                    stats['successfully_scraped'] += 1
                else:
                    stats['failed'] += 1
                    stats['errors'].append(f"PMID {pmid}: Processing failed")
            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f"PMID {pmid}: {str(e)}")
        
        return stats
    
    def assess_and_mark_articles(self, pmids: List[str]) -> Dict:
        """Assess all monitoring articles with PROBAST and mark as usable if appropriate"""
        conn = sqlite3.connect(self.database.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        stats = {
            'total_assessed': 0,
            'marked_usable': 0,
            'already_usable': 0,
            'not_usable': 0
        }
        
        for pmid in pmids:
            try:
                # Get article from database
                cursor.execute('SELECT * FROM papers WHERE pmid = ?', (pmid,))
                row = cursor.fetchone()
                
                if not row:
                    continue
                
                article = self.database._row_to_dict(row)
                stats['total_assessed'] += 1
                
                # Check if already marked as usable
                if article.get('used_in_model'):
                    stats['already_usable'] += 1
                    continue
                
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
                else:
                    # Use existing assessment
                    assessment = {
                        'overall_risk': article.get('probast_risk'),
                        'domain_1_participants': article.get('probast_domain_1'),
                        'domain_2_predictors': article.get('probast_domain_2'),
                        'domain_3_outcome': article.get('probast_domain_3'),
                        'domain_4_analysis': article.get('probast_domain_4')
                    }
                
                # Check if usable with justification
                if self._is_usable_with_justification(assessment):
                    # Check relevance score (should be ≥40)
                    relevance = article.get('relevance_score', 0) or 0
                    if relevance >= 40:
                        cursor.execute('''
                        UPDATE papers 
                        SET used_in_model = 1,
                            notes = 'Usable with justification: From GitHub monitoring'
                        WHERE pmid = ?
                        ''', (pmid,))
                        stats['marked_usable'] += 1
                    else:
                        stats['not_usable'] += 1
                else:
                    stats['not_usable'] += 1
            
            except Exception as e:
                print(f"Warning: Error processing PMID {pmid}: {e}")
                continue
        
        conn.commit()
        conn.close()
        return stats
    
    def _is_usable_with_justification(self, assessment: Dict) -> bool:
        """Check if article is usable with justification"""
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
    
    def process_all(self, monitoring_csv: str) -> Dict:
        """Process all monitoring articles through full workflow"""
        print("=" * 80)
        print("PROCESSING MONITORING ARTICLES")
        print("=" * 80)
        
        # Get unique PMIDs
        pmids = self.get_monitoring_pmids(monitoring_csv)
        print(f"\nTotal unique PMIDs from monitoring: {len(pmids)}")
        
        # Step 1: Scrape new articles
        print("\nStep 1: Scraping new articles...")
        scrape_stats = self.scrape_new_articles(pmids)
        print(f"  Successfully scraped: {scrape_stats['successfully_scraped']}")
        print(f"  Failed: {scrape_stats['failed']}")
        
        # Step 2: Assess and mark as usable
        print("\nStep 2: Assessing with PROBAST and marking usable articles...")
        assess_stats = self.assess_and_mark_articles(pmids)
        print(f"  Total assessed: {assess_stats['total_assessed']}")
        print(f"  Marked as usable: {assess_stats['marked_usable']}")
        print(f"  Already usable: {assess_stats['already_usable']}")
        print(f"  Not usable: {assess_stats['not_usable']}")
        
        return {
            'scraping': scrape_stats,
            'assessment': assess_stats,
            'total_processed': len(pmids)
        }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Monitoring Articles')
    parser.add_argument('--monitoring-csv', type=str,
                       default='../data/monitoringdata.csv',
                       help='Path to monitoring data CSV')
    
    args = parser.parse_args()
    
    processor = ProcessMonitoringArticles()
    results = processor.process_all(args.monitoring_csv)
    
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Total articles processed: {results['total_processed']}")
    print(f"New articles scraped: {results['scraping']['successfully_scraped']}")
    print(f"Articles marked as usable: {results['assessment']['marked_usable']}")
    print("=" * 80)
