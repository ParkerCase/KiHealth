import pandas as pd
import numpy as np

print("Loading data...")

# Load data
dep_data = pd.read_csv('data/processed/top_dependent_cell_lines.csv')
syn_let = pd.read_csv('data/processed/synthetic_lethality_results.csv')

# Load mutation data - check column names first
print("\nChecking mutation data structure...")
mutations = pd.read_csv('data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv', nrows=5)
print(f"Mutation file columns (first 10): {list(mutations.columns[:10])}")

mutations_full = pd.read_csv('data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv')
print(f"Total mutation columns: {len(mutations_full.columns)}")

# Load model info
print("\nChecking model data structure...")
model = pd.read_csv('data/raw/depmap/Model.csv', nrows=5)
print(f"Model file columns: {list(model.columns)}")

model_full = pd.read_csv('data/raw/depmap/Model.csv')

print("\n" + "="*80)
print("DETAILED CELL LINES FOR EACH SYNTHETIC LETHALITY RESULT")
print("="*80)

# Get all results with p < 0.10
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
    
    # Try different column name formats
    possible_cols = [
        f"{mutation} (mutation)",
        mutation,
        f"{mutation}_mutation",
    ]
    
    mutation_col = None
    for col_name in possible_cols:
        if col_name in mutations_full.columns:
            mutation_col = col_name
            break
    
    if mutation_col is None:
        # Search for partial match
        matching_cols = [col for col in mutations_full.columns if mutation in col]
        if matching_cols:
            mutation_col = matching_cols[0]
            print(f"\nNote: Using column '{mutation_col}'")
    
    if mutation_col:
        # Get cell lines with this mutation
        mutant_model_ids = mutations_full[mutations_full[mutation_col] == 1]['ModelID'].tolist()
        
        print(f"\nTotal cell lines with {mutation} mutation: {len(mutant_model_ids)}")
        
        # Match with our dependency data
        matching_lines = dep_data[dep_data['ModelID'].isin(mutant_model_ids)]
        
        if len(matching_lines) > 0:
            print(f"Cell lines in our dataset: {len(matching_lines)}")
            print(f"\n{'Cell Line':<25} {'Cancer Type':<40} {target + ' Dep':<12} Combined")
            print("-" * 95)
            
            # Sort by target dependency
            matching_sorted = matching_lines.sort_values(f'{target}_dependency')
            
            # Show top 20
            for _, line in matching_sorted.head(20).iterrows():
                cell_name = line['CellLineName'][:24]
                cancer = line['OncotreePrimaryDisease'][:39]
                target_dep = line[f'{target}_dependency']
                combined = line['combined_score']
                print(f"{cell_name:<25} {cancer:<40} {target_dep:>7.4f}     {combined:>7.4f}")
            
            if len(matching_sorted) > 20:
                print(f"\n... and {len(matching_sorted) - 20} more cell lines")
        else:
            print(f"(No matching cell lines found in our top-dependent dataset)")
    else:
        print(f"\n(Could not find {mutation} in mutation data)")

print("\n" + "="*80)
print("STK17B DEPENDENCY SCORES")
print("="*80)

# Load raw DepMap and extract STK17B
try:
    print("\nLoading DepMap dependency data...")
    depmap_full = pd.read_csv('data/raw/depmap/CRISPRGeneDependency.csv', nrows=5)
    print(f"DepMap columns (first 10): {list(depmap_full.columns[:10])}")
    
    depmap_full = pd.read_csv('data/raw/depmap/CRISPRGeneDependency.csv')
    
    stk17b_cols = [col for col in depmap_full.columns if 'STK17B' in col]
    stk17a_cols = [col for col in depmap_full.columns if 'STK17A' in col and 'STK17B' not in col]
    
    if stk17b_cols:
        stk17b_col = stk17b_cols[0]
        print(f"\nFound STK17B column: {stk17b_col}")
        
        stk17b_data = depmap_full[[depmap_full.columns[0], stk17b_col]].copy()
        stk17b_data.columns = ['ModelID', 'STK17B_dependency']
        
        # Merge with model info - use correct column name
        model_id_col = model_full.columns[0]
        cell_line_col = [col for col in model_full.columns if 'Cell' in col or 'Line' in col or 'Stripped' in col]
        disease_col = [col for col in model_full.columns if 'Disease' in col or 'Primary' in col]
        
        print(f"Model ID column: {model_id_col}")
        print(f"Cell line columns: {cell_line_col}")
        print(f"Disease columns: {disease_col}")
        
        if cell_line_col and disease_col:
            stk17b_with_info = stk17b_data.merge(
                model_full[[model_id_col, cell_line_col[0], disease_col[0]]],
                left_on='ModelID',
                right_on=model_id_col
            )
            
            # Get top dependent cell lines for STK17B
            top_stk17b = stk17b_with_info.nsmallest(20, 'STK17B_dependency')
            
            print(f"\nTop 20 STK17B-dependent cell lines:")
            print(f"{'Cell Line':<30} {'Cancer Type':<45} {'STK17B Dep'}")
            print("-" * 85)
            
            for _, line in top_stk17b.iterrows():
                cell_name = str(line[cell_line_col[0]])[:29]
                cancer = str(line[disease_col[0]])[:44]
                dep = line['STK17B_dependency']
                print(f"{cell_name:<30} {cancer:<45} {dep:>7.4f}")
            
            # Compare with STK17A
            if stk17a_cols:
                print("\n\nComparison: STK17A vs STK17B")
                print("="*80)
                
                stk17a_col = stk17a_cols[0]
                print(f"STK17A column: {stk17a_col}")
                
                comparison = depmap_full[[depmap_full.columns[0], stk17a_col, stk17b_col]].copy()
                comparison.columns = ['ModelID', 'STK17A_dependency', 'STK17B_dependency']
                
                # Merge with info
                comparison = comparison.merge(
                    model_full[[model_id_col, cell_line_col[0], disease_col[0]]],
                    left_on='ModelID',
                    right_on=model_id_col
                )
                
                # Calculate correlation
                corr = comparison['STK17A_dependency'].corr(comparison['STK17B_dependency'])
                print(f"\nCorrelation between STK17A and STK17B: {corr:.3f}")
                
                # Find lines most dependent on both
                comparison['avg_dependency'] = (comparison['STK17A_dependency'] + comparison['STK17B_dependency']) / 2
                top_both = comparison.nsmallest(15, 'avg_dependency')
                
                print(f"\nTop 15 cell lines dependent on BOTH STK17A and STK17B:")
                print(f"{'Cell Line':<30} {'Cancer Type':<40} {'STK17A':<9} {'STK17B':<9} {'Avg'}")
                print("-" * 100)
                
                for _, line in top_both.iterrows():
                    cell_name = str(line[cell_line_col[0]])[:29]
                    cancer = str(line[disease_col[0]])[:39]
                    stk17a = line['STK17A_dependency']
                    stk17b = line['STK17B_dependency']
                    avg = line['avg_dependency']
                    print(f"{cell_name:<30} {cancer:<40} {stk17a:>7.4f}  {stk17b:>7.4f}  {avg:>7.4f}")
    else:
        print("STK17B not found in DepMap")

except Exception as e:
    import traceback
    print(f"Error loading STK17B data: {e}")
    print(traceback.format_exc())

print("\n" + "="*80)
print("Done!")
