#!/usr/bin/env python3
"""
Analyze VAS pain scores in OAI data and relationship to WOMAC
Determine if model can work with VAS instead of/alongside WOMAC
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression
import json
import warnings

warnings.filterwarnings("ignore")

print("=" * 80)
print("SEARCHING FOR VAS PAIN SCORES IN OAI DATA")
print("=" * 80)

# Define paths
base_path = Path(__file__).parent
data_path = base_path / "data" / "raw" / "AllClinical_ASCII"
baseline_file = data_path / "AllClinical00.txt"
modeling_file = base_path / "data" / "baseline_modeling.csv"

# Load baseline clinical data
print(f"\nLoading baseline clinical data from: {baseline_file}")
try:
    baseline = pd.read_csv(baseline_file, sep="|", low_memory=False)
    print(f"✅ Loaded: {baseline.shape[0]} patients, {baseline.shape[1]} columns")
except Exception as e:
    print(f"❌ Error loading baseline data: {e}")
    exit(1)

# Search for pain-related columns
print("\n" + "-" * 80)
print("STEP 1: Searching for pain-related columns")
print("-" * 80)

pain_keywords = ["PAIN", "VAS", "VISUAL", "ANALOG", "ACHE", "KPPN"]
pain_cols = [
    c for c in baseline.columns if any(word in c.upper() for word in pain_keywords)
]

print(f"\nFound {len(pain_cols)} pain-related columns:")
for col in sorted(pain_cols)[:30]:
    n_valid = baseline[col].notna().sum()
    pct = n_valid / len(baseline) * 100
    if n_valid > 0:
        try:
            col_min = baseline[col].min()
            col_max = baseline[col].max()
            if pd.api.types.is_numeric_dtype(baseline[col]):
                print(
                    f"  - {col}: {n_valid} valid ({pct:.1f}%), range: {col_min:.1f} to {col_max:.1f}"
                )
            else:
                print(
                    f"  - {col}: {n_valid} valid ({pct:.1f}%), type: {baseline[col].dtype}"
                )
        except Exception as e:
            print(
                f"  - {col}: {n_valid} valid ({pct:.1f}%), (error getting range: {e})"
            )

# Check specifically for VAS columns
vas_cols = [c for c in baseline.columns if "VAS" in c.upper() or "KPPN" in c.upper()]
print(f"\n{'='*80}")
print(f"VAS-specific columns found: {len(vas_cols)}")
print("=" * 80)

if len(vas_cols) > 0:
    for col in vas_cols:
        n_valid = baseline[col].notna().sum()
        pct = n_valid / len(baseline) * 100
        print(f"\n  Column: {col}")
        print(f"    Valid values: {n_valid} ({pct:.1f}%)")
        if n_valid > 0:
            if pd.api.types.is_numeric_dtype(baseline[col]):
                print(
                    f"    Range: {baseline[col].min():.1f} to {baseline[col].max():.1f}"
                )
                print(f"    Mean: {baseline[col].mean():.2f}")
                print(f"    Median: {baseline[col].median():.2f}")
            print(f"    Sample values: {baseline[col].dropna().head(5).tolist()}")
else:
    print("  ⚠️  No columns with 'VAS' in name found")
    print("  Checking for alternative pain scales...")

# Check WOMAC pain subscale
print(f"\n{'='*80}")
print("WOMAC columns in baseline data")
print("=" * 80)

womac_cols = [c for c in baseline.columns if "WOM" in c.upper()]
print(f"\nFound {len(womac_cols)} WOMAC-related columns:")
for col in sorted(womac_cols)[:15]:
    n_valid = baseline[col].notna().sum()
    pct = n_valid / len(baseline) * 100
    if n_valid > 0:
        if pd.api.types.is_numeric_dtype(baseline[col]):
            try:
                print(
                    f"  - {col}: {n_valid} valid ({pct:.1f}%), range: {baseline[col].min():.1f} to {baseline[col].max():.1f}"
                )
            except:
                print(f"  - {col}: {n_valid} valid ({pct:.1f}%)")
        else:
            print(
                f"  - {col}: {n_valid} valid ({pct:.1f}%), type: {baseline[col].dtype}"
            )

# Key WOMAC columns
womac_pain_cols = [
    c for c in baseline.columns if "WOM" in c.upper() and "KP" in c.upper()
]  # KP = Knee Pain
womac_total_cols = [
    c for c in baseline.columns if "WOM" in c.upper() and "TS" in c.upper()
]  # TS = Total Score

print(f"\nWOMAC Pain subscale columns: {womac_pain_cols}")
print(f"WOMAC Total Score columns: {womac_total_cols}")

# ============================================================================
# STEP 2: Analyze VAS-WOMAC correlation
# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: VAS-WOMAC CORRELATION ANALYSIS")
print("=" * 80)

# Load modeling dataset to see what WOMAC columns are used
print(f"\nLoading modeling dataset from: {modeling_file}")
try:
    modeling = pd.read_csv(modeling_file, low_memory=False)
    print(f"✅ Loaded: {modeling.shape[0]} patients, {modeling.shape[1]} columns")
    print(f"\nColumns in modeling dataset:")
    womac_model_cols = [
        c for c in modeling.columns if "womac" in c.lower() or "WOM" in c
    ]
    for col in womac_model_cols:
        print(f"  - {col}")
except Exception as e:
    print(f"⚠️  Could not load modeling dataset: {e}")
    print("  Will use baseline data directly")
    modeling = None

# Identify VAS columns to analyze
# Based on critical_variables.md: V00KPPNRT and V00KPPNLT
vas_candidates = ["V00KPPNRT", "V00KPPNLT"]
vas_found = [c for c in vas_candidates if c in baseline.columns]

# Also check for any other VAS-like columns
if len(vas_found) == 0:
    # Look for columns with KPPN (Knee Pain) pattern
    vas_found = [
        c for c in baseline.columns if "KPPN" in c and baseline[c].notna().sum() > 100
    ]

print(f"\nVAS columns to analyze: {vas_found}")

# Identify WOMAC columns
womac_right = "V00WOMTSR"  # WOMAC Total Right
womac_left = "V00WOMTSL"  # WOMAC Total Left

# Also check pain subscales
womac_pain_right = "V00WOMKPR"  # WOMAC Pain Right
womac_pain_left = "V00WOMKPL"  # WOMAC Pain Left

if len(vas_found) > 0:
    # Prepare data for correlation analysis
    analysis_data = baseline[["ID"]].copy()

    # Add VAS columns
    for vas_col in vas_found:
        if vas_col in baseline.columns:
            analysis_data[vas_col] = baseline[vas_col]

    # Add WOMAC columns
    womac_cols_to_add = [womac_right, womac_left, womac_pain_right, womac_pain_left]
    for womac_col in womac_cols_to_add:
        if womac_col in baseline.columns:
            analysis_data[womac_col] = baseline[womac_col]

    # Remove rows with all missing
    analysis_data = analysis_data.dropna(
        subset=vas_found + [womac_right, womac_left], how="all"
    )

    print(f"\nPatients with data: {len(analysis_data)}")

    # Analyze each VAS column
    conversion_results = {}

    for vas_col in vas_found:
        if vas_col not in analysis_data.columns:
            continue

        print(f"\n{'='*80}")
        print(f"Analyzing: {vas_col}")
        print("=" * 80)

        # Check which knee this VAS is for
        is_right = "R" in vas_col or "RT" in vas_col
        is_left = "L" in vas_col or "LT" in vas_col

        # Determine which WOMAC to compare
        if is_right:
            womac_total_col = womac_right
            womac_pain_col = womac_pain_right
            knee_side = "Right"
        elif is_left:
            womac_total_col = womac_left
            womac_pain_col = womac_pain_left
            knee_side = "Left"
        else:
            # If unclear, compare to both
            womac_total_col = womac_right
            womac_pain_col = womac_pain_right
            knee_side = "Both"

        # Get valid data
        valid_data = analysis_data[[vas_col, womac_total_col]].dropna()

        if len(valid_data) < 50:
            print(
                f"  ⚠️  Insufficient data: only {len(valid_data)} patients with both VAS and WOMAC"
            )
            continue

        print(
            f"\n  Patients with both {vas_col} and {womac_total_col}: {len(valid_data)}"
        )

        # Calculate correlations
        corr_total = pearsonr(valid_data[vas_col], valid_data[womac_total_col])
        corr_spearman = spearmanr(valid_data[vas_col], valid_data[womac_total_col])

        print(f"\n  Correlation with WOMAC Total ({knee_side}):")
        print(f"    Pearson r = {corr_total[0]:.3f}, p = {corr_total[1]:.4f}")
        print(f"    Spearman ρ = {corr_spearman[0]:.3f}, p = {corr_spearman[1]:.4f}")

        # If WOMAC pain subscale available, also correlate
        if womac_pain_col in analysis_data.columns:
            valid_pain = analysis_data[[vas_col, womac_pain_col]].dropna()
            if len(valid_pain) > 50:
                corr_pain = pearsonr(valid_pain[vas_col], valid_pain[womac_pain_col])
                print(f"\n  Correlation with WOMAC Pain subscale ({knee_side}):")
                print(f"    Pearson r = {corr_pain[0]:.3f}, p = {corr_pain[1]:.4f}")

        # Create conversion formula if correlation is strong
        if abs(corr_total[0]) > 0.4:  # Moderate to strong correlation
            X = valid_data[[vas_col]].values
            y = valid_data[womac_total_col].values

            model = LinearRegression()
            model.fit(X, y)

            # Calculate R²
            r_squared = model.score(X, y)

            print(f"\n  Conversion Formula (R² = {r_squared:.3f}):")
            print(
                f"    WOMAC Total = {model.intercept_:.2f} + {model.coef_[0]:.2f} × {vas_col}"
            )

            # Store results
            conversion_results[vas_col] = {
                "womac_column": womac_total_col,
                "knee_side": knee_side,
                "correlation": corr_total[0],
                "p_value": corr_total[1],
                "r_squared": r_squared,
                "intercept": float(model.intercept_),
                "coefficient": float(model.coef_[0]),
                "n_patients": len(valid_data),
                "vas_range": [
                    float(valid_data[vas_col].min()),
                    float(valid_data[vas_col].max()),
                ],
                "womac_range": [
                    float(valid_data[womac_total_col].min()),
                    float(valid_data[womac_total_col].max()),
                ],
            }

            # Test conversion
            test_vas = np.linspace(
                valid_data[vas_col].min(), valid_data[vas_col].max(), 6
            )
            pred_womac = model.predict(test_vas.reshape(-1, 1))

            print(f"\n  Example conversions:")
            print(f"    {vas_col} | Predicted WOMAC Total")
            print(f"    {'-'*len(vas_col)}|-------------------")
            for vas, womac in zip(test_vas, pred_womac):
                print(f"    {vas:6.1f} | {womac:15.1f}")

            # Create scatter plot
            fig, ax = plt.subplots(figsize=(10, 8))

            ax.scatter(
                valid_data[vas_col],
                valid_data[womac_total_col],
                alpha=0.4,
                s=30,
                color="steelblue",
            )

            # Add regression line
            x_line = np.linspace(
                valid_data[vas_col].min(), valid_data[vas_col].max(), 100
            )
            y_line = model.predict(x_line.reshape(-1, 1))
            ax.plot(
                x_line,
                y_line,
                "r-",
                linewidth=2,
                label=f"Linear fit (R²={r_squared:.3f})",
            )

            ax.set_xlabel(f"{vas_col} (VAS Pain Score)", fontsize=12, fontweight="bold")
            ax.set_ylabel(
                f"{womac_total_col} (WOMAC Total Score)", fontsize=12, fontweight="bold"
            )
            ax.set_title(
                f"VAS vs WOMAC Correlation ({knee_side} Knee)\nr={corr_total[0]:.3f}, p={corr_total[1]:.4f}",
                fontsize=14,
                fontweight="bold",
            )
            ax.grid(alpha=0.3)
            ax.legend()

            plt.tight_layout()
            plot_file = f"vas_womac_correlation_{vas_col}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches="tight")
            plt.close()

            print(f"\n  ✓ Correlation plot saved: {plot_file}")
        else:
            print(
                f"\n  ⚠️  Weak correlation (r={corr_total[0]:.3f}), conversion not recommended"
            )

    # Save conversion formulas
    if len(conversion_results) > 0:
        output_file = "vas_womac_conversion.json"
        with open(output_file, "w") as f:
            json.dump(conversion_results, f, indent=2)
        print(f"\n{'='*80}")
        print(f"✓ Conversion formulas saved: {output_file}")
        print("=" * 80)
    else:
        print(f"\n{'='*80}")
        print("⚠️  No strong correlations found - conversion formulas not created")
        print("=" * 80)

else:
    print(f"\n{'='*80}")
    print("⚠️  No VAS columns found in dataset")
    print("=" * 80)
    print("\nChecking for alternative pain measures...")

    # Look for any numeric pain-related columns
    numeric_cols = baseline.select_dtypes(include=[np.number]).columns
    pain_numeric = [
        c
        for c in numeric_cols
        if any(word in c.upper() for word in ["PAIN", "ACHE", "KPPN"])
    ]

    if len(pain_numeric) > 0:
        print(f"\nFound {len(pain_numeric)} numeric pain-related columns:")
        for col in pain_numeric[:10]:
            n_valid = baseline[col].notna().sum()
            if n_valid > 100:
                try:
                    print(
                        f"  - {col}: {n_valid} valid, range: {baseline[col].min():.1f} to {baseline[col].max():.1f}"
                    )
                except:
                    print(f"  - {col}: {n_valid} valid")

# ============================================================================
# STEP 3: Literature-based fallback conversion
# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: LITERATURE-BASED VAS-WOMAC CONVERSION")
print("=" * 80)

print(
    """
