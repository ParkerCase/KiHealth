#!/usr/bin/env python3
"""
Extract NRAS-mutant cell lines that were tested for CLK4 dependency.
This script efficiently processes large files without loading them entirely into memory.
"""

import pandas as pd
import csv

# Step 1: Get NRAS mutant ModelIDs from hotspot file
print("Step 1: Loading NRAS mutant cell lines...")
nras_mutants = set()

with open('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    # Find NRAS column (should be column 22, 0-indexed)
    nras_col = None
    modelid_col = 2  # ModelID is column 3 (0-indexed: 2)
    
    for i, col in enumerate(header):
        if 'NRAS' in col:
            nras_col = i
            break
    
    if nras_col is None:
        raise ValueError("NRAS column not found!")
    
    print(f"Found NRAS in column {nras_col}")
    
    # Get all NRAS-mutant ModelIDs
    for row in reader:
        if row[nras_col] == '1':
            nras_mutants.add(row[modelid_col])

print(f"Found {len(nras_mutants)} NRAS-mutant cell lines in mutation file")

# Step 2: Load CLK4 dependency data (just the columns we need)
print("\nStep 2: Loading CLK4 dependency data...")
# Use chunks to avoid memory issues
clk4_tested = {}

with open('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/CRISPRGeneDependency.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    # Find CLK4 column
    clk4_col = None
    for i, col in enumerate(header):
        if 'CLK4' in col:
            clk4_col = i
            break
    
    if clk4_col is None:
        raise ValueError("CLK4 column not found!")
    
    print(f"Found CLK4 in column {clk4_col}")
    
    # Get ModelID and CLK4 dependency for each cell line
    for row in reader:
        model_id = row[0]
        try:
            clk4_dep = float(row[clk4_col])
            clk4_tested[model_id] = clk4_dep
        except (ValueError, IndexError):
            continue

print(f"Found {len(clk4_tested)} cell lines with CLK4 dependency data")

# Step 3: Find intersection (NRAS mutants that have CLK4 data)
nras_with_clk4 = nras_mutants.intersection(set(clk4_tested.keys()))
print(f"\nFound {len(nras_with_clk4)} NRAS-mutant cell lines WITH CLK4 dependency data")

# Step 4: Get cell line names from Model.csv
print("\nStep 4: Getting cell line names...")
model_info = {}

df_model = pd.read_csv('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/Model.csv',
                      usecols=['ModelID', 'CellLineName', 'OncotreePrimaryDisease', 'OncotreeLineage'])

for _, row in df_model.iterrows():
    model_info[row['ModelID']] = {
        'CellLineName': row['CellLineName'],
        'Cancer': row['OncotreePrimaryDisease'],
        'Lineage': row['OncotreeLineage']
    }

# Step 5: Create output with all details
print("\nStep 5: Creating output file...")
output_data = []

for model_id in sorted(nras_with_clk4):
    if model_id in model_info:
        output_data.append({
            'ModelID': model_id,
            'CellLineName': model_info[model_id]['CellLineName'],
            'Cancer_Type': model_info[model_id]['Cancer'],
            'Lineage': model_info[model_id]['Lineage'],
            'CLK4_Dependency': clk4_tested[model_id],
            'NRAS_Status': 'Mutant'
        })

# Save to CSV
output_df = pd.DataFrame(output_data)
output_path = '/Users/parkercase/starx-therapeutics-analysis/data/processed/NRAS_CLK4_cell_lines.csv'
output_df.to_csv(output_path, index=False)

print(f"\n✅ SUCCESS!")
print(f"Saved {len(output_data)} NRAS-mutant cell lines to:")
print(f"  {output_path}")
print(f"\nTop 10 cell lines:")
print(output_df.head(10).to_string())

# Summary statistics
print(f"\n📊 SUMMARY:")
print(f"Total NRAS mutants in database: {len(nras_mutants)}")
print(f"NRAS mutants with CLK4 data: {len(nras_with_clk4)}")
print(f"Expected from synthetic_lethality_results.csv: 97")
print(f"Actual found: {len(output_data)}")

if len(output_data) != 97:
    print(f"\n⚠️  WARNING: Count mismatch! Expected 97, found {len(output_data)}")
else:
    print(f"\n✅ Count matches perfectly!")
