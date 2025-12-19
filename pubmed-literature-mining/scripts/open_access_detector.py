#!/usr/bin/env python3
"""
Open Access Detection and PDF Download
Checks multiple sources for open access status and downloads PDFs when available.
"""

import os
import logging
import requests
import time
from typing import Dict, Optional
from dotenv import load_dotenv
import pdfplumber
import PyPDF2
from io import BytesIO

load_dotenv()

logger = logging.getLogger(__name__)


class OpenAccessDetector:
    """Detects open access status and downloads PDFs"""
    
    UNPAYWALL_BASE = "https://api.unpaywall.org/v2"
    EUROPE_PMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    PMC_BASE = "https://www.ncbi.nlm.nih.gov/pmc"
    
    REQUEST_DELAY = 0.1  # Rate limiting
    
    def __init__(self):
        self.email = os.getenv('UNPAYWALL_EMAIL', 'parker@stroomai.com')
        self.pdf_dir = 'data/pdfs'
        os.makedirs(self.pdf_dir, exist_ok=True)
    
    def _make_request(self, url: str, params: Optional[Dict] = None, retry_count: int = 0) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        try:
            time.sleep(self.REQUEST_DELAY)
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if retry_count < 2:
                time.sleep(2 ** retry_count)
                return self._make_request(url, params, retry_count + 1)
            logger.warning(f"Request failed: {e}")
            return None
    
    def check_unpaywall(self, doi: str) -> Optional[Dict]:
        """Check Unpaywall API for open access status"""
        if not doi:
            return None
        
        url = f"{self.UNPAYWALL_BASE}/{doi}"
        params = {'email': self.email}
        
        response = self._make_request(url, params)
        if not response:
            return None
        
        try:
            data = response.json()
            is_oa = data.get('is_oa', False)
            pdf_url = None
            
            if is_oa:
                # Get best PDF URL
                oa_locations = data.get('oa_locations', [])
                for location in oa_locations:
                    if location.get('url_for_pdf'):
                        pdf_url = location['url_for_pdf']
                        break
                    elif location.get('url'):
                        pdf_url = location['url']
            
            return {
                'is_open_access': is_oa,
                'pdf_url': pdf_url,
                'source': 'unpaywall'
            }
        except (ValueError, KeyError) as e:
            logger.warning(f"Error parsing Unpaywall response: {e}")
            return None
    
    def check_pmc(self, pmid: str) -> Optional[Dict]:
        """Check PubMed Central for open access status"""
        if not pmid:
            return None
        
        # Check if PMCID exists (indicates PMC availability)
        url = f"{self.EUROPE_PMC_BASE}/search"
        params = {
            'query': f'EXT_ID:{pmid}',
            'format': 'json',
            'resultType': 'core'
        }
        
        response = self._make_request(url, params)
        if not response:
            return None
        
        try:
            data = response.json()
            results = data.get('resultList', {}).get('result', [])
            
            if results:
                result = results[0]
                pmcid = result.get('pmcid')
                if pmcid:
                    pdf_url = f"{self.PMC_BASE}/articles/{pmcid}/pdf"
                    return {
                        'is_open_access': True,
                        'pdf_url': pdf_url,
                        'source': 'pmc'
                    }
        except (ValueError, KeyError) as e:
            logger.warning(f"Error parsing PMC response: {e}")
        
        return None
    
    def check_europe_pmc(self, doi: str) -> Optional[Dict]:
        """Check Europe PMC for open access status"""
        if not doi:
            return None
        
        url = f"{self.EUROPE_PMC_BASE}/search"
        params = {
            'query': f'DOI:"{doi}"',
            'format': 'json',
            'resultType': 'core'
        }
        
        response = self._make_request(url, params)
        if not response:
            return None
        
        try:
            data = response.json()
            results = data.get('resultList', {}).get('result', [])
            
            if results:
                result = results[0]
                if result.get('isOpenAccess') == 'Y':
                    pdf_url = result.get('pdfUrl')
                    if pdf_url:
                        return {
                            'is_open_access': True,
                            'pdf_url': pdf_url,
                            'source': 'europe_pmc'
                        }
        except (ValueError, KeyError) as e:
            logger.warning(f"Error parsing Europe PMC response: {e}")
        
        return None
    
    def check_open_access(self, doi: str, pmid: Optional[str] = None) -> Dict:
        """
        Check multiple sources for open access status
        
        Args:
            doi: DOI string
            pmid: Optional PubMed ID for PMC check
            
        Returns:
            Dictionary with is_open_access, pdf_url, and source
        """
        # Try Unpaywall first (most reliable)
        result = self.check_unpaywall(doi)
        if result and result.get('is_open_access'):
            return result
        
        # Try PMC if we have PMID
        if pmid:
            result = self.check_pmc(pmid)
            if result and result.get('is_open_access'):
                return result
        
        # Try Europe PMC
        result = self.check_europe_pmc(doi)
        if result and result.get('is_open_access'):
            return result
        
        # Default: not open access
        return {
            'is_open_access': False,
            'pdf_url': None,
            'source': 'none'
        }
    
    def download_pdf(self, pdf_url: str, pmid: str) -> Optional[str]:
        """
        Download PDF and save to disk
        
        Args:
            pdf_url: URL to PDF
            pmid: PubMed ID for filename
            
        Returns:
            Path to saved PDF or None if failed
        """
        try:
            response = requests.get(pdf_url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Check if content is actually PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower():
                # Check first bytes
                content = response.content[:4]
                if content[:4] != b'%PDF':
                    logger.warning(f"URL {pdf_url} does not appear to be a PDF")
                    return None
            
            # Save PDF
            pdf_path = os.path.join(self.pdf_dir, f"{pmid}.pdf")
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded PDF for PMID {pmid}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            return None
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber failed for {pdf_path}, trying PyPDF2: {e}")
            try:
                # Fallback to PyPDF2
                with open(pdf_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e2:
                logger.error(f"Both PDF extraction methods failed for {pdf_path}: {e2}")
                return ""
        
        return text.strip()

