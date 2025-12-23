"""
Unit tests for success probability calculation
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.success_calculation import (
    calculate_success_category,
    get_success_probability,
    get_category_color,
    get_category_description,
    SUCCESS_THRESHOLDS
)


def test_success_category_calculation():
    """Test success category calculation based on improvement points"""
    print("Testing success category calculation...")
    
    # Test cases: (improvement, expected_category)
    test_cases = [
        (45, "Excellent Outcome"),  # >40
        (35, "Successful Outcome"),  # 30-40
        (30, "Successful Outcome"),  # Exactly 30 (threshold)
        (25, "Moderate Improvement"),  # 20-30
        (20, "Moderate Improvement"),  # Exactly 20
        (15, "Limited Improvement"),  # 10-20
        (10, "Limited Improvement"),  # Exactly 10
        (5, "Minimal Improvement"),  # 0-10
        (0, "Minimal Improvement"),  # Exactly 0
        (-5, "Minimal Improvement"),  # Negative (edge case)
        (100, "Excellent Outcome"),  # Very high (edge case)
    ]
    
    passed = 0
    failed = 0
    
    for improvement, expected in test_cases:
        result = calculate_success_category(improvement)
        if result == expected:
            print(f"  ✓ {improvement} points → {result}")
            passed += 1
        else:
            print(f"  ✗ {improvement} points → Expected {expected}, got {result}")
            failed += 1
    
    print(f"\nCategory calculation: {passed} passed, {failed} failed\n")
    return failed == 0


def test_success_probability_calculation():
    """Test success probability calculation (0-100%)"""
    print("Testing success probability calculation...")
    
    # Test cases: (improvement, expected_range)
    test_cases = [
        (45, (85, 100)),  # Excellent
        (35, (70, 85)),  # Successful
        (30, (70, 85)),  # Threshold
        (25, (40, 70)),  # Moderate
        (15, (20, 40)),  # Limited
        (5, (0, 20)),  # Minimal
        (0, (0, 20)),  # Zero
        (-5, (0, 20)),  # Negative
        (100, (85, 100)),  # Very high
    ]
    
    passed = 0
    failed = 0
    
    for improvement, (min_prob, max_prob) in test_cases:
        result = get_success_probability(improvement)
        if min_prob <= result <= max_prob:
            print(f"  ✓ {improvement} points → {result}% (expected {min_prob}-{max_prob}%)")
            passed += 1
        else:
            print(f"  ✗ {improvement} points → {result}% (expected {min_prob}-{max_prob}%)")
            failed += 1
    
    print(f"\nProbability calculation: {passed} passed, {failed} failed\n")
    return failed == 0


def test_category_color_mapping():
    """Test category color mapping"""
    print("Testing category color mapping...")
    
    categories = [
        "Excellent Outcome",
        "Successful Outcome",
        "Moderate Improvement",
        "Limited Improvement",
        "Minimal Improvement",
    ]
    
    passed = 0
    failed = 0
    
    for category in categories:
        color = get_category_color(category)
        # Function returns a dict with text/bg classes, which is correct
        if color and isinstance(color, dict) and "text" in color and "bg" in color:
            print(f"  ✓ {category} → {color.get('text', 'N/A')}")
            passed += 1
        else:
            print(f"  ✗ {category} → Invalid color format: {color}")
            failed += 1
    
    print(f"\nColor mapping: {passed} passed, {failed} failed\n")
    return failed == 0


def test_category_descriptions():
    """Test category descriptions"""
    print("Testing category descriptions...")
    
    categories = [
        "Excellent Outcome",
        "Successful Outcome",
        "Moderate Improvement",
        "Limited Improvement",
        "Minimal Improvement",
    ]
    
    passed = 0
    failed = 0
    
    for category in categories:
        desc = get_category_description(category)
        if desc and len(desc) > 10:  # Should have meaningful description
            print(f"  ✓ {category} → {desc[:50]}...")
            passed += 1
        else:
            print(f"  ✗ {category} → Missing or too short description")
            failed += 1
    
    print(f"\nDescription mapping: {passed} passed, {failed} failed\n")
    return failed == 0


def test_threshold_agreement():
    """Test that 30-point threshold aligns with successful outcome"""
    print("Testing 30-point threshold agreement...")
    
    # 30 points should be "Successful Outcome"
    category_30 = calculate_success_category(30)
    prob_30 = get_success_probability(30)
    
    # 29 points should be "Moderate Improvement"
    category_29 = calculate_success_category(29)
    
    passed = 0
    failed = 0
    
    if category_30 == "Successful Outcome":
        print(f"  ✓ 30 points correctly categorized as 'Successful Outcome'")
        passed += 1
    else:
        print(f"  ✗ 30 points incorrectly categorized as '{category_30}'")
        failed += 1
    
    if 70 <= prob_30 <= 85:
        print(f"  ✓ 30 points has success probability {prob_30}% (expected 70-85%)")
        passed += 1
    else:
        print(f"  ✗ 30 points has success probability {prob_30}% (expected 70-85%)")
        failed += 1
    
    if category_29 == "Moderate Improvement":
        print(f"  ✓ 29 points correctly categorized as 'Moderate Improvement'")
        passed += 1
    else:
        print(f"  ✗ 29 points incorrectly categorized as '{category_29}'")
        failed += 1
    
    print(f"\nThreshold agreement: {passed} passed, {failed} failed\n")
    return failed == 0


def run_all_tests():
    """Run all unit tests"""
    print("=" * 60)
    print("SUCCESS CALCULATION UNIT TESTS")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Category Calculation", test_success_category_calculation()))
    results.append(("Probability Calculation", test_success_probability_calculation()))
    results.append(("Color Mapping", test_category_color_mapping()))
    results.append(("Description Mapping", test_category_descriptions()))
    results.append(("Threshold Agreement", test_threshold_agreement()))
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All unit tests passed!")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

