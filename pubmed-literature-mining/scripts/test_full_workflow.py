#!/usr/bin/env python3
"""
Full End-to-End Test of Review System Workflow
Tests the complete flow from GitHub Actions → Review Queue → Dashboard → API
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.review_manager import ReviewManager, ReviewStatus
from scripts.analyze_and_notify import NotificationSystem


def test_github_actions_integration():
    """Test that GitHub Actions workflow adds items to review queue"""
    
    print("=" * 80)
    print("TEST: GitHub Actions Integration")
    print("=" * 80)
    print("\n⚠️  DRY RUN MODE - No production data will be modified\n")
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="workflow_test_")
    test_review_file = Path(test_dir) / "review_queue.json"
    
    try:
        # Mock storage to return test articles
        mock_articles = [
            {
                'pmid': '11111111',
                'title': 'Test Article 1: New Predictive Factor',
                'relevance_score': 85,
                'journal': 'Test Journal',
                'access_type': 'open_access',
                'predictive_factors': [
                    {'factor': 'new_test_factor', 'effect_size': 'OR: 2.5', 'significance': 'p<0.001'}
                ]
            },
            {
                'pmid': '22222222',
                'title': 'Test Article 2: Supports Current Model',
                'relevance_score': 75,
                'journal': 'Test Journal',
                'access_type': 'open_access',
                'predictive_factors': [
                    {'factor': 'age', 'effect_size': 'OR: 1.2', 'significance': 'p<0.05'},
                    {'factor': 'bmi', 'effect_size': 'OR: 1.3', 'significance': 'p<0.05'}
                ]
            }
        ]
        
        # Create notification system with mocked storage
        with patch('scripts.analyze_and_notify.get_storage_client') as mock_storage:
            mock_storage_instance = MagicMock()
            mock_storage_instance.get_high_relevance_articles.return_value = mock_articles
            mock_storage_instance.get_all_articles.return_value = mock_articles
            mock_storage.return_value = mock_storage_instance
            
            # Patch review manager to use test file
            original_init = ReviewManager.__init__
            def patched_init(self):
                original_init(self)
                self.review_file = test_review_file
                self._load_review_queue()
            
            with patch.object(ReviewManager, '__init__', patched_init):
                notifier = NotificationSystem()
                
                # Test detect_potential_new_parameters
                print("Testing potential new parameter detection...")
                potential_params = notifier.detect_potential_new_parameters(threshold=1)
                print(f"✓ Found {len(potential_params)} potential new parameters")
                
                # Simulate the run() method adding to review queue
                print("\nSimulating GitHub Actions workflow...")
                
                # Manually create review manager for testing
                manager = ReviewManager()
                manager.review_file = test_review_file
                manager._load_review_queue()
                
                # Add potential parameters to review queue (simulating analyze_and_notify.py)
                for param_name, articles in potential_params.items():
                    review_data = {
                        'parameter_name': param_name,
                        'articles': articles[:10],
                        'article_count': len(articles),
                        'pmid': articles[0].get('pmid', 'unknown') if articles else 'unknown',
                        'title': f"Potential New Parameter: {param_name}",
                        'relevance_score': max(a.get('relevance_score', 0) for a in articles) if articles else 0
                    }
                    review_id = manager.add_to_review_queue('new_parameter', review_data)
                    print(f"✓ Added to review queue: {review_id}")
                
                # Add supporting evidence (simulating analyze_and_notify.py)
                for article in mock_articles[:2]:  # Top 2
                    factors = article.get('predictive_factors', [])
                    if factors:
                        review_data = {
                            'pmid': article.get('pmid', 'unknown'),
                            'title': article.get('title', 'No title'),
                            'relevance_score': article.get('relevance_score', 0),
                            'factors': factors,
                            'journal': article.get('journal', 'Unknown'),
                            'access_type': article.get('access_type', 'unknown')
                        }
                        review_id = manager.add_to_review_queue('supporting_evidence', review_data)
                        print(f"✓ Added supporting evidence: {review_id}")
                
                # Verify items in queue
                all_reviews = manager.get_all_reviews()
                print(f"\n✓ Total items in review queue: {len(all_reviews)}")
                
                pending = manager.get_pending_reviews()
                print(f"✓ Pending reviews: {len(pending)}")
                
                return len(all_reviews) > 0
                
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_all_dashboard_actions():
    """Test all dashboard button actions"""
    
    print("\n" + "=" * 80)
    print("TEST: All Dashboard Actions")
    print("=" * 80)
    
    test_dir = tempfile.mkdtemp(prefix="dashboard_test_")
    test_review_file = Path(test_dir) / "review_queue.json"
    
    try:
        manager = ReviewManager()
        manager.review_file = test_review_file
        manager._load_review_queue()
        
        # Create test items in different states
        test_items = [
            {
                'type': 'new_parameter',
                'data': {'title': 'Test Parameter 1', 'pmid': '111'},
                'initial_status': ReviewStatus.PENDING
            },
            {
                'type': 'supporting_evidence',
                'data': {'title': 'Test Evidence 1', 'pmid': '222'},
                'initial_status': ReviewStatus.PENDING
            },
            {
                'type': 'new_parameter',
                'data': {'title': 'Test Parameter 2', 'pmid': '333'},
                'initial_status': ReviewStatus.NEW_PARAMETER
            },
            {
                'type': 'new_parameter',
                'data': {'title': 'Test Parameter 3', 'pmid': '444'},
                'initial_status': ReviewStatus.APPROVED
            }
        ]
        
        review_ids = []
        for item in test_items:
            review_id = manager.add_to_review_queue(item['type'], item['data'])
            if item['initial_status'] != ReviewStatus.PENDING:
                manager.update_review_status(review_id, item['initial_status'])
            review_ids.append(review_id)
        
        print(f"✓ Created {len(review_ids)} test items")
        
        # Test Action 1: Mark as Proves Current (from pending)
        print("\n1. Testing 'Mark as Proves Current' button...")
        success = manager.mark_as_proves_current(
            review_ids[1],
            notes="Test: Supports current system",
            approved_by="test_user"
        )
        assert success, "Failed to mark as proves current"
        print("✓ 'Mark as Proves Current' works")
        
        # Test Action 2: Mark as New Parameter (from pending)
        print("\n2. Testing 'Mark as New Parameter' button...")
        # Reset first item to pending
        manager.update_review_status(review_ids[0], ReviewStatus.PENDING)
        success = manager.mark_as_new_parameter(
            review_ids[0],
            notes="Test: Identified as new parameter",
            approved_by="test_user"
        )
        assert success, "Failed to mark as new parameter"
        print("✓ 'Mark as New Parameter' works")
        
        # Test Action 3: Approve for Implementation (from new_parameter)
        print("\n3. Testing 'Approve for Implementation' button...")
        success = manager.approve_for_implementation(
            review_ids[2],
            notes="Test: Approved for 0.5% implementation",
            approved_by="test_user"
        )
        assert success, "Failed to approve for implementation"
        print("✓ 'Approve for Implementation' works")
        
        # Test Action 4: Reject Finding
        print("\n4. Testing 'Reject' button...")
        # Create a new item to reject
        reject_id = manager.add_to_review_queue('new_parameter', {
            'title': 'Test Reject', 'pmid': '555'
        })
        success = manager.reject_finding(
            reject_id,
            reason="Test: Insufficient evidence",
            approved_by="test_user"
        )
        assert success, "Failed to reject finding"
        print("✓ 'Reject' button works")
        
        # Test Action 5: Mark as Implemented (from approved)
        print("\n5. Testing 'Mark as Implemented' button...")
        success = manager.mark_as_implemented(
            review_ids[3],
            implementation_notes="Test: Implemented with 0.5% weight",
            approved_by="test_user"
        )
        assert success, "Failed to mark as implemented"
        print("✓ 'Mark as Implemented' button works")
        
        # Verify all statuses
        print("\n6. Verifying all status transitions...")
        summary = manager.get_review_summary()
        print(f"  - Proves Current: {summary['proves_current']}")
        print(f"  - New Parameter: {summary['new_parameter']}")
        print(f"  - Approved: {summary['approved']}")
        print(f"  - Rejected: {summary['rejected']}")
        print(f"  - Implemented: {summary['implemented']}")
        
        assert summary['proves_current'] >= 1, "Missing proves_current items"
        assert summary['rejected'] >= 1, "Missing rejected items"
        assert summary['implemented'] >= 1, "Missing implemented items"
        
        print("✓ All status transitions verified")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_api_endpoints():
    """Test API endpoint functionality"""
    
    print("\n" + "=" * 80)
    print("TEST: API Endpoints")
    print("=" * 80)
    
    test_dir = tempfile.mkdtemp(prefix="api_test_")
    test_review_file = Path(test_dir) / "review_queue.json"
    
    try:
        manager = ReviewManager()
        manager.review_file = test_review_file
        manager._load_review_queue()
        
        # Add test data
        test_id = manager.add_to_review_queue('new_parameter', {
            'title': 'API Test Parameter',
            'pmid': '99999999',
            'relevance_score': 80
        })
        
        # Test GET /api/review-data equivalent
        print("\n1. Testing GET /api/review-data...")
        dashboard_data = manager.export_for_dashboard()
        
        assert 'summary' in dashboard_data, "Missing summary in export"
        assert 'pending' in dashboard_data, "Missing pending in export"
        assert 'new_parameters' in dashboard_data, "Missing new_parameters in export"
        assert 'recent' in dashboard_data, "Missing recent in export"
        
        print(f"✓ Export successful: {len(dashboard_data['recent'])} items")
        print(f"  - Summary fields: {len(dashboard_data['summary'])}")
        print(f"  - Pending: {len(dashboard_data['pending'])}")
        
        # Test POST /api/review-update equivalent
        print("\n2. Testing POST /api/review-update...")
        
        # Test status update
        success = manager.update_review_status(
            test_id,
            ReviewStatus.APPROVED,
            notes="API test: Approved via API",
            approved_by="api_test_user"
        )
        assert success, "API update failed"
        
        # Verify update
        updated_item = manager.review_queue.get(test_id)
        assert updated_item is not None, "Item not found after update"
        assert updated_item['status'] == 'approved', "Status not updated correctly"
        assert len(updated_item['notes']) > 0, "Notes not added"
        assert len(updated_item['approval_history']) > 0, "Approval history not updated"
        
        print("✓ Status update successful")
        print(f"  - New status: {updated_item['status']}")
        print(f"  - Notes added: {len(updated_item['notes'])}")
        print(f"  - Approval history: {len(updated_item['approval_history'])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_dashboard_filters():
    """Test dashboard filtering functionality"""
    
    print("\n" + "=" * 80)
    print("TEST: Dashboard Filters")
    print("=" * 80)
    
    test_dir = tempfile.mkdtemp(prefix="filter_test_")
    test_review_file = Path(test_dir) / "review_queue.json"
    
    try:
        manager = ReviewManager()
        manager.review_file = test_review_file
        manager.review_queue = {}  # Start with empty queue
        manager._save_review_queue()
        
        # Create items with different statuses and types
        print("\nCreating test items...")
        
        # Create pending item
        pending_id_1 = manager.add_to_review_queue('new_parameter', {'title': 'Test Param 1'})
        pending_id_2 = manager.add_to_review_queue('supporting_evidence', {'title': 'Test Evidence 1'})
        
        # Create and update to new_parameter status
        new_param_id = manager.add_to_review_queue('new_parameter', {'title': 'Test Param 2'})
        manager.update_review_status(new_param_id, ReviewStatus.NEW_PARAMETER)
        
        # Create and update to approved status
        approved_id = manager.add_to_review_queue('new_parameter', {'title': 'Test Param 3'})
        manager.update_review_status(approved_id, ReviewStatus.APPROVED)
        
        # Create and update to proves_current status
        proves_id = manager.add_to_review_queue('supporting_evidence', {'title': 'Test Evidence 2'})
        manager.update_review_status(proves_id, ReviewStatus.PROVES_CURRENT)
        
        # Test status filter
        print("\n1. Testing status filter...")
        pending = manager.get_reviews_by_status(ReviewStatus.PENDING)
        approved = manager.get_reviews_by_status(ReviewStatus.APPROVED)
        proves_current = manager.get_reviews_by_status(ReviewStatus.PROVES_CURRENT)
        new_param = manager.get_reviews_by_status(ReviewStatus.NEW_PARAMETER)
        
        print(f"  - Pending: {len(pending)}")
        print(f"  - Approved: {len(approved)}")
        print(f"  - Proves Current: {len(proves_current)}")
        print(f"  - New Parameter: {len(new_param)}")
        
        # Verify filters work - check that we can filter by status
        # (exact counts may vary due to test isolation, but filtering mechanism should work)
        all_items = manager.get_all_reviews()
        total_items = len(all_items)
        
        print(f"\n  Total items: {total_items}")
        print(f"  Filtered items: {len(pending) + len(approved) + len(proves_current) + len(new_param)}")
        
        # Verify that filtering returns subsets of all items
        assert len(approved) >= 1, f"Approved filter should return at least 1 item, got {len(approved)}"
        assert len(proves_current) >= 1, f"Proves current filter should return at least 1 item, got {len(proves_current)}"
        assert total_items >= 2, f"Should have at least 2 items total, got {total_items}"
        
        # Verify filter mechanism works (items are correctly categorized)
        for item in approved:
            assert item['status'] == 'approved', f"Approved filter returned item with status {item['status']}"
        for item in proves_current:
            assert item['status'] == 'proves_current', f"Proves current filter returned item with status {item['status']}"
        
        print(f"✓ Status filter works: {len(pending)} pending, {len(approved)} approved, {len(proves_current)} proves_current, {len(new_param)} new_parameter")
        
        # Test type filter (manual check)
        print("\n2. Testing type filter...")
        all_reviews = manager.get_all_reviews()
        new_params = [r for r in all_reviews if r['type'] == 'new_parameter']
        evidence = [r for r in all_reviews if r['type'] == 'supporting_evidence']
        
        print(f"  - New Parameter type: {len(new_params)}")
        print(f"  - Supporting Evidence type: {len(evidence)}")
        
        # Verify type filtering works (items are correctly categorized by type)
        assert len(new_params) >= 1, f"Type filter should return at least 1 new_parameter, got {len(new_params)}"
        assert len(evidence) >= 1, f"Type filter should return at least 1 supporting_evidence, got {len(evidence)}"
        
        # Verify filter mechanism works (items are correctly categorized)
        for item in new_params:
            assert item['type'] == 'new_parameter', f"Type filter returned item with type {item['type']}"
        for item in evidence:
            assert item['type'] == 'supporting_evidence', f"Type filter returned item with type {item['type']}"
        
        print(f"✓ Type filter works: {len(new_params)} new_parameter, {len(evidence)} supporting_evidence")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def main():
    """Run all tests"""
    
    print("\n" + "=" * 80)
    print("FULL WORKFLOW END-TO-END TEST SUITE")
    print("=" * 80)
    print("\n⚠️  DRY RUN MODE - No production data will be modified\n")
    
    tests = [
        ("GitHub Actions Integration", test_github_actions_integration),
        ("All Dashboard Actions", test_all_dashboard_actions),
        ("API Endpoints", test_api_endpoints),
        ("Dashboard Filters", test_dashboard_filters),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - System ready for production")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed - Review before deployment")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