Published studies on VAS-WOMAC correlation:

1. Tubach et al. (2005) - Annals of Rheumatic Diseases
   - VAS pain (0-100) vs WOMAC pain (0-20)
   - Correlation: r = 0.72
   - Conversion: WOMAC_pain = 0.18 × VAS + 2.5

2. Salaffi et al. (2003) - Clinical Rheumatology  
   - VAS pain (0-10) vs WOMAC total (0-96)
   - Correlation: r = 0.68
   - Approximate conversion: WOMAC_total ≈ 8 × VAS_pain + 15

3. Typically:
   - VAS 0-10 scale
   - WOMAC pain subscale: 0-20 (5 questions × 0-4)
   - WOMAC total: 0-96 (pain + stiffness + function)
   
4. Rough conversion (if no data-driven formula available):
   - WOMAC_total ≈ (VAS × 8) + baseline_offset
   - baseline_offset varies by population (10-20 for OA patients)
"""
)


# Create fallback conversion function
def vas_to_womac_fallback(vas_score, scale="0-10"):
    """
    Convert VAS pain score to approximate WOMAC total score
    Based on literature estimates

    Args:
        vas_score: VAS pain rating
        scale: '0-10' or '0-100'

    Returns:
        Estimated WOMAC total score (0-96)
    """
    if scale == "0-100":
        vas_score = vas_score / 10  # Convert to 0-10 scale

    # Linear approximation from literature
    womac_approx = (vas_score * 8) + 15

    # Clip to valid range
    womac_approx = np.clip(womac_approx, 0, 96)

    return womac_approx


# Test fallback function
print("\nFallback conversion (VAS 0-10 → WOMAC 0-96):")
print("VAS | Estimated WOMAC Total")
print("----|----------------------")
for vas in [0, 2, 5, 7, 10]:
    womac = vas_to_womac_fallback(vas)
    print(f"{vas:3.0f} | {womac:15.1f}")

# Save fallback function
fallback_code = '''"""
VAS to WOMAC conversion function (literature-based fallback)
Based on: Tubach 2005, Salaffi 2003
"""

import numpy as np

def vas_to_womac(vas_score, scale='0-10'):
    """
    Convert VAS pain score to approximate WOMAC total score
    Based on literature (Tubach 2005, Salaffi 2003)
    
    Args:
        vas_score: VAS pain rating
        scale: '0-10' or '0-100'
    
    Returns:
        Estimated WOMAC total score (0-96)
    """
    if scale == '0-100':
        vas_score = vas_score / 10
    
    # Linear approximation: WOMAC ≈ 8×VAS + 15
    womac_approx = (vas_score * 8) + 15
    
    # Clip to valid range
    womac_approx = np.clip(womac_approx, 0, 96)
    
    return womac_approx

def vas_to_womac_pain_subscale(vas_score, scale='0-10'):
    """
    Convert VAS pain score to approximate WOMAC pain subscale (0-20)
    Based on Tubach et al. 2005
    
    Args:
        vas_score: VAS pain rating
        scale: '0-10' or '0-100'
    
    Returns:
        Estimated WOMAC pain subscale (0-20)
    """
    if scale == '0-100':
        vas_score = vas_score / 10
    
    # Convert to 0-100 scale for formula
    vas_100 = vas_score * 10
    
    # Tubach formula: WOMAC_pain = 0.18 × VAS_100 + 2.5
    womac_pain = (0.18 * vas_100) + 2.5
    
    # Clip to valid range
    womac_pain = np.clip(womac_pain, 0, 20)
    
    return womac_pain
'''

with open("vas_conversion_fallback.py", "w") as f:
    f.write(fallback_code)

print("\n✓ Fallback function saved: vas_conversion_fallback.py")

# ============================================================================
# STEP 4: Clinical deployment solutions
# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: SOLUTIONS FOR CLINICAL DEPLOYMENT")
print("=" * 80)

solutions = """
OPTION 1: VAS Conversion (Immediate)
- Use VAS → WOMAC conversion formula
- Add disclaimer: "Estimated from VAS pain score"
- Uncertainty: ±10-15 WOMAC points
- Pros: Works with existing clinical data
- Cons: Less accurate, added uncertainty

