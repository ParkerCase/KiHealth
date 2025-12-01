import pandas as pd
import numpy as np

print("Loading data...")

# Load the processed data
dep_data = pd.read_csv('data/processed/top_dependent_cell_lines.csv')
syn_let = pd.read_csv('data/processed/synthetic_lethality_results.csv')

# Load raw DepMap mutation data
mutations_hotspot = pd.read_csv('data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv')

print("\n" + "="*80)
print("1. NON-HODGKIN'S LYMPHOMA ANALYSIS")
print("="*80)

# Get Non-Hodgkin's Lymphoma cell lines
nhl = dep_data[dep_data['OncotreePrimaryDisease'] == 'Non-Hodgkin Lymphoma']
print(f"\nTotal NHL cell lines: {len(nhl)}")
print("\nCell line details:")
for idx, row in nhl.iterrows():
    print(f"\n  Cell Line: {row['CellLineName']}")
    print(f"    ModelID: {row['ModelID']}")
    print(f"    STK17A dependency: {row['STK17A_dependency']:.4f}")
    print(f"    CLK4 dependency: {row['CLK4_dependency']:.4f}")
    print(f"    TBK1 dependency: {row['TBK1_dependency']:.4f}")
    print(f"    MYLK4 dependency: {row['MYLK4_dependency']:.4f}")
    print(f"    Combined score: {row['combined_score']:.4f}")

# Check if they're the same cell line
if len(nhl) == 1:
    print("\n  ⚠️  ANSWER: Only ONE NHL cell line in dataset!")
    print(f"  The same cell line (SCC-3) shows both CLK4 and STK17A dependency.")

print("\n" + "="*80)
print("2. SYNTHETIC LETHALITY - SIGNIFICANT RESULTS")
print("="*80)

sig_results = syn_let[syn_let['significant'] == True]
print(f"\nTotal significant results: {len(sig_results)}\n")

for idx, row in sig_results.iterrows():
    mutation = row['mutation']
    target = row['target']
    
    print(f"\n{mutation} × {target}:")
    print(f"  p-value: {row['p_value']:.4e}")
    print(f"  Effect size (Δ): {row['mean_diff']:.4f}")
    print(f"  Sample sizes: {row['n_mutant']} mutant, {row['n_wt']} wild-type")
    
    # Try to find which cell lines have this mutation
    mutation_col = f"{mutation} (mutation)"
    if mutation_col in mutations_hotspot.columns:
        # Get cell lines with this mutation
        mutant_lines = mutations_hotspot[mutations_hotspot[mutation_col] == 1]['ModelID'].tolist()
        
        # Match with our dependent cell lines
        matching_lines = dep_data[dep_data['ModelID'].isin(mutant_lines)]
        
        if len(matching_lines) > 0:
            print(f"\n  Cell lines with {mutation} mutation:")
            for _, line in matching_lines.head(10).iterrows():  # Show first 10
                print(f"    - {line['CellLineName']} ({line['OncotreePrimaryDisease']})")
                print(f"      {target} dependency: {line[f'{target}_dependency']:.4f}")
        else:
            print(f"  (No matching cell lines found in top dependent dataset)")

print("\n" + "="*80)
print("3. STK17B CHECK")
print("="*80)

# Check dependency columns
dep_columns = dep_data.columns.tolist()
stk17_cols = [col for col in dep_columns if 'STK17' in col.upper()]
print(f"\nSTK17-related columns in dependency data: {stk17_cols}")

# Check raw DepMap files for STK17B
print("\nChecking raw DepMap files for STK17B...")
try:
    depmap_genes = pd.read_csv('data/raw/depmap/CRISPRGeneDependency.csv')
    stk17b_cols = [col for col in depmap_genes.columns if 'STK17B' in col.upper()]
    if stk17b_cols:
        print(f"✓ STK17B found in DepMap: {stk17b_cols}")
    else:
        print("✗ STK17B NOT found in DepMap dependency data")
except Exception as e:
    print(f"Error checking: {e}")

print("\n" + "="*80)
print("4. METHODOLOGY EXPLANATION - SYNTHETIC LETHALITY")
print("="*80)

print("""
How we got the synthetic lethality results:

1. Started with 237 cell lines from DepMap CRISPR screening
2. Loaded mutation data (hotspot mutations) for each cell line
3. For each mutation-target pair (e.g., PTEN × CLK4):
   - Grouped cell lines into: mutant vs wild-type
   - Compared their dependency scores for that target gene
   - Used Welch's t-test to check if difference is significant
   
4. Interpretation:
   - POSITIVE effect (Δ > 0) = Mutant cells are LESS dependent (mutation protects)
   - NEGATIVE effect (Δ < 0) = Mutant cells are MORE dependent (synthetic lethality)
   - p < 0.10 = Statistically significant difference

5. Example: PTEN × CLK4 (p=2.3e-07, Δ=+0.116)
   - Cells with PTEN mutation show HIGHER (less negative) CLK4 dependency
   - Meaning: PTEN-mutant cells rely MORE on CLK4
   - This is synthetic lethality candidate!
""")

print("\nDone!")
