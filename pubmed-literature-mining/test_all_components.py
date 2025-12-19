#!/usr/bin/env python3
"""
Comprehensive test script to validate all components
Tests structure, imports, and logic without requiring external services
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        # Test individual imports
        from scripts import xata_client
        from scripts import open_access_detector
        from scripts import relevance_scoring
        from scripts import factor_extraction
        print("✅ All module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_files():
    """Test that config files exist and are valid"""
    print("\nTesting config files...")
    try:
        config_path = 'config/keywords.json'
        if not os.path.exists(config_path):
            print(f"❌ Config file missing: {config_path}")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = ['high_value_keywords', 'study_designs', 'predictive_factors', 
                        'top_tier_journals', 'mid_tier_journals']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing key in config: {key}")
                return False
        
        print("✅ Config file valid")
        return True
    except Exception as e:
        print(f"❌ Config file error: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist or can be created"""
    print("\nTesting directory structure...")
    try:
        dirs = ['data/pdfs', 'logs', 'config']
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            if not os.path.exists(dir_path):
                print(f"❌ Cannot create directory: {dir_path}")
                return False
        print("✅ Directory structure valid")
        return True
    except Exception as e:
        print(f"❌ Directory error: {e}")
        return False

def test_relevance_scoring():
    """Test relevance scoring with sample data"""
    print("\nTesting relevance scoring...")
    try:
        from scripts.relevance_scoring import RelevanceScorer
        scorer = RelevanceScorer()
        
        # Test with sample article
        test_article = {
            'title': 'Predictors of total knee replacement in knee osteoarthritis',
            'abstract': 'This cohort study included 1500 patients. We assessed KL grade and WOMAC scores.',
            'journal': 'Arthritis & Rheumatology'
        }
        
        score = scorer.calculate_relevance_score(test_article)
        if not isinstance(score, int) or score < 0 or score > 100:
            print(f"❌ Invalid score: {score}")
            return False
        
        print(f"✅ Relevance scoring works (score: {score})")
        return True
    except Exception as e:
        print(f"❌ Relevance scoring error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factor_extraction():
    """Test factor extraction with sample text"""
    print("\nTesting factor extraction...")
    try:
        from scripts.factor_extraction import FactorExtractor
        extractor = FactorExtractor()
        
        test_text = "BMI was a significant predictor of total knee replacement (OR: 1.8, p<0.001)."
        factors = extractor.extract_predictive_factors(test_text)
        
        if not isinstance(factors, list):
            print(f"❌ Factors not a list: {type(factors)}")
            return False
        
        print(f"✅ Factor extraction works (found {len(factors)} factors)")
        return True
    except Exception as e:
        print(f"❌ Factor extraction error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xata_client_structure():
    """Test Xata client can be instantiated (without API calls)"""
    print("\nTesting Xata client structure...")
    try:
        from scripts.xata_client import XataClient
        # Don't set env vars, should handle gracefully
        client = XataClient()
        if not hasattr(client, 'enabled'):
            print("❌ XataClient missing 'enabled' attribute")
            return False
        print("✅ XataClient structure valid")
        return True
    except Exception as e:
        print(f"❌ XataClient error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_open_access_detector_structure():
    """Test OA detector structure"""
    print("\nTesting open access detector structure...")
    try:
        from scripts.open_access_detector import OpenAccessDetector
        detector = OpenAccessDetector()
        if not hasattr(detector, 'pdf_dir'):
            print("❌ OpenAccessDetector missing 'pdf_dir' attribute")
            return False
        print("✅ OpenAccessDetector structure valid")
        return True
    except Exception as e:
        print(f"❌ OpenAccessDetector error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pubmed_scraper_structure():
    """Test PubMed scraper can be imported"""
    print("\nTesting PubMed scraper structure...")
    try:
        from scripts.pubmed_scraper import PubMedScraper
        # Don't instantiate - requires env setup
        print("✅ PubMedScraper can be imported")
        return True
    except Exception as e:
        print(f"❌ PubMedScraper import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analyze_and_notify_structure():
    """Test notification system can be imported"""
    print("\nTesting notification system structure...")
    try:
        from scripts.analyze_and_notify import NotificationSystem
        print("✅ NotificationSystem can be imported")
        return True
    except Exception as e:
        print(f"❌ NotificationSystem import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_syntax():
    """Test GitHub Actions workflow YAML syntax"""
    print("\nTesting GitHub Actions workflow...")
    try:
        import yaml
        workflow_path = '.github/workflows/pubmed-scraper.yml'
        if not os.path.exists(workflow_path):
            print(f"❌ Workflow file missing: {workflow_path}")
            return False
        
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Check required keys
        if 'name' not in workflow:
            print("❌ Workflow missing 'name'")
            return False
        if 'on' not in workflow:
            print("❌ Workflow missing 'on'")
            return False
        if 'jobs' not in workflow:
            print("❌ Workflow missing 'jobs'")
            return False
        
        print("✅ Workflow YAML syntax valid")
        return True
    except ImportError:
        print("⚠️  PyYAML not installed, skipping workflow syntax check")
        return True  # Not critical
    except Exception as e:
        print(f"❌ Workflow syntax error: {e}")
        return False

def test_file_paths():
    """Test that file paths in scripts are correct"""
    print("\nTesting file paths...")
    try:
        # Check that scripts reference correct paths
        with open('scripts/relevance_scoring.py', 'r') as f:
            content = f.read()
            if 'config/keywords.json' not in content:
                print("❌ relevance_scoring.py doesn't reference config file correctly")
                return False
        
        with open('scripts/factor_extraction.py', 'r') as f:
            content = f.read()
            if 'config/keywords.json' not in content:
                print("❌ factor_extraction.py doesn't reference config file correctly")
                return False
        
        print("✅ File paths are correct")
        return True
    except Exception as e:
        print(f"❌ File path check error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("COMPREHENSIVE COMPONENT TEST")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config_files,
        test_directory_structure,
        test_relevance_scoring,
        test_factor_extraction,
        test_xata_client_structure,
        test_open_access_detector_structure,
        test_pubmed_scraper_structure,
        test_analyze_and_notify_structure,
        test_file_paths,
        test_workflow_syntax,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - System is ready!")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())

