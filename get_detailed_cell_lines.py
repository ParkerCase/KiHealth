import pandas as pd
import numpy as np

print("Loading data...")

# Load data
dep_data = pd.read_csv('data/processed/top_dependent_cell_lines.csv')
syn_let = pd.read_csv('data/processed/synthetic_lethality_results.csv')
mutations_hotspot = pd.read_csv('data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv')

print("\n" + "="*80)
print("DETAILED CELL LINES FOR EACH SYNTHETIC LETHALITY RESULT")
print("="*80)

# Get all results with p < 0.10 (using actual threshold from analysis)
sig_results = syn_let[syn_let['p_value'] < 0.10].sort_values('p_value')
print(f"\nTotal results with p < 0.10: {len(sig_results)}\n")

for idx, row in sig_results.iterrows():
    mutation = row['mutation']
    target = row['target']
    
    print("\n" + "="*80)
    print(f"{mutation} × {target}")
    print("="*80)
    print(f"p-value: {row['p_value']:.4e}")
    print(f"Effect size (Δ): {row['mean_diff']:.4f}")
    print(f"Mutant mean: {row['mutant_mean']:.4f}")
    print(f"Wild-type mean: {row['wt_mean']:.4f}")
    print(f"Sample sizes: {row['n_mutant']} mutant, {row['n_wt']} wild-type")
    
    # Find cell lines with this mutation
    mutation_col = f"{mutation} (mutation)"
    if mutation_col in mutations_hotspot.columns:
        # Get cell lines with this mutation
        mutant_model_ids = mutations_hotspot[mutations_hotspot[mutation_col] == 1]['ModelID'].tolist()
        
        # Match with our dependency data
        matching_lines = dep_data[dep_data['ModelID'].isin(mutant_model_ids)]
        
        if len(matching_lines) > 0:
            print(f"\nCell lines with {mutation} mutation ({len(matching_lines)} total):")
            print(f"{'Cell Line':<25} {'Cancer Type':<40} {target + ' Dep':<12} Combined")
            print("-" * 95)
            
            # Sort by target dependency
            matching_sorted = matching_lines.sort_values(f'{target}_dependency')
            
            for _, line in matching_sorted.iterrows():
                cell_name = line['CellLineName'][:24]
                cancer = line['OncotreePrimaryDisease'][:39]
                target_dep = line[f'{target}_dependency']
                combined = line['combined_score']
                print(f"{cell_name:<25} {cancer:<40} {target_dep:>7.4f}     {combined:>7.4f}")
        else:
            print(f"\n  (No matching cell lines found in dependency dataset)")
    else:
        print(f"\n  (Mutation column not found in hotspot data)")

print("\n" + "="*80)
print("STK17B DEPENDENCY SCORES")
print("="*80)

# Load raw DepMap and extract STK17B
try:
    depmap_full = pd.read_csv('data/raw/depmap/CRISPRGeneDependency.csv')
    stk17b_col = [col for col in depmap_full.columns if 'STK17B' in col][0]
    
    # Merge with cell line info
    model_info = pd.read_csv('data/raw/depmap/Model.csv')
    
    stk17b_data = depmap_full[['ModelID', stk17b_col]].copy()
    stk17b_data.columns = ['ModelID', 'STK17B_dependency']
    
    # Merge with cancer types
    stk17b_with_info = stk17b_data.merge(
        model_info[['ModelID', 'OncotreePrimaryDisease', 'StrippedCellLineName']],
        on='ModelID'
    )
    
    # Get top dependent cell lines for STK17B
    top_stk17b = stk17b_with_info.nsmallest(20, 'STK17B_dependency')
    
    print(f"\nTop 20 STK17B-dependent cell lines:")
    print(f"{'Cell Line':<25} {'Cancer Type':<40} {'STK17B Dep'}")
    print("-" * 75)
    
    for _, line in top_stk17b.iterrows():
        cell_name = str(line['StrippedCellLineName'])[:24]
        cancer = str(line['OncotreePrimaryDisease'])[:39]
        dep = line['STK17B_dependency']
        print(f"{cell_name:<25} {cancer:<40} {dep:>7.4f}")
    
    # Compare with STK17A
    print("\n\nComparison: STK17A vs STK17B")
    print("="*80)
    
    # Find STK17A column
    stk17a_col = [col for col in depmap_full.columns if 'STK17A' in col][0]
    comparison = depmap_full[['ModelID', stk17a_col, stk17b_col]].copy()
    comparison.columns = ['ModelID', 'STK17A_dependency', 'STK17B_dependency']
    
    # Merge with info
    comparison = comparison.merge(
        model_info[['ModelID', 'StrippedCellLineName', 'OncotreePrimaryDisease']],
        on='ModelID'
    )
    
    # Calculate correlation
    corr = comparison['STK17A_dependency'].corr(comparison['STK17B_dependency'])
    print(f"\nCorrelation between STK17A and STK17B: {corr:.3f}")
    
    # Find lines most dependent on both
    comparison['avg_dependency'] = (comparison['STK17A_dependency'] + comparison['STK17B_dependency']) / 2
    top_both = comparison.nsmallest(15, 'avg_dependency')
    
    print(f"\nTop 15 cell lines dependent on BOTH STK17A and STK17B:")
    print(f"{'Cell Line':<25} {'Cancer Type':<35} {'STK17A':<9} {'STK17B':<9} {'Avg'}")
    print("-" * 95)
    
    for _, line in top_both.iterrows():
        cell_name = str(line['StrippedCellLineName'])[:24]
        cancer = str(line['OncotreePrimaryDisease'])[:34]
        stk17a = line['STK17A_dependency']
        stk17b = line['STK17B_dependency']
        avg = line['avg_dependency']
        print(f"{cell_name:<25} {cancer:<35} {stk17a:>7.4f}  {stk17b:>7.4f}  {avg:>7.4f}")

except Exception as e:
    print(f"Error loading STK17B data: {e}")

print("\n" + "="*80)
print("Done!")
