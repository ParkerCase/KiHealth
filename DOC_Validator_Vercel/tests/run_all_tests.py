"""
Run all test suites
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    """Run all test suites"""
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE - SUCCESS PROBABILITY FEATURE")
    print("=" * 70)
    print()
    
    results = {}
    
    # Run unit tests
    print("\n" + "=" * 70)
    print("1. UNIT TESTS")
    print("=" * 70)
    try:
        from tests.test_success_calculation import run_all_tests as run_unit_tests
        results['unit'] = run_unit_tests()
    except Exception as e:
        print(f"Error running unit tests: {e}")
        results['unit'] = False
    
    # Run integration tests
    print("\n" + "=" * 70)
    print("2. INTEGRATION TESTS")
    print("=" * 70)
    try:
        from tests.test_api_integration import run_all_tests as run_integration_tests
        results['integration'] = run_integration_tests()
    except Exception as e:
        print(f"Error running integration tests: {e}")
        results['integration'] = False
    
    # Run UI/UX tests
    print("\n" + "=" * 70)
    print("3. UI/UX TESTS")
    print("=" * 70)
    try:
        from tests.test_ui_ux import run_all_tests as run_ui_tests
        results['ui'] = run_ui_tests()
    except Exception as e:
        print(f"Error running UI/UX tests: {e}")
        results['ui'] = False
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL TEST SUMMARY")
    print("=" * 70)
    print()
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    for suite, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {suite.upper()} tests")
    
    print()
    print(f"Overall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT!")
        return True
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed - REVIEW BEFORE DEPLOYMENT")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

