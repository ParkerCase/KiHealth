import pandas as pd
import csv

print("="*60)
print("EXTRACTING NRAS-MUTANT CELL LINES WITH CLK4 DATA")
print("="*60)

# Step 1: Get NRAS mutants
print("\n[1/4] Loading NRAS-mutant cell lines...")
nras_mutants = set()

with open('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/OmicsSomaticMutationsMatrixHotspot.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    for row in reader:
        try:
            if float(row[22]) > 0:  # NRAS is column 22 (0-indexed)
                nras_mutants.add(row[2])  # ModelID is column 2
        except:
            continue

print(f"   Found {len(nras_mutants)} NRAS-mutant cell lines")

# Step 2: Get CLK4 dependency
print("\n[2/4] Loading CLK4 dependency data...")
dep_data = []

with open('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/CRISPRGeneDependency.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    # Find CLK4
    clk4_col = None
    for i, col in enumerate(header):
        if 'CLK4' in col:
            clk4_col = i
            print(f"   CLK4 found in column {clk4_col}")
            break
    
    # Get NRAS mutants with CLK4 data
    for row in reader:
        model_id = row[0]
        if model_id in nras_mutants:
            try:
                clk4_dep = float(row[clk4_col])
                dep_data.append((model_id, clk4_dep))
            except:
                continue

print(f"   Found {len(dep_data)} NRAS-mutants with CLK4 data")

# Step 3: Get cell line names
print("\n[3/4] Loading cell line metadata...")
df_model = pd.read_csv('/Users/parkercase/starx-therapeutics-analysis/data/raw/depmap/Model.csv')
model_dict = df_model.set_index('ModelID')[['CellLineName', 'OncotreePrimaryDisease', 'OncotreeLineage']].to_dict('index')
print(f"   Loaded {len(model_dict)} cell line records")

# Step 4: Create output
print("\n[4/4] Creating output file...")
output = []
for model_id, clk4_dep in sorted(dep_data):
    if model_id in model_dict:
        output.append({
            'ModelID': model_id,
            'CellLineName': model_dict[model_id]['CellLineName'],
            'Cancer_Type': model_dict[model_id]['OncotreePrimaryDisease'],
            'Lineage': model_dict[model_id]['OncotreeLineage'],
            'CLK4_Dependency': round(clk4_dep, 6),
            'NRAS_Status': 'Mutant'
        })

df_out = pd.DataFrame(output)
out_path = '/Users/parkercase/starx-therapeutics-analysis/data/processed/NRAS_CLK4_cell_lines.csv'
df_out.to_csv(out_path, index=False)

print(f"   Saved to: {out_path}")

# Verify
print("\n" + "="*60)
print("VALIDATION")
print("="*60)
print(f"Expected from synthetic_lethality_results.csv: 97")
print(f"Actual cell lines found: {len(output)}")

if len(output) == 97:
    print("✅ COUNT MATCHES PERFECTLY!")
else:
    diff = len(output) - 97
    print(f"⚠️  Count difference: {diff:+d}")

print("\n" + "="*60)
print("SAMPLE OF NRAS-MUTANT CELL LINES (First 15)")
print("="*60)
print(df_out.head(15).to_string(index=False))

print("\n" + "="*60)
print("CANCER TYPE DISTRIBUTION")
print("="*60)
cancer_counts = df_out['Cancer_Type'].value_counts()
print(cancer_counts.head(10).to_string())

print("\n" + "="*60)
print("CLK4 DEPENDENCY STATISTICS")
print("="*60)
print(df_out['CLK4_Dependency'].describe())

print("\n✅ DONE!")
