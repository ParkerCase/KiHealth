#!/usr/bin/env python3
"""
Xata Database Client
Handles all database operations for storing and retrieving PubMed articles.
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger(__name__)


class XataClient:
    """Client for Xata database operations"""
    
    def __init__(self):
        self.api_key = os.getenv('XATA_API_KEY')
        self.database_url = os.getenv('XATA_DATABASE_URL')
        self.table_name = 'pubmed_articles'
        
        if not self.api_key or not self.database_url:
            logger.warning("Xata credentials not found. Database operations will be skipped.")
            self.enabled = False
        else:
            self.enabled = True
            # Extract database and branch from URL
            # Format: https://{workspace}.{region}.xata.sh/db/{database}:{branch}
            try:
                url_parts = self.database_url.rstrip('/')
                if ':' in url_parts:
                    # Has branch specified
                    base, branch = url_parts.rsplit(':', 1)
                    self.base_url = base
                    self.branch = branch
                else:
                    # No branch, use main
                    self.base_url = url_parts
                    self.branch = 'main'
                
                # Ensure base_url ends with /db/{database}
                if not self.base_url.endswith('/db/'):
                    # Extract database name from URL
                    if '/db/' in self.base_url:
                        db_part = self.base_url.split('/db/')[-1]
                        workspace_part = self.base_url.split('/db/')[0]
                        self.base_url = f"{workspace_part}/db/{db_part}"
            except Exception as e:
                logger.error(f"Error parsing database URL: {e}")
                self.enabled = False
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to Xata API"""
        if not self.enabled:
            logger.warning("Xata not enabled, skipping request")
            return None
        
        # Xata API format: https://{workspace}.{region}.xata.sh/db/{database}:{branch}/tables/{table}/{endpoint}
        url = f"{self.base_url}:{self.branch}/tables/{self.table_name}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params or data, timeout=30)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, params=params, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data, params=params, timeout=30)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Xata API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    logger.error(f"Response: {e.response.text}")
                except:
                    pass
            return None
    
    def get_article_by_pmid(self, pmid: str) -> Optional[Dict]:
        """Get article by PMID (primary key)"""
        if not self.enabled:
            return None
        
        result = self._make_request('GET', f'/{pmid}')
        # Xata returns record in 'record' field or directly
        if result:
            return result.get('record', result)
        return None
    
    def insert_article(self, article_data: Dict) -> bool:
        """
        Insert or update article in database
        
        Args:
            article_data: Dictionary with article fields
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.warning("Xata not enabled, skipping insert")
            return False
        
        # Ensure required fields
        if 'pmid' not in article_data:
            logger.error("PMID is required")
            return False
        
        # Use PATCH for upsert (insert or update)
        result = self._make_request('PATCH', f'/{article_data["pmid"]}', data=article_data)
        return result is not None
    
    def query_articles(self, filter_dict: Optional[Dict] = None, limit: int = 100) -> List[Dict]:
        """
        Query articles with optional filter
        
        Args:
            filter_dict: Xata filter expression
            limit: Maximum number of results
            
        Returns:
            List of article dictionaries
        """
        if not self.enabled:
            return []
        
        query_data = {'columns': ['*'], 'page': {'size': limit}}
        if filter_dict:
            query_data['filter'] = filter_dict
        
        result = self._make_request('POST', '/query', data=query_data)
        if result and 'records' in result:
            return result['records']
        return []
    
    def get_high_relevance_articles(self, threshold: int = 70) -> List[Dict]:
        """Get articles with relevance score >= threshold"""
        filter_expr = {
            'relevance_score': {'$ge': threshold}
        }
        return self.query_articles(filter_expr)
    
    def get_paywalled_articles(self, threshold: int = 70) -> List[Dict]:
        """Get paywalled articles with relevance >= threshold"""
        filter_expr = {
            '$and': [
                {'access_type': 'paywalled'},
                {'relevance_score': {'$ge': threshold}}
            ]
        }
        return self.query_articles(filter_expr)
    
    def count_paywalled_articles(self) -> int:
        """Count paywalled articles"""
        articles = self.get_paywalled_articles(threshold=0)
        return len(articles)
    
    def count_predictive_factors(self) -> int:
        """Count total number of predictive factors extracted"""
        articles = self.query_articles(limit=1000)
        total = 0
        for article in articles:
            factors = article.get('predictive_factors', [])
            if isinstance(factors, list):
                total += len(factors)
        return total

