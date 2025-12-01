"""
Test script for DOC Risk Calculator
===================================
Quick test to verify the calculator works correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from risk_calculator.app import preprocess_input, get_risk_category, get_clinical_interpretation
import joblib

# Load model
model_path = Path(__file__).parent.parent / "models" / "random_forest_best.pkl"
model = joblib.load(model_path)

print("=" * 60)
print("DOC RISK CALCULATOR - TEST")
print("=" * 60)

# Test case 1: High risk patient
print("\nTest Case 1: High Risk Patient")
print("-" * 60)
test_data_1 = {
    "age": "70",
    "sex": "Female",
    "bmi": "32.0",
    "womac_right": "60.0",
    "womac_left": "65.0",
    "kl_right": "4",
    "kl_left": "4",
    "family_history": "Yes",
}

X1 = preprocess_input(test_data_1)
pred1 = model.predict_proba(X1)[0, 1]
risk1 = pred1 * 100
category1, color1 = get_risk_category(risk1)
interpretation1 = get_clinical_interpretation(risk1, category1)

print(f"Age: {test_data_1['age']}, BMI: {test_data_1['bmi']}")
print(f"WOMAC: R={test_data_1['womac_right']}, L={test_data_1['womac_left']}")
print(f"KL Grade: R={test_data_1['kl_right']}, L={test_data_1['kl_left']}")
print(f"Family History: {test_data_1['family_history']}")
print(f"\nPredicted Risk: {risk1:.1f}%")
print(f"Category: {category1}")
print(f"Interpretation: {interpretation1[:100]}...")

# Test case 2: Low risk patient
print("\n\nTest Case 2: Low Risk Patient")
print("-" * 60)
test_data_2 = {
    "age": "50",
    "sex": "Male",
    "bmi": "24.0",
    "womac_right": "5.0",
    "womac_left": "8.0",
    "kl_right": "1",
    "kl_left": "1",
    "family_history": "No",
}

X2 = preprocess_input(test_data_2)
pred2 = model.predict_proba(X2)[0, 1]
risk2 = pred2 * 100
category2, color2 = get_risk_category(risk2)
interpretation2 = get_clinical_interpretation(risk2, category2)

print(f"Age: {test_data_2['age']}, BMI: {test_data_2['bmi']}")
print(f"WOMAC: R={test_data_2['womac_right']}, L={test_data_2['womac_left']}")
print(f"KL Grade: R={test_data_2['kl_right']}, L={test_data_2['kl_left']}")
print(f"Family History: {test_data_2['family_history']}")
print(f"\nPredicted Risk: {risk2:.1f}%")
print(f"Category: {category2}")
print(f"Interpretation: {interpretation2[:100]}...")

print("\n" + "=" * 60)
print("✓ Calculator test complete")
print("=" * 60)

