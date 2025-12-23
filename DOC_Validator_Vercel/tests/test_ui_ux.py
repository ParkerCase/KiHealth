"""
UI/UX validation tests
"""
import sys
import os
import re

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_no_womac_in_ui():
    """Test that WOMAC is not visible in primary UI"""
    print("Testing for WOMAC terminology in UI...")
    
    html_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'index.html')
    js_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'static', 'js', 'main.js')
    
    issues = []
    
    # Check HTML file
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Find WOMAC mentions (excluding internal IDs and comments)
        womac_pattern = r'\bWOMAC\b'
        matches = re.finditer(womac_pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            # Get context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(html_content), match.end() + 50)
            context = html_content[start:end]
            
            # Skip if it's in a comment, ID attribute, variable name, or value attribute
            skip_patterns = ['<!--', 'womac_r', 'womac_l', 'vasToWomac', '_womac', 'value="womac"', 'name="womac']
            if not any(skip in context.lower() for skip in skip_patterns):
                # Only flag if it appears to be user-facing text
                if 'label' in context.lower() or 'text' in context.lower() or 'title' in context.lower():
                    issues.append(f"HTML: Found 'WOMAC' at position {match.start()}: ...{context}...")
    
    # Check JS file for user-facing text
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Look for WOMAC in string literals (user-facing text)
        # This is a simple check - in production, use AST parsing
        string_pattern = r'["\']([^"\']*WOMAC[^"\']*)["\']'
        matches = re.finditer(string_pattern, js_content, re.IGNORECASE)
        
        for match in matches:
            text = match.group(1)
            # Skip if it's a variable name, internal reference, or comment
            skip_patterns = ['womac_r', 'womac_l', 'vasToWomac', '_womac', '//', '/*', 'womacrfield', 'womaclfield', 'getelementbyid']
            if not any(skip in text.lower() for skip in skip_patterns):
                # Also check if it's in a user-facing context (not just variable names)
                if len(text.strip()) > 3:  # Only flag if it's a meaningful string
                    issues.append(f"JS: Found 'WOMAC' in string: {text[:50]}")
    
    if issues:
        print(f"  ✗ Found {len(issues)} potential WOMAC mentions in UI:")
        for issue in issues[:5]:  # Show first 5
            print(f"    - {issue}")
        if len(issues) > 5:
            print(f"    ... and {len(issues) - 5} more")
        return False
    else:
        print("  ✓ No WOMAC terminology found in primary UI")
        return True


def test_success_categories_in_ui():
    """Test that success categories are displayed in UI"""
    print("\nTesting success category display in UI...")
    
    js_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'static', 'js', 'main.js')
    
    if not os.path.exists(js_file):
        print("  ✗ JavaScript file not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    required_categories = [
        "Excellent Outcome",
        "Successful Outcome",
        "Moderate Improvement",
        "Limited Improvement",
        "Minimal Improvement",
    ]
    
    found_categories = []
    for category in required_categories:
        if category in js_content:
            found_categories.append(category)
    
    if len(found_categories) == len(required_categories):
        print(f"  ✓ All {len(required_categories)} success categories found in UI")
        return True
    else:
        missing = set(required_categories) - set(found_categories)
        print(f"  ✗ Missing categories: {missing}")
        return False


def test_color_coding():
    """Test that color coding is implemented"""
    print("\nTesting color coding implementation...")
    
    js_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'static', 'js', 'main.js')
    
    if not os.path.exists(js_file):
        print("  ✗ JavaScript file not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Check for color definitions
    color_indicators = [
        "categoryColors",
        "#10b981",  # green
        "#3b82f6",  # blue
        "#eab308",  # yellow
        "#f97316",  # orange
        "#ef4444",  # red
    ]
    
    found_colors = sum(1 for indicator in color_indicators if indicator in js_content)
    
    if found_colors >= 4:  # At least categoryColors and some colors
        print(f"  ✓ Color coding implemented ({found_colors} indicators found)")
        return True
    else:
        print(f"  ✗ Color coding may be incomplete ({found_colors} indicators found)")
        return False


def test_success_probability_display():
    """Test that success probability is displayed as percentage"""
    print("\nTesting success probability display...")
    
    js_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'static', 'js', 'main.js')
    
    if not os.path.exists(js_file):
        print("  ✗ JavaScript file not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Check for success probability references
    indicators = [
        "success_probability",
        "Success Probability",
        "%",
    ]
    
    found = sum(1 for indicator in indicators if indicator in js_content)
    
    if found >= 2:
        print("  ✓ Success probability display implemented")
        return True
    else:
        print("  ✗ Success probability display may be incomplete")
        return False


def test_legend_presence():
    """Test that legend is present"""
    print("\nTesting legend presence...")
    
    js_file = os.path.join(os.path.dirname(__file__), '..', 'public', 'static', 'js', 'main.js')
    
    if not os.path.exists(js_file):
        print("  ✗ JavaScript file not found")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Check for legend elements
    legend_indicators = [
        "success-category-legend",
        "legend-grid",
        "legend-item",
        "Success Definition",
    ]
    
    found = sum(1 for indicator in legend_indicators if indicator in js_content)
    
    if found >= 3:
        print("  ✓ Legend implemented")
        return True
    else:
        print("  ✗ Legend may be incomplete")
        return False


def run_all_tests():
    """Run all UI/UX tests"""
    print("=" * 60)
    print("UI/UX VALIDATION TESTS")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("No WOMAC in UI", test_no_womac_in_ui()))
    results.append(("Success Categories Display", test_success_categories_in_ui()))
    results.append(("Color Coding", test_color_coding()))
    results.append(("Success Probability Display", test_success_probability_display()))
    results.append(("Legend Presence", test_legend_presence()))
    
    print()
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
        print("\n✅ All UI/UX tests passed!")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