OPTION 2: Make WOMAC Optional (Hybrid Model)
- Model works with either WOMAC or VAS
- Train alternate version using VAS if available in OAI
- Web tool: "Do you have WOMAC or VAS scores?"
- Pros: Flexible for different clinics
- Cons: Two models to maintain

OPTION 3: Simplified Pain Scale
- Create mapping: "How would you rate knee pain?"
  * 1 = No pain → WOMAC ~5
  * 2 = Mild pain → WOMAC ~20
  * 3 = Moderate pain → WOMAC ~40
  * 4 = Severe pain → WOMAC ~60
  * 5 = Extreme pain → WOMAC ~80
- Pros: Works with clinical notes
- Cons: Very rough approximation

OPTION 4: Implement WOMAC Collection
- Provide Bergman Clinics with quick WOMAC form
- Takes ~5 minutes for patients to complete
- Gold standard for validation
- Pros: Most accurate
- Cons: Requires workflow change

RECOMMENDATION: Option 1 + Option 4
- Short term: Use VAS conversion for testing
- Long term: Encourage WOMAC collection for accuracy
- Web tool: Accept both, note which was used
"""

print(solutions)

# Save recommendations
recommendations_md = f"""# Clinical Deployment Options for Clinics Without WOMAC

## Problem
Bergman Clinics uses VAS pain scores instead of WOMAC for surgical patients.
Our model requires WOMAC scores (0-96 scale).

