#!/usr/bin/env python3
"""
Literature Quality Workflow
Complete workflow for processing articles through ASReview, PROBAST assessment, and SQLite storage.

Workflow:
1. PubMed Scraper → Fetch articles (thousands, not just 100)
2. Export to CSV → For ASReview LAB screening
3. ASReview LAB → AI screening (keeps only high-quality papers)
4. PROBAST Assessment → Score each paper
5. SQLite Database → Store with PROBAST scores
6. Only Low Risk PROBAST papers → Used in model
"""

import os
import sys
import json
import logging
from typing import List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.pubmed_scraper import PubMedScraper
from scripts.asreview_integration import ASReviewIntegration
from scripts.probast_assessment import PROBASTAssessment
from scripts.literature_database import LiteratureDatabase

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/literature_quality_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LiteratureQualityWorkflow:
    """Complete literature quality workflow"""
    
    def __init__(self):
        self.scraper = PubMedScraper()
        self.asreview = ASReviewIntegration()
        self.probast = PROBASTAssessment()
        self.database = LiteratureDatabase()
        
        # Increase max articles for comprehensive search
        self.scraper.max_articles = int(os.getenv('MAX_ARTICLES_PER_RUN', '5000'))
    
    def run_full_workflow(self, max_articles: int = 5000, use_asreview: bool = True) -> Dict:
        """
        Run complete workflow: scrape → screen → assess → store
        
        Args:
            max_articles: Maximum articles to fetch from PubMed
            use_asreview: Whether to use ASReview LAB for screening
            
        Returns:
            Dictionary with workflow statistics
        """
        logger.info("=" * 80)
        logger.info("Starting Literature Quality Workflow")
        logger.info("=" * 80)
        
        stats = {
            "articles_fetched": 0,
            "articles_screened": 0,
            "articles_assessed": 0,
            "articles_stored": 0,
            "low_risk_probast": 0,
            "usable_for_model": 0,
            "errors": []
        }
        
        try:
            # Step 1: Fetch articles from PubMed
            logger.info(f"Step 1: Fetching up to {max_articles} articles from PubMed...")
            articles = self._fetch_articles(max_articles)
            stats["articles_fetched"] = len(articles)
            logger.info(f"Fetched {len(articles)} articles")
            
            if not articles:
                logger.warning("No articles fetched, stopping workflow")
                return stats
            
            # Step 2: ASReview screening (optional)
            if use_asreview and self.asreview.asreview_available:
                logger.info("Step 2: Exporting articles for ASReview LAB screening...")
                export_path = "data/asreview_export.csv"
                if self.asreview.export_for_asreview(articles, export_path):
                    logger.info(f"Exported {len(articles)} articles to {export_path}")
                    logger.info("IMPORTANT: Run ASReview LAB to screen articles:")
                    logger.info("  1. Install: pip install asreview")
                    logger.info("  2. Run: asreview web")
                    logger.info("  3. Upload: data/asreview_export.csv")
                    logger.info("  4. Screen articles and export results")
                    logger.info("  5. Import results using import_asreview_results()")
                else:
                    logger.warning("Failed to export for ASReview, continuing without screening")
                    use_asreview = False
            
            # If ASReview not used, use all articles
            articles_to_assess = articles
            
            # Step 3: PROBAST Assessment
            logger.info("Step 3: Assessing articles with PROBAST...")
            assessed_articles = []
            
            for i, article in enumerate(articles_to_assess, 1):
                if i % 100 == 0:
                    logger.info(f"Assessing article {i}/{len(articles_to_assess)}...")
                
                try:
                    assessment = self.probast.assess_article(article)
                    article["probast_assessment"] = assessment
                    assessed_articles.append(article)
                    stats["articles_assessed"] += 1
                    
                    if assessment.get("overall_risk") == "Low":
                        stats["low_risk_probast"] += 1
                    
                except Exception as e:
                    logger.error(f"Error assessing article {article.get('pmid', 'unknown')}: {e}")
                    stats["errors"].append(f"Assessment error for {article.get('pmid', 'unknown')}: {e}")
            
            logger.info(f"Assessed {len(assessed_articles)} articles")
            logger.info(f"Low Risk PROBAST: {stats['low_risk_probast']}")
            
            # Step 4: Store in SQLite database
            logger.info("Step 4: Storing articles in SQLite database...")
            
            for i, article in enumerate(assessed_articles, 1):
                if i % 100 == 0:
                    logger.info(f"Storing article {i}/{len(assessed_articles)}...")
                
                try:
                    assessment = article.get("probast_assessment", {})
                    if self.database.add_article(article, assessment):
                        stats["articles_stored"] += 1
                        
                        # Mark as usable if Low Risk
                        if self.probast.is_usable_for_model(assessment):
                            self.database.mark_as_used_in_model(article.get("pmid", ""))
                            stats["usable_for_model"] += 1
                    else:
                        stats["errors"].append(f"Storage error for {article.get('pmid', 'unknown')}")
                        
                except Exception as e:
                    logger.error(f"Error storing article {article.get('pmid', 'unknown')}: {e}")
                    stats["errors"].append(f"Storage error for {article.get('pmid', 'unknown')}: {e}")
            
            logger.info(f"Stored {stats['articles_stored']} articles in database")
            logger.info(f"Usable for model: {stats['usable_for_model']}")
            
            # Step 5: Generate summary
            db_stats = self.database.get_statistics()
            stats["database_statistics"] = db_stats
            
            logger.info("=" * 80)
            logger.info("Workflow Complete!")
            logger.info("=" * 80)
            logger.info(f"Articles fetched: {stats['articles_fetched']}")
            logger.info(f"Articles assessed: {stats['articles_assessed']}")
            logger.info(f"Articles stored: {stats['articles_stored']}")
            logger.info(f"Low Risk PROBAST: {stats['low_risk_probast']}")
            logger.info(f"Usable for model: {stats['usable_for_model']}")
            logger.info("=" * 80)
            
            return stats
            
        except Exception as e:
            logger.error(f"Workflow error: {e}", exc_info=True)
            stats["errors"].append(f"Workflow error: {e}")
            return stats
    
    def _fetch_articles(self, max_articles: int) -> List[Dict]:
        """Fetch articles from PubMed"""
        try:
            # Use comprehensive search strategy
            query = self._build_comprehensive_query()
            
            # Search PubMed
            pmids = self.scraper.search_pubmed(query, max_results=max_articles, date_range_years=10)
            logger.info(f"Found {len(pmids)} PMIDs")
            
            # Process articles
            articles = []
            for i, pmid in enumerate(pmids, 1):
                if i % 100 == 0:
                    logger.info(f"Processing article {i}/{len(pmids)}...")
                
                try:
                    article_data = self.scraper.fetch_article_details(pmid)
                    if article_data:
                        # Check open access
                        oa_info = self.scraper.oa_detector.check_open_access(
                            article_data.get('doi', ''),
                            pmid=pmid
                        )
                        article_data['access_type'] = 'open_access' if oa_info.get('is_open_access') else 'paywalled'
                        article_data['pdf_url'] = oa_info.get('pdf_url', '')
                        
                        # Calculate relevance using enhanced scorer
                        try:
                            enhanced_score, score_breakdown = self.scraper.enhanced_scorer.calculate_relevance_score(article_data)
                            article_data['relevance_score'] = enhanced_score
                            article_data['relevance_score_breakdown'] = score_breakdown
                        except Exception as e:
                            # Fallback to legacy scorer
                            logger.warning(f"Error calculating enhanced score, using legacy: {e}")
                            relevance_score = self.scraper.relevance_scorer.calculate_relevance_score(article_data)
                            article_data['relevance_score'] = relevance_score
                        
                        # Extract factors
                        text = f"{article_data.get('title', '')} {article_data.get('abstract', '')}"
                        factors = self.scraper.factor_extractor.extract_predictive_factors(text)
                        article_data['predictive_factors'] = factors
                        
                        articles.append(article_data)
                        
                except Exception as e:
                    logger.warning(f"Error processing PMID {pmid}: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return []
    
    def _build_comprehensive_query(self) -> str:
        """Build comprehensive PubMed search query"""
        # Systematic review-style query
        query = """
        (
            ("knee osteoarthritis"[Title/Abstract] OR "knee OA"[Title/Abstract] OR 
             "gonarthrosis"[Title/Abstract] OR "knee arthrosis"[Title/Abstract] OR
             (knee[Title/Abstract] AND osteoarthritis[Title/Abstract]))
        )
        AND
        (
            (progression[Title/Abstract] OR "total knee replacement"[Title/Abstract] OR 
             "total knee arthroplasty"[Title/Abstract] OR "TKR"[Title/Abstract] OR 
             "TKA"[Title/Abstract] OR "knee arthroplasty"[Title/Abstract] OR
             "knee replacement"[Title/Abstract] OR outcome[Title/Abstract] OR
             prediction[Title/Abstract] OR predictor[Title/Abstract] OR
             "risk factor"[Title/Abstract] OR "prognostic factor"[Title/Abstract])
        )
        AND
        (
            ("cohort study"[Publication Type] OR "prospective"[Title/Abstract] OR
             "retrospective"[Title/Abstract] OR "longitudinal"[Title/Abstract] OR
             "observational"[Title/Abstract] OR "registry"[Title/Abstract] OR
             "systematic review"[Publication Type] OR "meta-analysis"[Publication Type])
        )
        AND
        (
            (humans[Mesh] OR "human"[Title/Abstract])
        )
        """
        
        return query.strip().replace('\n', ' ')
    
    def import_asreview_results(self, project_path: str) -> bool:
        """
        Import ASReview screening results
        
        Args:
            project_path: Path to ASReview project
            
        Returns:
            True if successful
        """
        try:
            results = self.asreview.import_screening_results(project_path)
            if not results:
                logger.warning("No results imported from ASReview")
                return False
            
            logger.info(f"Imported {len(results)} screening results from ASReview")
            
            # Update database with screening results
            for result in results:
                pmid = result.get("pmid")
                if pmid:
                    # Update article in database
                    conn = self.database.db_path
                    # This would require updating the database class
                    # For now, log the results
                    logger.info(f"Article {pmid}: Relevant={result.get('asreview_relevant')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing ASReview results: {e}")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Literature Quality Workflow')
    parser.add_argument('--max-articles', type=int, default=5000, 
                       help='Maximum articles to fetch (default: 5000)')
    parser.add_argument('--use-asreview', action='store_true',
                       help='Use ASReview LAB for screening')
    
    args = parser.parse_args()
    
    workflow = LiteratureQualityWorkflow()
    
    # Run workflow
    stats = workflow.run_full_workflow(max_articles=args.max_articles, use_asreview=args.use_asreview)
    
    # Print statistics
    print("\n" + "=" * 80)
    print("Workflow Statistics")
    print("=" * 80)
    print(json.dumps(stats, indent=2))
    print("=" * 80)
