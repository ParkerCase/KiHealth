#!/usr/bin/env python3
"""
Test Persistence Flow: GitHub Actions → Review Queue → Dashboard
Verifies that items added by GitHub Actions will persist and show up in dashboard
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

from scripts.review_manager import ReviewManager, ReviewStatus


def test_persistence_flow():
    """Test complete persistence flow"""
    
    print("=" * 80)
    print("PERSISTENCE FLOW TEST")
    print("=" * 80)
    print("\nTesting: GitHub Actions → Review Queue File → Dashboard API\n")
    
    # Create temporary directory to simulate repo structure
    test_dir = tempfile.mkdtemp(prefix="persistence_test_")
    test_data_dir = Path(test_dir) / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    test_review_file = test_data_dir / "review_queue.json"
    
    try:
        # STEP 1: Simulate GitHub Actions adding items
        print("STEP 1: Simulating GitHub Actions workflow...")
        
        # Create ReviewManager with test file path
        manager1 = ReviewManager()
        manager1.review_file = test_review_file
        manager1.review_queue = {}
        manager1._save_review_queue()
        
        # Simulate analyze_and_notify.py adding items
        test_items = [
            {
                'type': 'new_parameter',
                'data': {
                    'parameter_name': 'test_factor_1',
                    'articles': [{'pmid': '111', 'title': 'Test Article 1'}],
                    'article_count': 1,
                    'pmid': '111',
                    'title': 'Potential New Parameter: test_factor_1',
                    'relevance_score': 85
                }
            },
            {
                'type': 'supporting_evidence',
                'data': {
                    'pmid': '222',
                    'title': 'Test Article 2',
                    'relevance_score': 80,
                    'factors': [{'factor': 'age', 'effect_size': 'OR: 1.2'}],
                    'journal': 'Test Journal',
                    'access_type': 'open_access'
                }
            }
        ]
        
        review_ids = []
        for item in test_items:
            review_id = manager1.add_to_review_queue(item['type'], item['data'])
            review_ids.append(review_id)
            print(f"  ✓ Added: {review_id}")
        
        # Verify file exists and has content
        assert test_review_file.exists(), "Review queue file was not created!"
        print(f"  ✓ File created: {test_review_file}")
        
        # Verify file has content
        with open(test_review_file, 'r') as f:
            file_content = json.load(f)
        assert len(file_content) == 2, f"Expected 2 items, got {len(file_content)}"
        print(f"  ✓ File contains {len(file_content)} items")
        
        # STEP 2: Simulate file being committed to git (just verify it exists)
        print("\nSTEP 2: Verifying file is ready for commit...")
        print(f"  ✓ File path: {test_review_file}")
        print(f"  ✓ File size: {test_review_file.stat().st_size} bytes")
        print(f"  ✓ File is readable and valid JSON")
        
        # STEP 3: Simulate Dashboard API loading the file
        print("\nSTEP 3: Simulating Dashboard API loading...")
        
        # Create NEW ReviewManager instance (simulating API request)
        manager2 = ReviewManager()
        manager2.review_file = test_review_file
        manager2._load_review_queue()
        
        # Verify items are loaded
        all_reviews = manager2.get_all_reviews()
        assert len(all_reviews) == 2, f"Expected 2 items loaded, got {len(all_reviews)}"
        print(f"  ✓ Loaded {len(all_reviews)} items from file")
        
        # Verify specific items
        for review_id in review_ids:
            item = manager2.review_queue.get(review_id)
            assert item is not None, f"Item {review_id} not found in loaded queue!"
            print(f"  ✓ Item {review_id} loaded correctly")
        
        # STEP 4: Test dashboard export
        print("\nSTEP 4: Testing dashboard export...")
        dashboard_data = manager2.export_for_dashboard()
        
        assert 'summary' in dashboard_data, "Missing summary in export"
        assert 'pending' in dashboard_data, "Missing pending in export"
        assert 'recent' in dashboard_data, "Missing recent in export"
        
        print(f"  ✓ Dashboard export successful")
        print(f"    - Total items: {dashboard_data['summary']['total']}")
        print(f"    - Pending: {dashboard_data['summary']['pending']}")
        print(f"    - Recent items: {len(dashboard_data['recent'])}")
        
        # STEP 5: Verify persistence after updates
        print("\nSTEP 5: Testing persistence after status updates...")
        
        # Update status of first item
        manager2.update_review_status(
            review_ids[0],
            ReviewStatus.APPROVED,
            notes="Test approval",
            approved_by="test_user"
        )
        
        # Reload and verify update persisted
        manager3 = ReviewManager()
        manager3.review_file = test_review_file
        manager3._load_review_queue()
        
        updated_item = manager3.review_queue.get(review_ids[0])
        assert updated_item['status'] == 'approved', "Status update did not persist!"
        assert len(updated_item['notes']) > 0, "Notes did not persist!"
        print(f"  ✓ Status updates persist correctly")
        
        print("\n" + "=" * 80)
        print("✅ ALL PERSISTENCE TESTS PASSED")
        print("=" * 80)
        print("\nFlow verified:")
        print("  1. GitHub Actions adds items → File created ✓")
        print("  2. File is ready for commit ✓")
        print("  3. Dashboard API loads items from file ✓")
        print("  4. Dashboard export works ✓")
        print("  5. Status updates persist ✓")
        print("\n⚠️  IMPORTANT: Ensure review_queue.json is committed to git!")
        print("   The GitHub Actions workflow should commit this file.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    success = test_persistence_flow()
    sys.exit(0 if success else 1)

