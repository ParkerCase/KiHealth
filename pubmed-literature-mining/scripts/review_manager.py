#!/usr/bin/env python3
"""
Review Manager for Literature Findings
Manages the review and approval workflow for new findings from PubMed.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.google_sheets_storage import get_storage_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Status of a review item"""
    PENDING = "pending"
    PROVES_CURRENT = "proves_current"
    NEW_PARAMETER = "new_parameter"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class ReviewManager:
    """Manages review and approval workflow for literature findings"""
    
    def __init__(self):
        self.storage = get_storage_client()
        self.review_file = Path(__file__).parent.parent / "data" / "review_queue.json"
        self.review_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_review_queue()
    
    def _load_review_queue(self):
        """Load review queue from file"""
        if self.review_file.exists():
            try:
                with open(self.review_file, 'r') as f:
                    self.review_queue = json.load(f)
            except Exception as e:
                logger.error(f"Error loading review queue: {e}")
                self.review_queue = {}
        else:
            self.review_queue = {}
    
    def _save_review_queue(self):
        """Save review queue to file"""
        try:
            with open(self.review_file, 'w') as f:
                json.dump(self.review_queue, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving review queue: {e}")
    
    def add_to_review_queue(self, finding_type: str, data: Dict, source: str = "pubmed") -> str:
        """
        Add a finding to the review queue
        
        Args:
            finding_type: Type of finding ('new_parameter', 'factor_pattern', 'supporting_evidence')
            data: Finding data (article info, factors, etc.)
            source: Source of the finding
            
        Returns:
            Review ID
        """
        review_id = f"{finding_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{data.get('pmid', 'unknown')}"
        
        review_item = {
            'id': review_id,
            'type': finding_type,
            'status': ReviewStatus.PENDING.value,
            'data': data,
            'source': source,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'notes': [],
            'approval_history': []
        }
        
        self.review_queue[review_id] = review_item
        self._save_review_queue()
        logger.info(f"Added {finding_type} to review queue: {review_id}")
        
        return review_id
    
    def update_review_status(self, review_id: str, status: ReviewStatus, notes: str = None, approved_by: str = None):
        """Update the status of a review item"""
        if review_id not in self.review_queue:
            logger.error(f"Review ID not found: {review_id}")
            return False
        
        review_item = self.review_queue[review_id]
        old_status = review_item['status']
        review_item['status'] = status.value
        review_item['updated_at'] = datetime.now().isoformat()
        
        if notes:
            review_item['notes'].append({
                'timestamp': datetime.now().isoformat(),
                'note': notes,
                'status_change': f"{old_status} -> {status.value}"
            })
        
        if approved_by:
            review_item['approval_history'].append({
                'timestamp': datetime.now().isoformat(),
                'action': status.value,
                'approved_by': approved_by
            })
        
        self._save_review_queue()
        logger.info(f"Updated review {review_id}: {old_status} -> {status.value}")
        
        return True
    
    def mark_as_proves_current(self, review_id: str, notes: str = None, approved_by: str = None):
        """Mark a finding as supporting the current system"""
        return self.update_review_status(
            review_id, 
            ReviewStatus.PROVES_CURRENT, 
            notes=notes or "Finding supports current model parameters",
            approved_by=approved_by
        )
    
    def mark_as_new_parameter(self, review_id: str, notes: str = None, approved_by: str = None):
        """Mark a finding as a potential new parameter"""
        return self.update_review_status(
            review_id,
            ReviewStatus.NEW_PARAMETER,
            notes=notes or "Identified as potential new model parameter",
            approved_by=approved_by
        )
    
    def approve_for_implementation(self, review_id: str, notes: str = None, approved_by: str = None):
        """Approve a finding for implementation"""
        return self.update_review_status(
            review_id,
            ReviewStatus.APPROVED,
            notes=notes or "Approved for incremental implementation",
            approved_by=approved_by
        )
    
    def reject_finding(self, review_id: str, reason: str, approved_by: str = None):
        """Reject a finding"""
        return self.update_review_status(
            review_id,
            ReviewStatus.REJECTED,
            notes=f"Rejected: {reason}",
            approved_by=approved_by
        )
    
    def mark_as_implemented(self, review_id: str, implementation_notes: str = None, approved_by: str = None):
        """Mark a finding as implemented"""
        return self.update_review_status(
            review_id,
            ReviewStatus.IMPLEMENTED,
            notes=implementation_notes or "Successfully implemented in model",
            approved_by=approved_by
        )
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get all pending review items"""
        return [
            item for item in self.review_queue.values()
            if item['status'] == ReviewStatus.PENDING.value
        ]
    
    def get_reviews_by_status(self, status: ReviewStatus) -> List[Dict]:
        """Get all reviews with a specific status"""
        return [
            item for item in self.review_queue.values()
            if item['status'] == status.value
        ]
    
    def get_all_reviews(self, limit: int = None) -> List[Dict]:
        """Get all review items, optionally limited"""
        items = list(self.review_queue.values())
        items.sort(key=lambda x: x['created_at'], reverse=True)
        return items[:limit] if limit else items
    
    def get_review_summary(self) -> Dict:
        """Get summary statistics of review queue"""
        total = len(self.review_queue)
        by_status = {}
        for status in ReviewStatus:
            by_status[status.value] = len(self.get_reviews_by_status(status))
        
        return {
            'total': total,
            'by_status': by_status,
            'pending': by_status.get('pending', 0),
            'proves_current': by_status.get('proves_current', 0),
            'new_parameter': by_status.get('new_parameter', 0),
            'approved': by_status.get('approved', 0),
            'rejected': by_status.get('rejected', 0),
            'implemented': by_status.get('implemented', 0)
        }
    
    def export_for_dashboard(self) -> Dict:
        """Export review data for dashboard display"""
        return {
            'summary': self.get_review_summary(),
            'pending': self.get_pending_reviews(),
            'new_parameters': self.get_reviews_by_status(ReviewStatus.NEW_PARAMETER),
            'approved': self.get_reviews_by_status(ReviewStatus.APPROVED),
            'proves_current': self.get_reviews_by_status(ReviewStatus.PROVES_CURRENT),
            'recent': self.get_all_reviews(limit=20)
        }


if __name__ == "__main__":
    # Example usage
    manager = ReviewManager()
    
    # Example: Add a finding to review queue
    example_finding = {
        'pmid': '12345678',
        'title': 'Example Article',
        'relevance_score': 85,
        'factors': ['new_factor_1', 'new_factor_2']
    }
    
    review_id = manager.add_to_review_queue('new_parameter', example_finding)
    print(f"Added to review queue: {review_id}")
    
    # Get summary
    summary = manager.get_review_summary()
    print(f"Review Summary: {summary}")

