#!/usr/bin/env python3
"""
Automated Screening System
Pre-filters articles using relevance scoring so you don't have to manually review 4,671 articles.

This uses the existing relevance scoring system to automatically identify relevant articles,
so you only need to review the high-scoring ones (or let the system handle it automatically).
"""

import os
import sys
import json
import logging
from typing import List, Dict
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.literature_database import LiteratureDatabase
from scripts.enhanced_relevance_scoring import EnhancedRelevanceScorer

logger = logging.getLogger(__name__)


class AutomatedScreening:
    """Automated screening using relevance scores"""
    
    def __init__(self):
        self.database = LiteratureDatabase()
        self.scorer = EnhancedRelevanceScorer()
    
    def get_relevant_articles(self, min_score: int = 60, max_articles: int = None) -> List[Dict]:
        """
        Get articles automatically filtered by relevance score
        
        Args:
            min_score: Minimum relevance score (0-100)
            max_articles: Maximum number of articles to return (None = all)
            
        Returns:
            List of relevant articles sorted by score
        """
        import sqlite3
        
        conn = sqlite3.connect(self.database.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get articles with relevance scores
        query = '''
        SELECT * FROM papers 
        WHERE relevance_score >= ?
        ORDER BY relevance_score DESC
        '''
        
        if max_articles:
            query += f' LIMIT {max_articles}'
        
        cursor.execute(query, (min_score,))
        rows = cursor.fetchall()
        
        articles = []
        for row in rows:
            article = dict(row)
            # Parse JSON fields
            if article.get('predictive_factors'):
                try:
                    article['predictive_factors'] = json.loads(article['predictive_factors'])
                except:
                    article['predictive_factors'] = []
            articles.append(article)
        
        conn.close()
        return articles
    
    def auto_screen_articles(self, min_score: int = 70) -> Dict:
        """
        Automatically screen articles based on relevance score
        
        Args:
            min_score: Minimum relevance score to consider "relevant"
            
        Returns:
            Dictionary with screening results
        """
        logger.info(f"Automated screening with minimum score: {min_score}")
        
        import sqlite3
        
        conn = sqlite3.connect(self.database.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all articles with scores
        cursor.execute('SELECT pmid, relevance_score, title FROM papers')
        all_articles = cursor.fetchall()
        
        # Categorize
        relevant = []
        irrelevant = []
        needs_review = []
        
        for row in all_articles:
            score = row['relevance_score'] or 0
            
            if score >= min_score:
                relevant.append({
                    'pmid': row['pmid'],
                    'score': score,
                    'title': row['title']
                })
            elif score >= 40:  # Medium scores need review
                needs_review.append({
                    'pmid': row['pmid'],
                    'score': score,
                    'title': row['title']
                })
            else:
                irrelevant.append({
                    'pmid': row['pmid'],
                    'score': score,
                    'title': row['title']
                })
        
        results = {
            'total_articles': len(all_articles),
            'automatically_relevant': len(relevant),
            'needs_review': len(needs_review),
            'automatically_irrelevant': len(irrelevant),
            'relevant_articles': relevant[:100],  # Top 100
            'needs_review_articles': needs_review[:50]  # Top 50 for review
        }
        
        conn.close()
        return results
    
    def export_for_review(self, min_score: int = 60, max_articles: int = 500) -> str:
        """
        Export only high-scoring articles for manual review
        
        This way you only review the most relevant articles, not all 4,671!
        
        Args:
            min_score: Minimum relevance score
            max_articles: Maximum articles to export
            
        Returns:
            Path to exported CSV file
        """
        relevant = self.get_relevant_articles(min_score=min_score, max_articles=max_articles)
        
        import pandas as pd
        
        records = []
        for article in relevant:
            records.append({
                'pmid': article.get('pmid', ''),
                'title': article.get('title', ''),
                'abstract': article.get('abstract', ''),
                'authors': article.get('authors', ''),
                'journal': article.get('journal', ''),
                'doi': article.get('doi', ''),
                'publication_date': article.get('publication_date', ''),
                'access_type': article.get('access_type', 'unknown'),
                'relevance_score': article.get('relevance_score', 0)
            })
        
        df = pd.DataFrame(records)
        output_path = 'data/asreview_filtered_export.csv'
        df.to_csv(output_path, index=False)
        
        logger.info(f"Exported {len(relevant)} high-scoring articles to {output_path}")
        return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Screening System')
    parser.add_argument('--export', action='store_true', help='Export filtered articles for ASReview')
    parser.add_argument('--min-score', type=int, default=70, help='Minimum relevance score (default: 70)')
    parser.add_argument('--max-articles', type=int, default=500, help='Maximum articles to export (default: 500)')
    
    args = parser.parse_args()
    
    screening = AutomatedScreening()
    
    if args.export:
        # Export filtered articles
        output_path = screening.export_for_review(min_score=args.min_score, max_articles=args.max_articles)
        print(f"\n✅ Exported filtered articles to: {output_path}")
        print(f"   Use this file in ASReview instead of the full 4,671 articles!")
    else:
        # Show screening results
        results = screening.auto_screen_articles(min_score=args.min_score)
        
        print("=" * 60)
        print("AUTOMATED SCREENING RESULTS")
        print("=" * 60)
        print(f"Total articles: {results['total_articles']}")
        print(f"Automatically Relevant (score ≥{args.min_score}): {results['automatically_relevant']}")
        print(f"Needs Review (score 40-{args.min_score-1}): {results['needs_review']}")
        print(f"Automatically Irrelevant (score <40): {results['automatically_irrelevant']}")
        print()
        print("=" * 60)
        print("RECOMMENDATION")
        print("=" * 60)
        print(f"✅ You only need to review {results['automatically_relevant']} articles")
        print(f"   (instead of all {results['total_articles']}!)")
        print()
        print("Export filtered list for ASReview:")
        print(f"  python scripts/automated_screening.py --export --min-score {args.min_score}")
        print("=" * 60)
