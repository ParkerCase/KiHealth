import pandas as pd

# Load data
syn_let = pd.read_csv('data/processed/synthetic_lethality_results.csv')

# TRUE synthetic lethality = NEGATIVE effect size (mutants MORE dependent)
true_sl = syn_let[syn_let['mean_diff'] < 0].sort_values('p_value')

print("="*80)
print("TRUE SYNTHETIC LETHALITY CANDIDATES")
print("(Negative Δ = mutants MORE dependent than wild-type)")
print("="*80)

for idx, row in true_sl.iterrows():
    mutation = row['mutation']
    target = row['target']
    p_val = row['p_value']
    delta = row['mean_diff']
    mutant_mean = row['mutant_mean']
    wt_mean = row['wt_mean']
    
    print(f"\n{mutation} × {target}:")
    print(f"  Δ = {delta:.4f} (NEGATIVE = mutants MORE dependent)")
    print(f"  Mutant cells: {mutant_mean:.4f} (more negative = more dependent)")
    print(f"  Wild-type cells: {wt_mean:.4f}")
    print(f"  p-value: {p_val:.4e}")
    
    if p_val < 0.10:
        print(f"  ✅ SIGNIFICANT (p < 0.10)")
        print(f"  INTERPRETATION: Cells with {mutation} mutation NEED {target} more!")
    else:
        print(f"  ❌ Not significant (p > 0.10)")

print("\n" + "="*80)
print("POSITIVE EFFECT SIZES (NOT Synthetic Lethality)")  
print("(Positive Δ = mutants LESS dependent = opposite of SL)")
print("="*80)

not_sl = syn_let[syn_let['mean_diff'] > 0].sort_values('p_value').head(10)

for idx, row in not_sl.iterrows():
    mutation = row['mutation']
    target = row['target']
    p_val = row['p_value']
    delta = row['mean_diff']
    
    print(f"\n{mutation} × {target}:")
    print(f"  Δ = {delta:.4f} (POSITIVE = mutants LESS dependent)")
    print(f"  p-value: {p_val:.4e}")
    
    if p_val < 0.10:
        print(f"  ⚠️  Significant difference, but NOT synthetic lethality")
        print(f"  This is suppressor/compensatory, not therapeutic target")
