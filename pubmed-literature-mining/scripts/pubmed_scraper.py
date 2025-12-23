#!/usr/bin/env python3
"""
PubMed Literature Mining Scraper
Queries PubMed API for knee osteoarthritis progression studies and stores metadata in Xata.
"""

import os
import sys
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from scripts.google_sheets_storage import get_storage_client
from scripts.open_access_detector import OpenAccessDetector
from scripts.relevance_scoring import RelevanceScorer
from scripts.factor_extraction import FactorExtractor

# Load environment variables
load_dotenv()

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pubmed_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PubMedScraper:
    """Main scraper class for PubMed API integration"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    MAX_RETRIES = 3
    REQUEST_DELAY = 0.34  # ~3 requests/second max
    
    def __init__(self):
        self.email = os.getenv('PUBMED_EMAIL', 'parker@stroomai.com')
        self.tool = os.getenv('PUBMED_TOOL', 'PubMedLiteratureMining')
        self.max_articles = int(os.getenv('MAX_ARTICLES_PER_RUN', '100'))
        self.storage = get_storage_client()  # Google Sheets if available, else file storage
        self.oa_detector = OpenAccessDetector()
        self.relevance_scorer = RelevanceScorer()
        self.factor_extractor = FactorExtractor()
        
    def _make_request(self, url: str, params: Dict, retry_count: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic and rate limiting"""
        try:
            time.sleep(self.REQUEST_DELAY)  # Rate limiting
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if retry_count < self.MAX_RETRIES:
                wait_time = (2 ** retry_count) * 5  # Exponential backoff
                logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
                return self._make_request(url, params, retry_count + 1)
            else:
                logger.error(f"Request failed after {self.MAX_RETRIES} retries: {e}")
                return None
    
    def search_pubmed(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search PubMed and return list of PMIDs
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            
        Returns:
            List of PMID strings
        """
        search_url = f"{self.BASE_URL}/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'email': self.email,
            'tool': self.tool,
            'sort': 'pub_date',  # Most recent first
            'datetype': 'pdat',
            'mindate': (datetime.now() - timedelta(days=5*365)).strftime('%Y/%m/%d'),
            'maxdate': datetime.now().strftime('%Y/%m/%d')
        }
        
        response = self._make_request(search_url, params)
        if not response:
            return []
        
        try:
            data = response.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
            logger.info(f"Found {len(pmids)} articles matching query")
            return pmids
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing search results: {e}")
            return []
    
    def fetch_article_details(self, pmid: str) -> Optional[Dict]:
        """
        Fetch detailed article information from PubMed
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Dictionary with article details or None if error
        """
        fetch_url = f"{self.BASE_URL}/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': pmid,
            'retmode': 'xml',
            'email': self.email,
            'tool': self.tool
        }
        
        response = self._make_request(fetch_url, params)
        if not response:
            return None
        
        try:
            root = ET.fromstring(response.content)
            article = root.find('.//PubmedArticle')
            if article is None:
                logger.warning(f"No article data found for PMID {pmid}")
                return None
            
            # Extract article data
            medline_citation = article.find('.//MedlineCitation')
            pubmed_data = article.find('.//PubmedData')
            
            # Title
            title_elem = medline_citation.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else ""
            
            # Abstract
            abstract_elems = medline_citation.findall('.//AbstractText')
            abstract = " ".join([elem.text or "" for elem in abstract_elems])
            
            # Authors
            author_list = medline_citation.find('.//AuthorList')
            authors = []
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.find('LastName')
                    first_name = author.find('ForeName')
                    if last_name is not None:
                        name = last_name.text or ""
                        if first_name is not None:
                            name += f", {first_name.text or ''}"
                        authors.append(name)
            authors_str = "; ".join(authors) if authors else ""
            
            # Journal
            journal_elem = medline_citation.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else ""
            
            # Publication date
            pub_date_elem = medline_citation.find('.//PubDate')
            pub_date = None
            if pub_date_elem is not None:
                year = pub_date_elem.find('Year')
                month = pub_date_elem.find('Month')
                day = pub_date_elem.find('Day')
                if year is not None:
                    date_str = year.text or ""
                    if month is not None:
                        date_str += f"-{month.text or '01'}"
                    else:
                        date_str += "-01"
                    if day is not None:
                        date_str += f"-{day.text or '01'}"
                    else:
                        date_str += "-01"
                    try:
                        pub_date = datetime.strptime(date_str, "%Y-%m-%d").isoformat()
                    except ValueError:
                        pub_date = datetime.now().isoformat()
            
            # DOI
            doi = ""
            article_id_list = pubmed_data.find('.//ArticleIdList') if pubmed_data is not None else None
            if article_id_list is not None:
                for article_id in article_id_list.findall('.//ArticleId'):
                    if article_id.get('IdType') == 'doi':
                        doi = article_id.text or ""
                        break
            
            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'authors': authors_str,
                'journal': journal,
                'doi': doi,
                'publication_date': pub_date or datetime.now().isoformat()
            }
            
        except ET.ParseError as e:
            logger.error(f"Error parsing XML for PMID {pmid}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing PMID {pmid}: {e}")
            return None
    
    def process_article(self, pmid: str) -> bool:
        """
        Process a single article: fetch, check OA, score, extract factors, store
        
        Args:
            pmid: PubMed ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if already exists in storage
            existing = self.storage.get_article_by_pmid(pmid)
            if existing:
                # Check if article has missing details (title, journal, etc.)
                has_details = (
                    existing.get('title') and 
                    existing.get('title') != 'No title' and
                    existing.get('journal') and
                    existing.get('journal') != 'Unknown Journal'
                )
                
                if has_details:
                    logger.info(f"Article {pmid} already exists with full details, skipping")
                    return True
                else:
                    logger.info(f"Article {pmid} exists but missing details, will update")
                    # Continue to fetch and update
            
            # Fetch article details
            article_data = self.fetch_article_details(pmid)
            if not article_data:
                logger.warning(f"Could not fetch details for PMID {pmid}")
                return False
            
            # Check open access status
            oa_info = self.oa_detector.check_open_access(
                article_data.get('doi', ''),
                pmid=pmid
            )
            article_data['access_type'] = 'open_access' if oa_info.get('is_open_access') else 'paywalled'
            article_data['pdf_url'] = oa_info.get('pdf_url', '')
            
            # Download PDF if open access
            if oa_info.get('is_open_access') and oa_info.get('pdf_url'):
                pdf_path = self.oa_detector.download_pdf(oa_info['pdf_url'], pmid)
                if pdf_path:
                    article_data['pdf_path'] = pdf_path
            
            # Calculate relevance score
            relevance_score = self.relevance_scorer.calculate_relevance_score(article_data)
            article_data['relevance_score'] = relevance_score
            
            # Extract predictive factors
            text = article_data.get('abstract', '')
            if article_data.get('pdf_path'):
                try:
                    full_text = self.oa_detector.extract_pdf_text(article_data['pdf_path'])
                    text += " " + full_text
                except Exception as e:
                    logger.warning(f"Could not extract PDF text for {pmid}: {e}")
            
            predictive_factors = self.factor_extractor.extract_predictive_factors(text)
            article_data['predictive_factors'] = predictive_factors
            
            # Set processing status
            article_data['processing_status'] = 'processed'
            article_data['created_at'] = datetime.now().isoformat()
            article_data['updated_at'] = datetime.now().isoformat()
            
            # Store in file storage
            success = self.storage.insert_article(article_data)
            if success:
                logger.info(f"Successfully processed PMID {pmid} (score: {relevance_score})")
            else:
                logger.error(f"Failed to store PMID {pmid}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing article {pmid}: {e}", exc_info=True)
            # Store error status
            try:
                error_data = {
                    'pmid': pmid,
                    'processing_status': 'error',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                self.storage.insert_article(error_data)
            except:
                pass
            return False
    
    def run(self):
        """Main execution method"""
        logger.info("Starting PubMed scraper")
        
        # Build search query - less restrictive to find more articles
        # Try with publication type filters first
        query = '("knee osteoarthritis" OR "knee OA") AND ("progression" OR "total knee replacement" OR "arthroplasty" OR "TKR") AND (human[Filter]) AND (Clinical Trial[ptyp] OR Cohort Studies[ptyp] OR Systematic Review[ptyp])'
        
        # Search PubMed
        pmids = self.search_pubmed(query, max_results=self.max_articles)
        
        # If no results with strict filters, try without publication type filter
        if not pmids:
            logger.info("No articles found with strict filters, trying broader search...")
            query = '("knee osteoarthritis" OR "knee OA") AND ("progression" OR "total knee replacement" OR "arthroplasty" OR "TKR") AND (human[Filter])'
            pmids = self.search_pubmed(query, max_results=self.max_articles)
        
        # If still no results, try even broader (just OA progression)
        if not pmids:
            logger.info("Still no articles, trying even broader search...")
            query = '("knee osteoarthritis" OR "knee OA") AND ("progression" OR "total knee replacement" OR "arthroplasty")'
            pmids = self.search_pubmed(query, max_results=self.max_articles)
        
        if not pmids:
            logger.warning("No articles found with any search query")
            return
        
        # Process each article
        processed = 0
        errors = 0
        
        for pmid in pmids:
            try:
                if self.process_article(pmid):
                    processed += 1
                else:
                    errors += 1
            except Exception as e:
                logger.error(f"Unexpected error processing {pmid}: {e}")
                errors += 1
            
            # Log progress
            if (processed + errors) % 10 == 0:
                logger.info(f"Progress: {processed} processed, {errors} errors")
        
        logger.info(f"Scraping complete: {processed} processed, {errors} errors")
        
        # Write daily summary
        self._write_daily_summary(processed, errors, len(pmids))
    
    def _write_daily_summary(self, processed: int, errors: int, total: int):
        """Write daily summary to log file"""
        try:
            summary = {
                'date': datetime.now().isoformat(),
                'total_found': total,
                'processed': processed,
                'errors': errors,
                'success_rate': (processed / total * 100) if total > 0 else 0
            }
            
            os.makedirs('logs', exist_ok=True)
            with open('logs/daily_summary.json', 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Also write simple text summary
            with open('logs/daily_count.txt', 'w') as f:
                f.write(str(processed))
            
            try:
                paywalled = self.storage.count_paywalled_articles()
                with open('logs/paywalled_count.txt', 'w') as f:
                    f.write(str(paywalled))
            except Exception as e:
                logger.warning(f"Could not count paywalled articles: {e}")
                with open('logs/paywalled_count.txt', 'w') as f:
                    f.write('0')
            
            try:
                factors = self.storage.count_predictive_factors()
                with open('logs/factors_count.txt', 'w') as f:
                    f.write(str(factors))
            except Exception as e:
                logger.warning(f"Could not count predictive factors: {e}")
                with open('logs/factors_count.txt', 'w') as f:
                    f.write('0')
        except Exception as e:
            logger.error(f"Error writing daily summary: {e}")


if __name__ == "__main__":
    scraper = PubMedScraper()
    scraper.run()