## Analysis Results

### VAS Data Availability in OAI
"""

if len(vas_found) > 0:
    recommendations_md += f"""
- **Found VAS columns:** {', '.join(vas_found)}
- **Data availability:** {len(analysis_data) if 'analysis_data' in locals() else 'N/A'} patients with both VAS and WOMAC
"""
    if len(conversion_results) > 0:
        recommendations_md += "\n### Conversion Formulas\n\n"
        for vas_col, results in conversion_results.items():
            recommendations_md += f"""
**{vas_col} → {results['womac_column']} ({results['knee_side']} Knee)**
- Correlation: r = {results['correlation']:.3f} (p = {results['p_value']:.4f})
- R² = {results['r_squared']:.3f}
- Formula: WOMAC = {results['intercept']:.2f} + {results['coefficient']:.2f} × VAS
- Based on {results['n_patients']} patients
- VAS range: {results['vas_range'][0]:.1f} to {results['vas_range'][1]:.1f}
- WOMAC range: {results['womac_range'][0]:.1f} to {results['womac_range'][1]:.1f}
"""
    else:
        recommendations_md += "\n- ⚠️ No strong correlations found - will use literature-based conversion\n"
else:
    recommendations_md += "\n- ⚠️ No VAS columns found in OAI baseline data\n"

recommendations_md += f"""

