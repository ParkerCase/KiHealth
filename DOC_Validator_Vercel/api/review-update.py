"""
API endpoint for updating review status
Handles POST requests to update review item status
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
    from scripts.review_manager import ReviewManager, ReviewStatus
except ImportError:
    ReviewManager = None
    ReviewStatus = None


def handler(request):
    """Handle POST request to update review status"""
    try:
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        if ReviewManager is None:
            return {
                'statusCode': 503,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Review manager not available'})
            }
        
        body = json.loads(request.body) if hasattr(request, 'body') else {}
        review_id = body.get('id')
        status = body.get('status')
        notes = body.get('notes', '')
        approved_by = body.get('approved_by', 'dashboard_user')
        
        if not review_id or not status:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields: id, status'})
            }
        
        manager = ReviewManager()
        
        # Map status string to ReviewStatus enum
        status_map = {
            'proves_current': ReviewStatus.PROVES_CURRENT,
            'new_parameter': ReviewStatus.NEW_PARAMETER,
            'approved': ReviewStatus.APPROVED,
            'rejected': ReviewStatus.REJECTED,
            'implemented': ReviewStatus.IMPLEMENTED
        }
        
        if status not in status_map:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Invalid status: {status}'})
            }
        
        # Update status
        success = manager.update_review_status(
            review_id,
            status_map[status],
            notes=notes,
            approved_by=approved_by
        )
        
        if success:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': True, 'id': review_id, 'status': status})
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Review item not found'})
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

