#!/usr/bin/env python3
"""
Rank Best Articles from the 314 Usable Articles

Identifies the highest-quality articles based on:
1. Relevance score (0-100)
2. PROBAST domains (Low Risk preferred)
3. Study design quality
4. Sample size
5. Novelty/impact
"""

import os
import sys
import pandas as pd
import json
from typing import List, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.literature_database import LiteratureDatabase


class ArticleRanker:
    """Rank articles by quality and relevance"""
    
    def __init__(self):
        self.database = LiteratureDatabase()
    
    def calculate_quality_score(self, article: Dict) -> float:
        """
        Calculate overall quality score (0-100)
        
        Factors:
        - Relevance score (40%)
        - PROBAST quality (30%)
        - Study design (20%)
        - Sample size/impact (10%)
        """
        score = 0.0
        
        # 1. Relevance score (0-100) - 40% weight
        relevance = article.get('relevance_score', 0) or 0
        score += (relevance / 100) * 40
        
        # 2. PROBAST quality (30% weight)
        probast_score = self._calculate_probast_score(article)
        score += probast_score * 30
        
        # 3. Study design (20% weight)
        design_score = self._calculate_design_score(article)
        score += design_score * 20
        
        # 4. Sample size/impact (10% weight)
        impact_score = self._calculate_impact_score(article)
        score += impact_score * 10
        
        return min(score, 100.0)
    
    def _calculate_probast_score(self, article: Dict) -> float:
        """Calculate PROBAST quality score (0-1)"""
        domain_1 = (article.get('probast_domain_1') or '').lower()
        domain_2 = (article.get('probast_domain_2') or '').lower()
        domain_3 = (article.get('probast_domain_3') or '').lower()
        domain_4 = (article.get('probast_domain_4') or '').lower()
        
        domains = [domain_1, domain_2, domain_3, domain_4]
        
        # Score: Low = 1.0, Moderate = 0.7, Unclear = 0.4, High = 0.0
        scores = {
            'low': 1.0,
            'moderate': 0.7,
            'unclear': 0.4,
            'high': 0.0
        }
        
        total = sum(scores.get(d, 0.4) for d in domains)
        return total / 4.0  # Average across 4 domains
    
    def _calculate_design_score(self, article: Dict) -> float:
        """Calculate study design quality score (0-1)"""
        abstract = (article.get('abstract') or '').lower()
        title = (article.get('title') or '').lower()
        text = f"{title} {abstract}"
        
        # High quality designs
        if any(term in text for term in ['prospective cohort', 'randomized controlled', 'systematic review', 'meta-analysis']):
            return 1.0
        
        # Medium quality designs
        if any(term in text for term in ['cohort', 'longitudinal', 'registry', 'database']):
            return 0.8
        
        # Lower quality designs
        if any(term in text for term in ['case-control', 'cross-sectional', 'retrospective']):
            return 0.6
        
        return 0.5  # Default
    
    def _calculate_impact_score(self, article: Dict) -> float:
        """Calculate impact/novelty score (0-1)"""
        abstract = (article.get('abstract') or '').lower()
        
        # Check for high-impact indicators
        impact_terms = [
            'validation', 'external validation', 'calibration', 'discrimination',
            'auc', 'c-statistic', 'harrell', 'epv', 'events per variable',
            'large sample', 'multicenter', 'international'
        ]
        
        impact_count = sum(1 for term in impact_terms if term in abstract)
        
        # Score based on impact indicators
        if impact_count >= 3:
            return 1.0
        elif impact_count >= 2:
            return 0.8
        elif impact_count >= 1:
            return 0.6
        else:
            return 0.5
    
    def rank_articles(self, min_quality: float = 70.0, max_articles: int = 100) -> List[Dict]:
        """
        Rank articles by quality score
        
        Args:
            min_quality: Minimum quality score (0-100)
            max_articles: Maximum number of articles to return
            
        Returns:
            List of ranked articles with quality scores
        """
        # Get usable articles from database
        conn = self.database.db_path
        import sqlite3
        
        conn_db = sqlite3.connect(conn)
        conn_db.row_factory = sqlite3.Row
        cursor = conn_db.cursor()
        
        cursor.execute('''
        SELECT * FROM papers 
        WHERE used_in_model = 1
        AND relevance_score >= 40
        ORDER BY relevance_score DESC
        ''')
        
        rows = cursor.fetchall()
        articles = [self.database._row_to_dict(row) for row in rows]
        
        conn_db.close()
        
        # Calculate quality scores
        ranked = []
        for article in articles:
            quality_score = self.calculate_quality_score(article)
            if quality_score >= min_quality:
                article['quality_score'] = quality_score
                ranked.append(article)
        
        # Sort by quality score (descending)
        ranked.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        # Limit to max_articles
        return ranked[:max_articles]
    
    def export_top_articles(self, output_path: str = 'data/top_articles.csv', 
                           min_quality: float = 70.0, max_articles: int = 100) -> str:
        """Export top-ranked articles to CSV"""
        top_articles = self.rank_articles(min_quality=min_quality, max_articles=max_articles)
        
        records = []
        for article in top_articles:
            records.append({
                'pmid': article.get('pmid', ''),
                'title': article.get('title', ''),
                'abstract': article.get('abstract', ''),
                'authors': article.get('authors', ''),
                'journal': article.get('journal', ''),
                'doi': article.get('doi', ''),
                'publication_date': article.get('publication_date', ''),
                'relevance_score': article.get('relevance_score', 0),
                'quality_score': article.get('quality_score', 0),
                'probast_risk': article.get('probast_risk', ''),
                'probast_domain_1': article.get('probast_domain_1', ''),
                'probast_domain_2': article.get('probast_domain_2', ''),
                'probast_domain_3': article.get('probast_domain_3', ''),
                'probast_domain_4': article.get('probast_domain_4', ''),
                'access_type': article.get('access_type', 'unknown'),
                'notes': article.get('notes', '')
            })
        
        df = pd.DataFrame(records)
        df.to_csv(output_path, index=False)
        
        return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Rank Best Articles')
    parser.add_argument('--min-quality', type=float, default=70.0, 
                       help='Minimum quality score (0-100, default: 70.0)')
    parser.add_argument('--max-articles', type=int, default=100,
                       help='Maximum number of articles to return (default: 100)')
    parser.add_argument('--export', action='store_true',
                       help='Export top articles to CSV')
    
    args = parser.parse_args()
    
    ranker = ArticleRanker()
    
    print("Ranking articles by quality...")
    top_articles = ranker.rank_articles(min_quality=args.min_quality, max_articles=args.max_articles)
    
    print(f"\n{'='*80}")
    print(f"TOP {len(top_articles)} ARTICLES (Quality Score ≥{args.min_quality})")
    print(f"{'='*80}\n")
    
    for i, article in enumerate(top_articles[:20], 1):  # Show top 20
        quality = article.get('quality_score', 0)
        relevance = article.get('relevance_score', 0)
        probast = article.get('probast_risk', 'Unknown')
        title = article.get('title', 'No title')[:70]
        
        print(f"{i:2d}. Quality: {quality:5.1f} | Relevance: {relevance:3d} | PROBAST: {probast:8s}")
        print(f"    {title}...")
        print()
    
    if len(top_articles) > 20:
        print(f"... and {len(top_articles) - 20} more articles\n")
    
    print(f"{'='*80}")
    print(f"Total top articles: {len(top_articles)}")
    print(f"Quality score range: {min(a.get('quality_score', 0) for a in top_articles):.1f} - {max(a.get('quality_score', 0) for a in top_articles):.1f}")
    print(f"{'='*80}")
    
    if args.export:
        output_path = ranker.export_top_articles(
            min_quality=args.min_quality,
            max_articles=args.max_articles
        )
        print(f"\n✅ Exported top {len(top_articles)} articles to: {output_path}")
