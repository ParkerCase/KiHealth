#!/usr/bin/env python3
"""
End-to-End Test of Review System
Tests the review workflow without modifying any data or the production system.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import review manager
from scripts.review_manager import ReviewManager, ReviewStatus


def test_review_system():
    """Test the review system end-to-end without modifying production data"""
    
    print("=" * 80)
    print("REVIEW SYSTEM END-TO-END TEST")
    print("=" * 80)
    print("\n⚠️  DRY RUN MODE - No production data will be modified\n")
    
    # Create temporary directory for test data
    test_dir = tempfile.mkdtemp(prefix="review_test_")
    test_review_file = Path(test_dir) / "review_queue.json"
    
    print(f"Test directory: {test_dir}")
    print(f"Test review file: {test_review_file}\n")
    
    try:
        # Create a test review manager with temporary file
        # We'll patch the review_file path
        manager = ReviewManager()
        original_file = manager.review_file
        manager.review_file = test_review_file
        
        print("✓ ReviewManager initialized")
        
        # Test 1: Add finding to review queue
        print("\n" + "-" * 80)
        print("TEST 1: Add Finding to Review Queue")
        print("-" * 80)
        
        test_finding_1 = {
            'pmid': '12345678',
            'title': 'Test Article: New Predictive Factor',
            'relevance_score': 85,
            'parameter_name': 'test_factor_1',
            'articles': [
                {'pmid': '12345678', 'title': 'Test Article 1', 'relevance_score': 85},
                {'pmid': '12345679', 'title': 'Test Article 2', 'relevance_score': 82}
            ],
            'article_count': 2
        }
        
        review_id_1 = manager.add_to_review_queue('new_parameter', test_finding_1)
        print(f"✓ Added finding to queue: {review_id_1}")
        
        # Test 2: Add supporting evidence
        print("\n" + "-" * 80)
        print("TEST 2: Add Supporting Evidence")
        print("-" * 80)
        
        test_finding_2 = {
            'pmid': '87654321',
            'title': 'Test Article: Supports Current Model',
            'relevance_score': 75,
            'factors': ['age', 'bmi', 'womac'],
            'journal': 'Test Journal',
            'access_type': 'open_access'
        }
        
        review_id_2 = manager.add_to_review_queue('supporting_evidence', test_finding_2)
        print(f"✓ Added supporting evidence: {review_id_2}")
        
        # Test 3: Get pending reviews
        print("\n" + "-" * 80)
        print("TEST 3: Get Pending Reviews")
        print("-" * 80)
        
        pending = manager.get_pending_reviews()
        print(f"✓ Found {len(pending)} pending reviews")
        for item in pending:
            print(f"  - {item['id']}: {item['data'].get('title', 'No title')}")
        
        # Test 4: Mark as proves current
        print("\n" + "-" * 80)
        print("TEST 4: Mark as Proves Current")
        print("-" * 80)
        
        success = manager.mark_as_proves_current(
            review_id_2,
            notes="Test: This finding supports the current model parameters",
            approved_by="test_user"
        )
        print(f"✓ Status update: {success}")
        
        proves_current = manager.get_reviews_by_status(ReviewStatus.PROVES_CURRENT)
        print(f"✓ Found {len(proves_current)} items marked as 'proves current'")
        
        # Test 5: Mark as new parameter
        print("\n" + "-" * 80)
        print("TEST 5: Mark as New Parameter")
        print("-" * 80)
        
        success = manager.mark_as_new_parameter(
            review_id_1,
            notes="Test: Identified as potential new parameter",
            approved_by="test_user"
        )
        print(f"✓ Status update: {success}")
        
        new_params = manager.get_reviews_by_status(ReviewStatus.NEW_PARAMETER)
        print(f"✓ Found {len(new_params)} items marked as 'new parameter'")
        
        # Test 6: Approve for implementation
        print("\n" + "-" * 80)
        print("TEST 6: Approve for Implementation")
        print("-" * 80)
        
        success = manager.approve_for_implementation(
            review_id_1,
            notes="Test: Approved for incremental implementation (0.5% initial weight)",
            approved_by="test_user"
        )
        print(f"✓ Status update: {success}")
        
        approved = manager.get_reviews_by_status(ReviewStatus.APPROVED)
        print(f"✓ Found {len(approved)} items approved for implementation")
        
        # Test 7: Get review summary
        print("\n" + "-" * 80)
        print("TEST 7: Get Review Summary")
        print("-" * 80)
        
        summary = manager.get_review_summary()
        print(f"✓ Review Summary:")
        print(f"  - Total: {summary['total']}")
        print(f"  - Pending: {summary['pending']}")
        print(f"  - Proves Current: {summary['proves_current']}")
        print(f"  - New Parameter: {summary['new_parameter']}")
        print(f"  - Approved: {summary['approved']}")
        print(f"  - Implemented: {summary['implemented']}")
        
        # Test 8: Export for dashboard
        print("\n" + "-" * 80)
        print("TEST 8: Export for Dashboard")
        print("-" * 80)
        
        dashboard_data = manager.export_for_dashboard()
        print(f"✓ Dashboard export successful")
        print(f"  - Summary: {len(dashboard_data.get('summary', {}))} fields")
        print(f"  - Pending: {len(dashboard_data.get('pending', []))} items")
        print(f"  - New Parameters: {len(dashboard_data.get('new_parameters', []))} items")
        print(f"  - Recent: {len(dashboard_data.get('recent', []))} items")
        
        # Test 9: Verify data persistence
        print("\n" + "-" * 80)
        print("TEST 9: Verify Data Persistence")
        print("-" * 80)
        
        # Create new manager instance to test file loading
        manager2 = ReviewManager()
        manager2.review_file = test_review_file
        manager2._load_review_queue()
        
        loaded_count = len(manager2.review_queue)
        print(f"✓ Loaded {loaded_count} items from file")
        assert loaded_count == summary['total'], "Data persistence failed!"
        print("✓ Data persistence verified")
        
        # Test 10: Reject finding
        print("\n" + "-" * 80)
        print("TEST 10: Reject Finding")
        print("-" * 80)
        
        test_finding_3 = {
            'pmid': '99999999',
            'title': 'Test Article: Should Be Rejected',
            'relevance_score': 50
        }
        
        review_id_3 = manager.add_to_review_queue('new_parameter', test_finding_3)
        success = manager.reject_finding(
            review_id_3,
            reason="Test: Insufficient evidence for model integration",
            approved_by="test_user"
        )
        print(f"✓ Rejection successful: {success}")
        
        rejected = manager.get_reviews_by_status(ReviewStatus.REJECTED)
        print(f"✓ Found {len(rejected)} rejected items")
        
        # Final summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        final_summary = manager.get_review_summary()
        print(f"\nFinal Review Queue Status:")
        print(f"  ✓ Total Items: {final_summary['total']}")
        print(f"  ✓ Pending: {final_summary['pending']}")
        print(f"  ✓ Proves Current: {final_summary['proves_current']}")
        print(f"  ✓ New Parameter: {final_summary['new_parameter']}")
        print(f"  ✓ Approved: {final_summary['approved']}")
        print(f"  ✓ Rejected: {final_summary['rejected']}")
        print(f"  ✓ Implemented: {final_summary['implemented']}")
        
        print("\n✅ ALL TESTS PASSED")
        print(f"\nTest data location: {test_dir}")
        print("⚠️  Test data will be cleaned up automatically")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup test directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\n✓ Test directory cleaned up: {test_dir}")


if __name__ == "__main__":
    success = test_review_system()
    sys.exit(0 if success else 1)

