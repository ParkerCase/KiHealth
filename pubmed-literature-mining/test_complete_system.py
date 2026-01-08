#!/usr/bin/env python3
"""
Complete System Test
Tests all components of the literature quality system end-to-end
"""

import os
import sys
import json
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    
    try:
        from probast_assessment import PROBASTAssessment
        print("✓ PROBAST Assessment imported")
    except Exception as e:
        print(f"✗ PROBAST Assessment import failed: {e}")
        return False
    
    try:
        from literature_database import LiteratureDatabase
        print("✓ Literature Database imported")
    except Exception as e:
        print(f"✗ Literature Database import failed: {e}")
        return False
    
    try:
        from asreview_integration import ASReviewIntegration
        print("✓ ASReview Integration imported")
    except Exception as e:
        print(f"✗ ASReview Integration import failed: {e}")
        return False
    
    try:
        from literature_quality_workflow import LiteratureQualityWorkflow
        print("✓ Literature Quality Workflow imported")
    except Exception as e:
        print(f"✗ Literature Quality Workflow import failed: {e}")
        return False
    
    return True


def test_probast_assessment():
    """Test PROBAST assessment functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: PROBAST Assessment")
    print("=" * 60)
    
    from probast_assessment import PROBASTAssessment
    
    assessor = PROBASTAssessment()
    
    # Test article with good PROBAST characteristics
    good_article = {
        "title": "Predictors of Total Knee Replacement: A Prospective Cohort Study",
        "abstract": "We conducted a prospective cohort study of 500 patients with knee osteoarthritis. Baseline predictors including age, BMI, WOMAC scores, and KL grades were measured prospectively. Outcomes were total knee replacement (TKR) at 5 years, determined from registry data. Multivariable Cox regression was used with internal validation via bootstrap. EPV was 18.5.",
        "study_type": "Cohort Study"
    }
    
    assessment = assessor.assess_article(good_article)
    print(f"✓ Assessment completed: {assessment['overall_risk']} risk")
    print(f"  Domain 1: {assessment['domain_1_participants']}")
    print(f"  Domain 2: {assessment['domain_2_predictors']}")
    print(f"  Domain 3: {assessment['domain_3_outcome']}")
    print(f"  Domain 4: {assessment['domain_4_analysis']}")
    
    is_usable = assessor.is_usable_for_model(assessment)
    print(f"✓ Usable for model: {is_usable}")
    
    return is_usable  # Should be True for good article


def test_database():
    """Test database functionality"""
    print("\n" + "=" * 60)
    print("TEST 3: SQLite Database")
    print("=" * 60)
    
    from literature_database import LiteratureDatabase
    from probast_assessment import PROBASTAssessment
    
    test_db = "test_system.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    db = LiteratureDatabase(test_db)
    assessor = PROBASTAssessment()
    
    # Test article
    article = {
        "pmid": "99999999",
        "title": "Test Article for System Test",
        "abstract": "Prospective cohort study of knee osteoarthritis progression with 500 patients.",
        "journal": "Test Journal",
        "relevance_score": 85,
        "access_type": "open_access"
    }
    
    assessment = assessor.assess_article(article)
    db.add_article(article, assessment)
    print("✓ Article added to database")
    
    # Test retrieval
    usable = db.get_usable_articles()
    print(f"✓ Retrieved usable articles: {len(usable)}")
    
    # Test statistics
    stats = db.get_statistics()
    print(f"✓ Database statistics: {stats['total_articles']} articles")
    
    # Cleanup
    os.remove(test_db)
    print("✓ Database test complete")
    
    return True


def test_asreview_export():
    """Test ASReview export"""
    print("\n" + "=" * 60)
    print("TEST 4: ASReview Export")
    print("=" * 60)
    
    from asreview_integration import ASReviewIntegration
    
    asreview = ASReviewIntegration()
    
    test_articles = [
        {
            "pmid": "12345678",
            "title": "Test Article 1",
            "abstract": "Test abstract about knee osteoarthritis",
            "authors": "Smith J",
            "journal": "Test Journal",
            "doi": "10.1234/test",
            "publication_date": "2023-01-01"
        }
    ]
    
    export_path = "test_asreview_export.csv"
    success = asreview.export_for_asreview(test_articles, export_path)
    
    if success and os.path.exists(export_path):
        print("✓ ASReview export successful")
        print(f"  File: {export_path}")
        os.remove(export_path)
        return True
    else:
        print("✗ ASReview export failed")
        return False


def test_workflow_components():
    """Test workflow component initialization"""
    print("\n" + "=" * 60)
    print("TEST 5: Workflow Components")
    print("=" * 60)
    
    from literature_quality_workflow import LiteratureQualityWorkflow
    
    workflow = LiteratureQualityWorkflow()
    print("✓ Workflow initialized")
    print(f"  Max articles: {workflow.scraper.max_articles}")
    print(f"  ASReview available: {workflow.asreview.asreview_available}")
    
    # Test query building
    query = workflow._build_comprehensive_query()
    print(f"✓ Query built: {len(query)} characters")
    print(f"  Contains 'knee osteoarthritis': {'knee osteoarthritis' in query.lower()}")
    print(f"  Contains 'cohort': {'cohort' in query.lower()}")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("COMPLETE SYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    results['imports'] = test_imports()
    results['probast'] = test_probast_assessment()
    results['database'] = test_database()
    results['asreview'] = test_asreview_export()
    results['workflow'] = test_workflow_components()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - System is ready!")
    else:
        print("✗ SOME TESTS FAILED - Review errors above")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