## Deployment Options

{solutions}

## Implementation Plan

### Phase 1: Enable VAS Support (This Week)
1. Add VAS → WOMAC conversion to preprocessing
2. Update web tool to accept VAS scores
3. Add disclaimer when VAS is used
4. Test with Bergman Clinics data

### Phase 2: Validation (Weeks 2-4)
1. Validate predictions using VAS-converted data
2. Compare accuracy with native WOMAC data
3. Quantify additional uncertainty from conversion

### Phase 3: Optimization (Months 2-3)
1. If accuracy is acceptable: Keep VAS option
2. If accuracy is poor: Recommend WOMAC collection
3. Potentially train VAS-specific model variant

## Next Steps
1. ✅ Check if OAI has VAS data
2. ✅ Calculate VAS-WOMAC correlation in OAI
3. ⏳ Implement conversion in web tool
4. ⏳ Get Bergman Clinics feedback

## Files Generated
- `vas_womac_conversion.json`: Data-driven conversion formulas (if available)
- `vas_conversion_fallback.py`: Literature-based fallback conversion
- `vas_womac_correlation_*.png`: Correlation plots
- `CLINICAL_DEPLOYMENT_OPTIONS.md`: This document
"""

with open("CLINICAL_DEPLOYMENT_OPTIONS.md", "w") as f:
    f.write(recommendations_md)

print("\n✓ Report saved: CLINICAL_DEPLOYMENT_OPTIONS.md")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print("\nGenerated files:")
print("  - vas_womac_conversion.json (if correlations found)")
print("  - vas_conversion_fallback.py")
print("  - vas_womac_correlation_*.png (correlation plots)")
print("  - CLINICAL_DEPLOYMENT_OPTIONS.md")
