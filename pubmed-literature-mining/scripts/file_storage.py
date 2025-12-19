#!/usr/bin/env python3
"""
File-Based Storage System
Replaces Xata with free file-based storage using JSON files in the repository.
100% free, version-controlled, and perfect for GitHub Actions.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class FileStorage:
    """File-based storage using JSON files - 100% free alternative to Xata"""
    
    def __init__(self, data_dir: str = 'data/articles'):
        """
        Initialize file storage
        
        Args:
            data_dir: Directory to store article JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Index file for fast lookups
        self.index_file = self.data_dir / 'index.json'
        self._load_index()
    
    def _load_index(self):
        """Load or create index file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading index, creating new one: {e}")
                self.index = {}
        else:
            self.index = {}
    
    def _save_index(self):
        """Save index file"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def _get_article_file(self, pmid: str) -> Path:
        """Get file path for an article"""
        # Store in subdirectories to avoid too many files in one directory
        # Use first 2 digits of PMID for directory structure
        subdir = pmid[:2] if len(pmid) >= 2 else '00'
        article_dir = self.data_dir / subdir
        article_dir.mkdir(exist_ok=True)
        return article_dir / f"{pmid}.json"
    
    def get_article_by_pmid(self, pmid: str) -> Optional[Dict]:
        """Get article by PMID"""
        article_file = self._get_article_file(pmid)
        if not article_file.exists():
            return None
        
        try:
            with open(article_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading article {pmid}: {e}")
            return None
    
    def insert_article(self, article_data: Dict) -> bool:
        """
        Insert or update article
        
        Args:
            article_data: Dictionary with article fields
            
        Returns:
            True if successful
        """
        if 'pmid' not in article_data:
            logger.error("PMID is required")
            return False
        
        pmid = article_data['pmid']
        article_file = self._get_article_file(pmid)
        
        try:
            # Load existing article if it exists
            existing = self.get_article_by_pmid(pmid)
            if existing:
                # Merge with existing data (update)
                article_data = {**existing, **article_data}
                article_data['updated_at'] = datetime.now().isoformat()
            else:
                # New article
                article_data['created_at'] = datetime.now().isoformat()
                article_data['updated_at'] = datetime.now().isoformat()
            
            # Save article
            with open(article_file, 'w') as f:
                json.dump(article_data, f, indent=2, ensure_ascii=False)
            
            # Update index
            self.index[pmid] = {
                'pmid': pmid,
                'title': article_data.get('title', '')[:100],  # Truncate for index
                'relevance_score': article_data.get('relevance_score', 0),
                'access_type': article_data.get('access_type', 'unknown'),
                'journal': article_data.get('journal', ''),
                'updated_at': article_data.get('updated_at', '')
            }
            self._save_index()
            
            return True
        except Exception as e:
            logger.error(f"Error saving article {pmid}: {e}")
            return False
    
    def query_articles(self, filter_func=None, limit: int = 100) -> List[Dict]:
        """
        Query articles with optional filter function
        
        Args:
            filter_func: Function that takes article dict and returns bool
            limit: Maximum number of results
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        # Load all articles from index
        for pmid, index_data in self.index.items():
            if len(articles) >= limit:
                break
            
            article = self.get_article_by_pmid(pmid)
            if not article:
                continue
            
            # Apply filter if provided
            if filter_func is None or filter_func(article):
                articles.append(article)
        
        return articles
    
    def get_high_relevance_articles(self, threshold: int = 70) -> List[Dict]:
        """Get articles with relevance score >= threshold"""
        def filter_func(article):
            return article.get('relevance_score', 0) >= threshold
        return self.query_articles(filter_func=filter_func)
    
    def get_paywalled_articles(self, threshold: int = 70) -> List[Dict]:
        """Get paywalled articles with relevance >= threshold"""
        def filter_func(article):
            return (article.get('access_type') == 'paywalled' and 
                   article.get('relevance_score', 0) >= threshold)
        return self.query_articles(filter_func=filter_func)
    
    def count_paywalled_articles(self) -> int:
        """Count paywalled articles"""
        def filter_func(article):
            return article.get('access_type') == 'paywalled'
        return len(self.query_articles(filter_func=filter_func, limit=10000))
    
    def count_predictive_factors(self) -> int:
        """Count total number of predictive factors extracted"""
        total = 0
        for pmid in self.index.keys():
            article = self.get_article_by_pmid(pmid)
            if article:
                factors = article.get('predictive_factors', [])
                if isinstance(factors, list):
                    total += len(factors)
        return total
    
    def get_all_articles(self) -> List[Dict]:
        """Get all articles (for analysis)"""
        return self.query_articles(limit=10000)
    
    def search_articles(self, search_term: str, limit: int = 100) -> List[Dict]:
        """Search articles by title or abstract"""
        search_lower = search_term.lower()
        def filter_func(article):
            title = article.get('title', '').lower()
            abstract = article.get('abstract', '').lower()
            return search_lower in title or search_lower in abstract
        return self.query_articles(filter_func=filter_func, limit=limit)

