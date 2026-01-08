#!/usr/bin/env python3
"""
SQLite Database Manager for Literature Storage
Simple, local, free database for storing articles with PROBAST assessments.

No external services required - uses built-in SQLite.
"""

import os
import sqlite3
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LiteratureDatabase:
    """SQLite database manager for literature storage"""
    
    def __init__(self, db_path: str = "data/literature.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Create directory if path contains directories
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create if there's a directory path
            os.makedirs(db_dir, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main papers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            pmid TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            journal TEXT,
            authors TEXT,
            doi TEXT,
            publication_date TEXT,
            access_type TEXT,
            pdf_path TEXT,
            relevance_score INTEGER,
            probast_risk TEXT,
            probast_domain_1 TEXT,
            probast_domain_2 TEXT,
            probast_domain_3 TEXT,
            probast_domain_4 TEXT,
            probast_justification TEXT,
            assessment_date TEXT,
            assessment_method TEXT,
            used_in_model BOOLEAN DEFAULT 0,
            date_added TEXT,
            last_updated TEXT,
            predictive_factors TEXT,
            asreview_screened BOOLEAN DEFAULT 0,
            asreview_relevant BOOLEAN DEFAULT 0,
            relevance_score INTEGER,
            notes TEXT
        )
        ''')
        
        # Paywalled articles upload table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS paywalled_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pmid TEXT,
            title TEXT,
            pdf_path TEXT,
            uploaded_date TEXT,
            uploaded_by TEXT,
            probast_assessed BOOLEAN DEFAULT 0,
            probast_risk TEXT,
            notes TEXT,
            FOREIGN KEY (pmid) REFERENCES papers(pmid)
        )
        ''')
        
        # Indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_probast_risk ON papers(probast_risk)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_used_in_model ON papers(used_in_model)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_access_type ON papers(access_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relevance_score ON papers(relevance_score)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    def add_article(self, article: Dict, probast_assessment: Optional[Dict] = None) -> bool:
        """
        Add or update article in database
        
        Args:
            article: Article dictionary with metadata
            probast_assessment: Optional PROBAST assessment
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            pmid = article.get("pmid", "")
            if not pmid:
                logger.warning("Article missing PMID, skipping")
                return False
            
            # Prepare data
            now = datetime.now().isoformat()
            
            # Handle predictive factors (convert list to JSON string)
            factors = article.get("predictive_factors", [])
            factors_json = json.dumps(factors) if factors else None
            
            # PROBAST data
            probast_risk = probast_assessment.get("overall_risk", None) if probast_assessment else None
            probast_domain_1 = probast_assessment.get("domain_1_participants", None) if probast_assessment else None
            probast_domain_2 = probast_assessment.get("domain_2_predictors", None) if probast_assessment else None
            probast_domain_3 = probast_assessment.get("domain_3_outcome", None) if probast_assessment else None
            probast_domain_4 = probast_assessment.get("domain_4_analysis", None) if probast_assessment else None
            probast_justification = probast_assessment.get("justification", None) if probast_assessment else None
            assessment_date = probast_assessment.get("assessment_date", None) if probast_assessment else None
            assessment_method = probast_assessment.get("assessment_method", None) if probast_assessment else None
            
            # Check if article exists
            cursor.execute('SELECT pmid FROM papers WHERE pmid = ?', (pmid,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing article
                cursor.execute('''
                UPDATE papers SET
                    title = ?,
                    abstract = ?,
                    journal = ?,
                    authors = ?,
                    doi = ?,
                    publication_date = ?,
                    access_type = ?,
                    pdf_path = ?,
                    relevance_score = ?,
                    probast_risk = COALESCE(?, probast_risk),
                    probast_domain_1 = COALESCE(?, probast_domain_1),
                    probast_domain_2 = COALESCE(?, probast_domain_2),
                    probast_domain_3 = COALESCE(?, probast_domain_3),
                    probast_domain_4 = COALESCE(?, probast_domain_4),
                    probast_justification = COALESCE(?, probast_justification),
                    assessment_date = COALESCE(?, assessment_date),
                    assessment_method = COALESCE(?, assessment_method),
                    predictive_factors = COALESCE(?, predictive_factors),
                    last_updated = ?
                WHERE pmid = ?
                ''', (
                    article.get("title"),
                    article.get("abstract"),
                    article.get("journal"),
                    article.get("authors"),
                    article.get("doi"),
                    article.get("publication_date"),
                    article.get("access_type"),
                    article.get("pdf_path"),
                    article.get("relevance_score"),
                    probast_risk,
                    probast_domain_1,
                    probast_domain_2,
                    probast_domain_3,
                    probast_domain_4,
                    probast_justification,
                    assessment_date,
                    assessment_method,
                    factors_json,
                    now,
                    pmid
                ))
            else:
                # Insert new article
                cursor.execute('''
                INSERT INTO papers (
                    pmid, title, abstract, journal, authors, doi, publication_date,
                    access_type, pdf_path, relevance_score,
                    probast_risk, probast_domain_1, probast_domain_2,
                    probast_domain_3, probast_domain_4, probast_justification,
                    assessment_date, assessment_method, predictive_factors,
                    date_added, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pmid,
                    article.get("title"),
                    article.get("abstract"),
                    article.get("journal"),
                    article.get("authors"),
                    article.get("doi"),
                    article.get("publication_date"),
                    article.get("access_type"),
                    article.get("pdf_path"),
                    article.get("relevance_score"),
                    probast_risk,
                    probast_domain_1,
                    probast_domain_2,
                    probast_domain_3,
                    probast_domain_4,
                    probast_justification,
                    assessment_date,
                    assessment_method,
                    factors_json,
                    now,
                    now
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Article {pmid} added/updated in database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding article to database: {e}")
            return False
    
    def get_articles_by_probast_risk(self, risk_level: str = "Low") -> List[Dict]:
        """
        Get articles by PROBAST risk level
        
        Args:
            risk_level: "Low", "Moderate", "High", or "Unclear"
            
        Returns:
            List of article dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM papers WHERE probast_risk = ?
        ORDER BY relevance_score DESC, date_added DESC
        ''', (risk_level,))
        
        rows = cursor.fetchall()
        articles = [self._row_to_dict(row) for row in rows]
        
        conn.close()
        return articles
    
    def get_usable_articles(self) -> List[Dict]:
        """
        Get articles usable for model (Low Risk PROBAST)
        
        Returns:
            List of article dictionaries with Low Risk PROBAST
        """
        return self.get_articles_by_probast_risk("Low")
    
    def get_articles_by_score(self, min_score: int = 60, max_articles: int = None) -> List[Dict]:
        """
        Get articles by relevance score (automated filtering)
        
        Args:
            min_score: Minimum relevance score (0-100)
            max_articles: Maximum number of articles to return
            
        Returns:
            List of articles sorted by score
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
        SELECT * FROM papers 
        WHERE relevance_score >= ?
        ORDER BY relevance_score DESC
        '''
        
        if max_articles:
            query += f' LIMIT {max_articles}'
        
        cursor.execute(query, (min_score,))
        rows = cursor.fetchall()
        articles = [self._row_to_dict(row) for row in rows]
        
        conn.close()
        return articles
    
    def get_paywalled_articles(self) -> List[Dict]:
        """Get all paywalled articles"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM papers WHERE access_type = 'paywalled'
        ORDER BY relevance_score DESC
        ''')
        
        rows = cursor.fetchall()
        articles = [self._row_to_dict(row) for row in rows]
        
        conn.close()
        return articles
    
    def add_paywalled_upload(self, pmid: str, pdf_path: str, uploaded_by: str = "user") -> bool:
        """
        Record paywalled article upload
        
        Args:
            pmid: PubMed ID
            pdf_path: Path to uploaded PDF
            uploaded_by: Username or identifier
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO paywalled_uploads (pmid, pdf_path, uploaded_date, uploaded_by)
            VALUES (?, ?, ?, ?)
            ''', (pmid, pdf_path, now, uploaded_by))
            
            # Update main papers table if article exists
            cursor.execute('''
            UPDATE papers SET pdf_path = ?, access_type = 'uploaded'
            WHERE pmid = ?
            ''', (pdf_path, pmid))
            
            conn.commit()
            conn.close()
            logger.info(f"Paywalled upload recorded for PMID {pmid}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording paywalled upload: {e}")
            return False
    
    def mark_as_used_in_model(self, pmid: str) -> bool:
        """Mark article as used in model"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE papers SET used_in_model = 1 WHERE pmid = ?
            ''', (pmid,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error marking article as used: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total articles
        cursor.execute('SELECT COUNT(*) FROM papers')
        stats['total_articles'] = cursor.fetchone()[0]
        
        # By PROBAST risk
        for risk in ['Low', 'Moderate', 'High', 'Unclear']:
            cursor.execute('SELECT COUNT(*) FROM papers WHERE probast_risk = ?', (risk,))
            stats[f'probast_{risk.lower()}_risk'] = cursor.fetchone()[0]
        
        # Usable for model
        cursor.execute('SELECT COUNT(*) FROM papers WHERE probast_risk = "Low" AND used_in_model = 1')
        stats['used_in_model'] = cursor.fetchone()[0]
        
        # Access types
        cursor.execute('SELECT access_type, COUNT(*) FROM papers GROUP BY access_type')
        stats['by_access_type'] = dict(cursor.fetchall())
        
        conn.close()
        return stats
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert SQLite row to dictionary"""
        article = dict(row)
        
        # Parse JSON fields
        if article.get('predictive_factors'):
            try:
                article['predictive_factors'] = json.loads(article['predictive_factors'])
            except:
                article['predictive_factors'] = []
        else:
            article['predictive_factors'] = []
        
        return article


if __name__ == "__main__":
    # Test database
    db = LiteratureDatabase("test_literature.db")
    
    test_article = {
        "pmid": "12345678",
        "title": "Test Article",
        "abstract": "Test abstract",
        "journal": "Test Journal",
        "relevance_score": 85,
        "access_type": "open_access"
    }
    
    test_assessment = {
        "overall_risk": "Low",
        "domain_1_participants": "Low",
        "domain_2_predictors": "Low",
        "domain_3_outcome": "Low",
        "domain_4_analysis": "Low",
        "assessment_method": "automated"
    }
    
    db.add_article(test_article, test_assessment)
    
    stats = db.get_statistics()
    print(json.dumps(stats, indent=2))
    
    usable = db.get_usable_articles()
    print(f"\nUsable articles: {len(usable)}")
    
    # Cleanup
    os.remove("test_literature.db")
