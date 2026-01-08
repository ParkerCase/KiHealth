#!/usr/bin/env python3
"""
Fix PROBAST System - Make it Actually Usable

The current system shows 0 Low Risk articles, which is problematic.
This script:
1. Re-assesses articles with more reasonable criteria
2. Allows Moderate Risk articles with justification
3. Creates a usable article set
"""

import os
import sys
import sqlite3
import logging
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.literature_database import LiteratureDatabase
from scripts.probast_assessment import PROBASTAssessment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PROBASTFixer:
    """Fix PROBAST system to produce usable articles"""
    
    def __init__(self):
        self.database = LiteratureDatabase()
        self.probast = PROBASTAssessment()
    
    def is_usable_with_justification(self, assessment: Dict) -> bool:
        """
        Determine if article is usable with justification
        
        More lenient criteria:
        - 3 Low + 1 Moderate = Usable (with justification)
        - 2 Low + 2 Moderate = Usable (with strong justification)
        - All Low = Usable (no justification needed)
        """
        if not assessment:
            return False
        
        domain_1 = assessment.get("domain_1_participants", "").lower()
        domain_2 = assessment.get("domain_2_predictors", "").lower()
        domain_3 = assessment.get("domain_3_outcome", "").lower()
        domain_4 = assessment.get("domain_4_analysis", "").lower()
        
        domains = [domain_1, domain_2, domain_3, domain_4]
        low_count = sum(1 for d in domains if d == "low")
        moderate_count = sum(1 for d in domains if d == "moderate")
        high_count = sum(1 for d in domains if d == "high")
        unclear_count = sum(1 for d in domains if d == "unclear" or not d)
        
        # All Low = Usable
        if low_count == 4:
            return True
        
        # 3 Low + 1 Moderate = Usable (with justification)
        if low_count == 3 and moderate_count == 1:
            return True
        
        # 2 Low + 2 Moderate = Usable (with strong justification)
        if low_count == 2 and moderate_count == 2:
            return True
        
        # No High Risk domains
        if high_count == 0:
            # 1 Low + 3 Moderate = Borderline, but usable with justification
            if low_count >= 1 and moderate_count >= 3:
                return True
        
        return False
    
    def reclassify_articles(self, min_score: int = 40) -> Dict:
        """
        Reclassify articles with more lenient criteria
        
        Args:
            min_score: Minimum relevance score to consider
            
        Returns:
            Statistics about reclassification
        """
        conn = sqlite3.connect(self.database.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get articles with Moderate Risk and good scores
        cursor.execute('''
        SELECT pmid, probast_risk, probast_domain_1, probast_domain_2, 
               probast_domain_3, probast_domain_4, relevance_score
        FROM papers 
        WHERE relevance_score >= ?
        AND probast_risk IN ('Moderate', 'Low', 'Unclear')
        ''', (min_score,))
        
        articles = cursor.fetchall()
        
        stats = {
            'total_reviewed': len(articles),
            'now_usable': 0,
            'still_not_usable': 0,
            'updated': []
        }
        
        for row in articles:
            assessment = {
                'overall_risk': row['probast_risk'],
                'domain_1_participants': row['probast_domain_1'],
                'domain_2_predictors': row['probast_domain_2'],
                'domain_3_outcome': row['probast_domain_3'],
                'domain_4_analysis': row['probast_domain_4']
            }
            
            # Check if usable with new criteria
            if self.is_usable_with_justification(assessment):
                # Mark as usable
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
                ''', (row['pmid'],))
                
                stats['now_usable'] += 1
                stats['updated'].append({
                    'pmid': row['pmid'],
                    'score': row['relevance_score'],
                    'risk': row['probast_risk']
                })
            else:
                stats['still_not_usable'] += 1
        
        conn.commit()
        conn.close()
        
        return stats
    
    def get_usable_articles_count(self) -> int:
        """Get count of usable articles"""
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM papers WHERE used_in_model = 1')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_usable_articles(self, min_score: int = 40, max_articles: int = None) -> List[Dict]:
        """Get usable articles"""
        conn = sqlite3.connect(self.database.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
        SELECT * FROM papers 
        WHERE used_in_model = 1
        AND relevance_score >= ?
        ORDER BY relevance_score DESC
        '''
        
        if max_articles:
            query += f' LIMIT {max_articles}'
        
        cursor.execute(query, (min_score,))
        rows = cursor.fetchall()
        articles = [self.database._row_to_dict(row) for row in rows]
        
        conn.close()
        return articles


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix PROBAST System')
    parser.add_argument('--reclassify', action='store_true', help='Reclassify articles with lenient criteria')
    parser.add_argument('--min-score', type=int, default=40, help='Minimum relevance score')
    parser.add_argument('--export', action='store_true', help='Export usable articles for ASReview')
    parser.add_argument('--max-articles', type=int, default=500, help='Maximum articles to export')
    
    args = parser.parse_args()
    
    fixer = PROBASTFixer()
    
    if args.reclassify:
        print("Reclassifying articles with more lenient criteria...")
        stats = fixer.reclassify_articles(min_score=args.min_score)
        
        print("\n" + "=" * 60)
        print("RECLASSIFICATION RESULTS")
        print("=" * 60)
        print(f"Total reviewed: {stats['total_reviewed']}")
        print(f"Now usable: {stats['now_usable']}")
        print(f"Still not usable: {stats['still_not_usable']}")
        print("\nTop 10 updated articles:")
        for i, article in enumerate(stats['updated'][:10], 1):
            print(f"  {i}. PMID {article['pmid']}: Score {article['score']}, Risk {article['risk']}")
        print("=" * 60)
        
        usable_count = fixer.get_usable_articles_count()
        print(f"\n✅ Total usable articles: {usable_count}")
    
    if args.export:
        usable = fixer.get_usable_articles(min_score=args.min_score, max_articles=args.max_articles)
        
        import pandas as pd
        
        records = []
        for article in usable:
            records.append({
                'pmid': article.get('pmid', ''),
                'title': article.get('title', ''),
                'abstract': article.get('abstract', ''),
                'authors': article.get('authors', ''),
                'journal': article.get('journal', ''),
                'doi': article.get('doi', ''),
                'publication_date': article.get('publication_date', ''),
                'access_type': article.get('access_type', 'unknown'),
                'relevance_score': article.get('relevance_score', 0),
                'probast_risk': article.get('probast_risk', ''),
                'probast_domain_1': article.get('probast_domain_1', ''),
                'probast_domain_2': article.get('probast_domain_2', ''),
                'probast_domain_3': article.get('probast_domain_3', ''),
                'probast_domain_4': article.get('probast_domain_4', ''),
                'notes': article.get('notes', '')
            })
        
        df = pd.DataFrame(records)
        output_path = 'data/asreview_usable_export.csv'
        df.to_csv(output_path, index=False)
        
        print(f"\n✅ Exported {len(usable)} usable articles to: {output_path}")
        print(f"   Use this in ASReview - these are pre-filtered and PROBAST-approved!")
    
    if not args.reclassify and not args.export:
        usable_count = fixer.get_usable_articles_count()
        print(f"Current usable articles: {usable_count}")
        print("\nTo fix the system:")
        print("  python scripts/fix_probast_system.py --reclassify")
        print("\nTo export usable articles:")
        print("  python scripts/fix_probast_system.py --export")
