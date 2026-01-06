"""
API endpoint for review dashboard data
Returns review queue data for the literature review dashboard
"""

import json
import sys
import os
from pathlib import Path

# Add pubmed-literature-mining to path
project_root = Path(__file__).parent.parent.parent
pubmed_path = project_root / "pubmed-literature-mining"
sys.path.insert(0, str(pubmed_path))

try:
    from scripts.review_manager import ReviewManager
except ImportError:
    # Fallback if review manager not available
    ReviewManager = None


def handler(request):
    """Handle GET request for review data"""
    try:
        if ReviewManager is None:
            return {
                'statusCode': 503,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Review manager not available',
                    'summary': {
                        'total': 0,
                        'pending': 0,
                        'new_parameter': 0,
                        'proves_current': 0,
                        'approved': 0,
                        'implemented': 0
                    },
                    'recent': []
                })
            }
        
        manager = ReviewManager()
        data = manager.export_for_dashboard()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(data, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

