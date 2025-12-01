#!/bin/bash

echo "Extracting NRAS-mutant cell lines with CLK4 dependency data..."

# Step 1: Extract NRAS mutant ModelIDs
cd /Users/parkercase/starx-therapeutics-analysis/data/raw/depmap
awk -F',' 'NR>1 && $23 > 0 {print $3}' OmicsSomaticMutationsMatrixHotspot.csv > /tmp/nras_mutants.txt

echo "Found $(wc -l < /tmp/nras_mutants.txt) NRAS-mutant cell lines"

# Step 2: Get CLK4 dependency for these cell lines
# First find CLK4 column
echo "Getting CLK4 dependency data..."
python3 << 'PYTHON_END'
import pandas as pd
import csv

# Load NRAS mutants
with open('/tmp/nras_mutants.txt', 'r') as f:
    nras_mutants = set(line.strip() for line in f)

print(f"Loaded {len(nras_mutants)} NRAS-mutant ModelIDs")

# Get CLK4 dependency - read in chunks
print("Loading CLK4 dependency data...")
dep_data = []

with open('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/CRISPRGeneDependency.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    # Find CLK4 column
    clk4_col = None
    for i, col in enumerate(header):
        if 'CLK4' in col:
            clk4_col = i
            break
    
    print(f"Found CLK4 in column {clk4_col}")
    
    # Get dependency for NRAS mutants only
    for row in reader:
        model_id = row[0]
        if model_id in nras_mutants:
            try:
                clk4_dep = float(row[clk4_col])
                dep_data.append((model_id, clk4_dep))
            except (ValueError, IndexError):
                continue

print(f"Found {len(dep_data)} NRAS-mutant cell lines with CLK4 data")

# Get cell line info
print("Getting cell line names...")
df_model = pd.read_csv('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/Model.csv')
model_dict = df_model.set_index('ModelID')[['CellLineName', 'OncotreePrimaryDisease', 'OncotreeLineage']].to_dict('index')

# Create output
output = []
for model_id, clk4_dep in dep_data:
    if model_id in model_dict:
        output.append({
            'ModelID': model_id,
            'CellLineName': model_dict[model_id]['CellLineName'],
            'Cancer_Type': model_dict[model_id]['OncotreePrimaryDisease'],
            'Lineage': model_dict[model_id]['OncotreeLineage'],
            'CLK4_Dependency': clk4_dep,
            'NRAS_Status': 'Mutant'
        })

# Save
df_out = pd.DataFrame(output)
out_path = '/Users/parkercase/starx-therapeutics-analysis/data/processed/NRAS_CLK4_cell_lines.csv'
df_out.to_csv(out_path, index=False)

print(f"\n✅ Saved {len(output)} cell lines to: {out_path}")
print(f"\nExpected: 97")
print(f"Found: {len(output)}")

if len(output) == 97:
    print("✅ COUNT MATCHES!")
else:
    print(f"⚠️  Count mismatch by {abs(len(output)-97)}")

print("\n📊 Top 10 cell lines:")
print(df_out.head(10).to_string())
PYTHON_END

echo "Done!"
