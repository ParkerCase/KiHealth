#!/usr/bin/env python3
"""
Google Sheets Storage System for Python
Replaces file storage with Google Sheets for easy monitoring
100% free, easy to view and filter data
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import Google Sheets libraries
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    logger.warning("Google Sheets libraries not installed. Install with: pip install gspread google-auth")


class GoogleSheetsStorage:
    """Google Sheets storage using gspread"""
    
    def __init__(self, sheet_name: str = "oa_articles"):
        """
        Initialize Google Sheets storage
        
        Args:
            sheet_name: Name of the sheet tab to use
        """
        self.sheet_name = sheet_name
        self.client = None
        self.spreadsheet = None
        self.sheet = None
        self.initialized = False
        
    def _initialize(self):
        """Initialize Google Sheets connection"""
        if self.initialized:
            return
        
        if not GOOGLE_SHEETS_AVAILABLE:
            raise ImportError(
                "Google Sheets libraries not installed. "
                "Install with: pip install gspread google-auth"
            )
        
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        service_account_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
        private_key = os.getenv('GOOGLE_PRIVATE_KEY', '').replace('\\n', '\n')
        
        if not all([sheet_id, service_account_email, private_key]):
            raise ValueError(
                "Google Sheets credentials not found. "
                "Set GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_EMAIL, and GOOGLE_PRIVATE_KEY"
            )
        
        try:
            # Try to parse as JSON first (if full service account JSON provided)
            try:
                creds_json = json.loads(private_key) if private_key.startswith('{') else None
                if creds_json and 'type' in creds_json:
                    # Full service account JSON provided
                    scopes = ['https://www.googleapis.com/auth/spreadsheets']
                    creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
                else:
                    # Only private key provided, construct minimal creds dict
                    creds_dict = {
                        "type": "service_account",
                        "project_id": "oa-literature-mining",
                        "private_key_id": "dummy",
                        "private_key": private_key,
                        "client_email": service_account_email,
                        "client_id": "dummy",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{service_account_email}"
                    }
                    scopes = ['https://www.googleapis.com/auth/spreadsheets']
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            except (json.JSONDecodeError, ValueError):
                # Not JSON, use as private key only
                creds_dict = {
                    "type": "service_account",
                    "project_id": "oa-literature-mining",
                    "private_key_id": "dummy",
                    "private_key": private_key,
                    "client_email": service_account_email,
                    "client_id": "dummy",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{service_account_email}"
                }
                scopes = ['https://www.googleapis.com/auth/spreadsheets']
                creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            
            # Initialize client
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(sheet_id)
            
            # Get or create sheet
            try:
                self.sheet = self.spreadsheet.worksheet(self.sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                # Create new sheet
                self.sheet = self.spreadsheet.add_worksheet(
                    title=self.sheet_name,
                    rows=1000,
                    cols=20
                )
                # Add headers
                self._setup_headers()
            
            self.initialized = True
            logger.info(f"Connected to Google Sheets: {self.sheet_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {e}")
            raise
    
    def _setup_headers(self):
        """Set up column headers"""
        headers = [
            'id', 'pmid', 'title', 'abstract', 'authors', 'journal',
            'publication_date', 'doi', 'access_type', 'relevance_score',
            'predictive_factors', 'pdf_url', 'processing_status',
            'created_at', 'updated_at'
        ]
        self.sheet.append_row(headers)
    
    def get_article_by_pmid(self, pmid: str) -> Optional[Dict]:
        """Get article by PMID"""
        self._initialize()
        
        try:
            # Search for row with matching PMID
            cell = self.sheet.find(pmid, in_column=2)  # Column 2 is pmid
            if cell:
                row = self.sheet.row_values(cell.row)
                headers = self.sheet.row_values(1)
                return dict(zip(headers, row))
        except gspread.exceptions.CellNotFound:
            pass
        except Exception as e:
            logger.error(f"Error getting article {pmid}: {e}")
        
        return None
    
    def insert_article(self, article_data: Dict) -> bool:
        """
        Insert or update article
        
        Args:
            article_data: Dictionary with article fields
            
        Returns:
            True if successful
        """
        self._initialize()
        
        if 'pmid' not in article_data:
            logger.error("PMID is required")
            return False
        
        pmid = article_data['pmid']
        
        try:
            # Check if article exists
            existing = self.get_article_by_pmid(pmid)
            
            # Prepare row data
            row_data = [
                article_data.get('pmid', ''),  # id (use pmid as id)
                article_data.get('pmid', ''),
                article_data.get('title', ''),
                article_data.get('abstract', '')[:5000],  # Limit abstract length
                article_data.get('authors', ''),
                article_data.get('journal', ''),
                article_data.get('publication_date', ''),
                article_data.get('doi', ''),
                article_data.get('access_type', 'unknown'),
                article_data.get('relevance_score', 0),
                json.dumps(article_data.get('predictive_factors', [])),  # JSON string
                article_data.get('pdf_url', ''),
                article_data.get('processing_status', 'processed'),
                article_data.get('created_at', datetime.now().isoformat()),
                article_data.get('updated_at', datetime.now().isoformat())
            ]
            
            if existing:
                # Update existing row - only update fields that have new data
                cell = self.sheet.find(pmid, in_column=2)
                if cell:
                    # Get headers to map columns correctly
                    headers = self.sheet.row_values(1)
                    current_row = self.sheet.row_values(cell.row)
                    
                    # Map headers to column indices
                    header_map = {h: i+1 for i, h in enumerate(headers)}
                    
                    # Define which fields to update (only if new value is better)
                    fields_to_update = {
                        'title': article_data.get('title', ''),
                        'abstract': article_data.get('abstract', '')[:5000],
                        'authors': article_data.get('authors', ''),
                        'journal': article_data.get('journal', ''),
                        'publication_date': article_data.get('publication_date', ''),
                        'doi': article_data.get('doi', ''),
                        'access_type': article_data.get('access_type', ''),
                        'relevance_score': article_data.get('relevance_score', 0),
                        'predictive_factors': json.dumps(article_data.get('predictive_factors', [])),
                        'pdf_url': article_data.get('pdf_url', ''),
                        'processing_status': article_data.get('processing_status', 'processed'),
                    }
                    
                    # Update fields only if new value is better (not empty, or existing is empty)
                    for field_name, new_value in fields_to_update.items():
                        if field_name in header_map:
                            col_idx = header_map[field_name]
                            current_value = current_row[col_idx - 1] if col_idx <= len(current_row) else ''
                            
                            # Update if:
                            # 1. New value is not empty AND (current is empty OR new is better)
                            # 2. For relevance_score, always update if new is higher
                            should_update = False
                            
                            if field_name == 'relevance_score':
                                # Always update if new score is higher
                                new_score = float(new_value) if new_value else 0
                                current_score = float(current_value) if current_value else 0
                                should_update = new_score > current_score
                            elif field_name in ['title', 'journal', 'authors']:
                                # Update if current is empty/missing or new is better
                                should_update = (
                                    new_value and str(new_value).strip() and
                                    (not current_value or not str(current_value).strip() or
                                     current_value in ['No title', 'Unknown Journal', ''])
                                )
                            else:
                                # Update if new value exists and current is empty
                                should_update = (
                                    new_value and str(new_value).strip() and
                                    (not current_value or not str(current_value).strip())
                                )
                            
                            if should_update:
                                self.sheet.update_cell(cell.row, col_idx, new_value)
                    
                    # Always update updated_at timestamp
                    if 'updated_at' in header_map:
                        self.sheet.update_cell(cell.row, header_map['updated_at'], datetime.now().isoformat())
                    
                    logger.info(f"Updated article {pmid} in Google Sheets")
            else:
                # Insert new row
                self.sheet.append_row(row_data)
                logger.info(f"Inserted article {pmid} into Google Sheets")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving article {pmid} to Google Sheets: {e}")
            return False
    
    def get_paywalled_articles(self, threshold: int = 70) -> List[Dict]:
        """Get paywalled articles with relevance >= threshold"""
        self._initialize()
        
        try:
            articles = []
            all_records = self.sheet.get_all_records()
            
            logger.info(f"Checking {len(all_records)} records for paywalled articles...")
            
            for record in all_records:
                access_type = record.get('access_type', '').lower().strip()
                relevance_score = record.get('relevance_score', 0)
                
                # Try to convert relevance_score to float
                try:
                    score = float(relevance_score) if relevance_score else 0
                except (ValueError, TypeError):
                    score = 0
                
                # Check if paywalled (case-insensitive)
                is_paywalled = access_type == 'paywalled'
                
                # Debug logging for first few records
                if len(articles) < 3:
                    logger.debug(f"Record: access_type='{access_type}', score={score}, is_paywalled={is_paywalled}")
                
                if is_paywalled and score >= threshold:
                    articles.append(record)
            
            logger.info(f"Found {len(articles)} paywalled articles with score >= {threshold}")
            return articles
        except Exception as e:
            logger.error(f"Error getting paywalled articles: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def get_high_relevance_articles(self, threshold: int = 70) -> List[Dict]:
        """Get articles with relevance score >= threshold"""
        self._initialize()
        
        try:
            articles = []
            all_records = self.sheet.get_all_records()
            
            for record in all_records:
                if float(record.get('relevance_score', 0)) >= threshold:
                    articles.append(record)
            
            return articles
        except Exception as e:
            logger.error(f"Error getting high relevance articles: {e}")
            return []
    
    def count_paywalled_articles(self) -> int:
        """Count paywalled articles"""
        self._initialize()
        
        try:
            count = 0
            all_records = self.sheet.get_all_records()
            
            for record in all_records:
                if record.get('access_type') == 'paywalled':
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error counting paywalled articles: {e}")
            return 0
    
    def count_predictive_factors(self) -> int:
        """Count total number of predictive factors"""
        self._initialize()
        
        try:
            total = 0
            all_records = self.sheet.get_all_records()
            
            for record in all_records:
                factors_json = record.get('predictive_factors', '[]')
                try:
                    factors = json.loads(factors_json) if isinstance(factors_json, str) else factors_json
                    if isinstance(factors, list):
                        total += len(factors)
                except:
                    pass
            
            return total
        except Exception as e:
            logger.error(f"Error counting predictive factors: {e}")
            return 0


class HybridStorage:
    """Hybrid storage that checks both Google Sheets and file storage"""
    
    def __init__(self):
        self.sheets_storage = None
        self.file_storage = None
        
        # Try to initialize Google Sheets
        if (os.getenv('GOOGLE_SHEET_ID') and 
            os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL') and 
            os.getenv('GOOGLE_PRIVATE_KEY')):
            try:
                self.sheets_storage = GoogleSheetsStorage()
            except Exception as e:
                logger.warning(f"Failed to initialize Google Sheets: {e}")
        
        # Always have file storage as fallback
        from scripts.file_storage import FileStorage
        self.file_storage = FileStorage()
    
    def get_article_by_pmid(self, pmid: str):
        """Get article from Google Sheets first, then file storage"""
        # Try Google Sheets first
        if self.sheets_storage:
            try:
                article = self.sheets_storage.get_article_by_pmid(pmid)
                if article:
                    return article
            except Exception as e:
                logger.warning(f"Error getting article from Google Sheets: {e}")
        
        # Fall back to file storage
        return self.file_storage.get_article_by_pmid(pmid)
    
    def insert_article(self, article_data: Dict) -> bool:
        """Insert article into both Google Sheets and file storage"""
        success = True
        
        # Insert into Google Sheets if available
        if self.sheets_storage:
            try:
                sheets_success = self.sheets_storage.insert_article(article_data)
                if not sheets_success:
                    success = False
            except Exception as e:
                logger.warning(f"Error inserting into Google Sheets: {e}")
                success = False
        
        # Always insert into file storage as backup
        try:
            file_success = self.file_storage.insert_article(article_data)
            if not file_success:
                success = False
        except Exception as e:
            logger.error(f"Error inserting into file storage: {e}")
            success = False
        
        return success
    
    def get_paywalled_articles(self, threshold: int = 70) -> List[Dict]:
        """Get paywalled articles from both sources"""
        articles = []
        
        # Get from Google Sheets
        if self.sheets_storage:
            try:
                sheets_articles = self.sheets_storage.get_paywalled_articles(threshold)
                articles.extend(sheets_articles)
            except Exception as e:
                logger.warning(f"Error getting paywalled articles from Google Sheets: {e}")
        
        # Get from file storage
        try:
            file_articles = self.file_storage.get_paywalled_articles(threshold)
            # Merge, avoiding duplicates by PMID
            existing_pmids = {a.get('pmid') for a in articles}
            for article in file_articles:
                if article.get('pmid') not in existing_pmids:
                    articles.append(article)
        except Exception as e:
            logger.warning(f"Error getting paywalled articles from file storage: {e}")
        
        return articles
    
    def get_high_relevance_articles(self, threshold: int = 70) -> List[Dict]:
        """Get high relevance articles from both sources"""
        articles = []
        
        # Get from Google Sheets
        if self.sheets_storage:
            try:
                sheets_articles = self.sheets_storage.get_high_relevance_articles(threshold)
                articles.extend(sheets_articles)
            except Exception as e:
                logger.warning(f"Error getting high relevance articles from Google Sheets: {e}")
        
        # Get from file storage
        try:
            file_articles = self.file_storage.get_high_relevance_articles(threshold)
            # Merge, avoiding duplicates by PMID
            existing_pmids = {a.get('pmid') for a in articles}
            for article in file_articles:
                if article.get('pmid') not in existing_pmids:
                    articles.append(article)
        except Exception as e:
            logger.warning(f"Error getting high relevance articles from file storage: {e}")
        
        return articles


def get_storage_client():
    """
    Get storage client - Hybrid (Google Sheets + file storage) if available, otherwise file storage
    
    Returns:
        Storage client instance
    """
    # Check if Google Sheets credentials are available
    if (os.getenv('GOOGLE_SHEET_ID') and 
        os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL') and 
        os.getenv('GOOGLE_PRIVATE_KEY')):
        try:
            return HybridStorage()
        except Exception as e:
            logger.warning(f"Failed to initialize hybrid storage, falling back to file storage: {e}")
            from scripts.file_storage import FileStorage
            return FileStorage()
    else:
        # Fall back to file storage
        from scripts.file_storage import FileStorage
        return FileStorage()

