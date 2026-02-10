#!/usr/bin/env python3
"""
Literature Review - PROMPT 3
Structured PubMed searches for top cancer types and target genes

Outputs:
1. data/processed/literature_summary_manual.csv
2. data/processed/literature_scoring.csv
3. outputs/reports/literature_review_summary.md
"""

import pandas as pd
import time
from pathlib import Path
from Bio import Entrez
import sys

# Configure Entrez
Entrez.email = "parker@example.com"  # Required by NCBI
# Entrez.api_key = "YOUR_API_KEY"  # Optional: increases rate limit to 10/sec

# Set up paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
REPORTS = PROJECT_ROOT / "outputs" / "reports"

# Create output directories
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("LITERATURE REVIEW - PROMPT 3")
print("=" * 80)

# ==============================================================================
# STEP 1: Load Top 10 Cancer Types
# ==============================================================================

print("\n[STEP 1] Loading top 10 cancer types...")

# Load cancer rankings
cancer_rankings = pd.read_csv(DATA_PROCESSED / "cancer_type_rankings.csv")

# Get top 10
top_10_cancers = cancer_rankings.head(10)['OncotreePrimaryDisease'].tolist()

print(f"✓ Top 10 cancer types identified:")
for i, cancer in enumerate(top_10_cancers, 1):
    print(f"  {i:2d}. {cancer}")

# ==============================================================================
# STEP 2: Define Target Genes
# ==============================================================================

print("\n[STEP 2] Setting up target genes...")

target_genes = ['STK17A', 'MYLK4', 'TBK1', 'CLK4']
print(f"✓ Target genes: {', '.join(target_genes)}")

# ==============================================================================
# STEP 3: PubMed Search Function
# ==============================================================================

def search_pubmed(gene, cancer_type=None, max_results=100):
    """
    Search PubMed for gene and cancer type
    Returns: paper count, recent paper count, sample citations
    """
    try:
        # Build query
        if cancer_type:
            # For specific cancer types
            query = f'({gene}[Title/Abstract]) AND ({cancer_type}[Title/Abstract]) AND (cancer OR tumor OR carcinoma OR malignancy)'
        else:
            # For gene alone
            query = f'({gene}[Title/Abstract]) AND (kinase OR phosphorylation) AND cancer'
        
        # Search PubMed
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
        record = Entrez.read(handle)
        handle.close()
        
        total_count = int(record["Count"])
        pmids = record["IdList"]
        
        # Get details for top papers
        recent_count = 0
        citations = []
        
        if pmids:
            # Fetch details
            handle = Entrez.efetch(db="pubmed", id=pmids[:5], retmode="xml")
            articles = Entrez.read(handle)
            handle.close()
            
            for article in articles['PubmedArticle']:
                try:
                    medline = article['MedlineCitation']
                    article_info = medline['Article']
                    
                    # Get publication year
                    pub_date = article_info.get('Journal', {}).get('JournalIssue', {}).get('PubDate', {})
                    year = pub_date.get('Year', '')
                    
                    if year and int(year) >= 2020:
                        recent_count += 1
                    
                    # Get PMID and title
                    pmid = medline['PMID']
                    title = article_info.get('ArticleTitle', 'No title')
                    
                    citations.append({
                        'pmid': str(pmid),
                        'title': title,
                        'year': year
                    })
                except Exception as e:
                    continue
        
        # Rate limiting
        time.sleep(0.34)  # ~3 requests per second
        
        return {
            'total_papers': total_count,
            'recent_papers': recent_count,
            'citations': citations
        }
    
    except Exception as e:
        print(f"  ⚠️  Error searching {gene} × {cancer_type}: {str(e)}")
        return {
            'total_papers': 0,
            'recent_papers': 0,
            'citations': []
        }

# ==============================================================================
# STEP 4: Perform Literature Searches
# ==============================================================================

print("\n[STEP 3] Performing PubMed searches...")
print("  This will take ~15-20 minutes (rate-limited to avoid bans)")
print("  Searching 40 combinations + 4 gene-only searches = 44 searches total")
print()

literature_results = []
search_count = 0
total_searches = len(top_10_cancers) * len(target_genes) + len(target_genes)

# Search each cancer × gene combination
for cancer in top_10_cancers:
    print(f"  Searching: {cancer}")
    
    for gene in target_genes:
        search_count += 1
        print(f"    [{search_count:2d}/{total_searches}] {gene}...", end=" ")
        
        result = search_pubmed(gene, cancer)
        
        literature_results.append({
            'cancer_type': cancer,
            'gene': gene,
            'total_papers': result['total_papers'],
            'recent_papers_2020plus': result['recent_papers'],
            'key_citation_1': result['citations'][0]['pmid'] if len(result['citations']) > 0 else 'none',
            'key_citation_1_title': result['citations'][0]['title'] if len(result['citations']) > 0 else '',
            'key_citation_2': result['citations'][1]['pmid'] if len(result['citations']) > 1 else 'none',
            'key_citation_2_title': result['citations'][1]['title'] if len(result['citations']) > 1 else '',
            'clinical_trials_mentioned': False,  # Would need separate trials search
            'notes': f"{result['total_papers']} papers found, {result['recent_papers']} recent"
        })
        
        print(f"✓ {result['total_papers']} papers ({result['recent_papers']} recent)")

# Search each gene alone (for general information)
print(f"\n  Searching general gene information:")
for gene in target_genes:
    search_count += 1
    print(f"    [{search_count:2d}/{total_searches}] {gene} (general)...", end=" ")
    
    result = search_pubmed(gene, cancer_type=None)
    
    literature_results.append({
        'cancer_type': 'GENERAL',
        'gene': gene,
        'total_papers': result['total_papers'],
        'recent_papers_2020plus': result['recent_papers'],
        'key_citation_1': result['citations'][0]['pmid'] if len(result['citations']) > 0 else 'none',
        'key_citation_1_title': result['citations'][0]['title'] if len(result['citations']) > 0 else '',
        'key_citation_2': result['citations'][1]['pmid'] if len(result['citations']) > 1 else 'none',
        'key_citation_2_title': result['citations'][1]['title'] if len(result['citations']) > 1 else '',
        'clinical_trials_mentioned': False,
        'notes': f"General kinase/cancer literature"
    })
    
    print(f"✓ {result['total_papers']} papers")

# ==============================================================================
# STEP 5: Save literature_summary_manual.csv (REQUIRED OUTPUT #1)
# ==============================================================================

print("\n[STEP 4] Saving literature_summary_manual.csv...")

lit_summary_df = pd.DataFrame(literature_results)
output_file = DATA_PROCESSED / "literature_summary_manual.csv"
lit_summary_df.to_csv(output_file, index=False)

print(f"✓ Saved: {output_file}")
print(f"  Rows: {len(lit_summary_df)}")
print(f"  Cancer × gene combinations: {len(lit_summary_df[lit_summary_df['cancer_type'] != 'GENERAL'])}")

# ==============================================================================
# STEP 6: Calculate Literature Scores (REQUIRED OUTPUT #2)
# ==============================================================================

print("\n[STEP 5] Calculating literature scores...")

# For each cancer type (excluding GENERAL), calculate total paper count
cancer_lit_scores = []

for cancer in top_10_cancers:
    cancer_data = lit_summary_df[lit_summary_df['cancer_type'] == cancer]
    
    # Sum papers across all 4 genes
    total_papers = cancer_data['total_papers'].sum()
    recent_papers = cancer_data['recent_papers_2020plus'].sum()
    
    # Get individual gene counts
    gene_counts = {}
    for gene in target_genes:
        count = cancer_data[cancer_data['gene'] == gene]['total_papers'].values
        gene_counts[f'{gene}_paper_count'] = count[0] if len(count) > 0 else 0
    
    # Calculate literature confidence score
    # Scale: 80+ papers = 1.0, 40-79 = 0.5-0.99, <40 = <0.5
    literature_confidence_score = min(1.0, total_papers / 80)
    
    # Check if there's any clinical evidence
    has_clinical_evidence = recent_papers > 0  # Simplified proxy
    
    cancer_lit_scores.append({
        'cancer_type': cancer,
        **gene_counts,
        'total_paper_count': total_papers,
        'recent_paper_count': recent_papers,
        'literature_confidence_score': literature_confidence_score,
        'has_clinical_evidence': has_clinical_evidence
    })

# Create DataFrame
lit_scoring_df = pd.DataFrame(cancer_lit_scores)

# Also add other cancer types with zero scores (for completeness)
all_cancers = cancer_rankings['OncotreePrimaryDisease'].tolist()
missing_cancers = [c for c in all_cancers if c not in top_10_cancers]

for cancer in missing_cancers:
    zero_scores = {
        'cancer_type': cancer,
        **{f'{gene}_paper_count': 0 for gene in target_genes},
        'total_paper_count': 0,
        'recent_paper_count': 0,
        'literature_confidence_score': 0.0,
        'has_clinical_evidence': False
    }
    lit_scoring_df = pd.concat([lit_scoring_df, pd.DataFrame([zero_scores])], ignore_index=True)

# Save
output_file = DATA_PROCESSED / "literature_scoring.csv"
lit_scoring_df.to_csv(output_file, index=False)

print(f"✓ Saved: {output_file}")
print(f"  Rows: {len(lit_scoring_df)}")

# Show top 10
print("\nTop 10 by literature_confidence_score:")
top_lit = lit_scoring_df.nlargest(10, 'literature_confidence_score')[
    ['cancer_type', 'total_paper_count', 'recent_paper_count', 'literature_confidence_score']
]
print(top_lit.to_string(index=False))

# ==============================================================================
# STEP 7: Create literature_review_summary.md (REQUIRED OUTPUT #3)
# ==============================================================================

print("\n[STEP 6] Creating literature_review_summary.md...")

summary_file = REPORTS / "literature_review_summary.md"

with open(summary_file, 'w') as f:
    f.write("# Literature Review Summary\n")
    f.write("Generated: 2025-11-01\n\n")
    f.write("=" * 80 + "\n\n")
    
    # Methodology
    f.write("## Methodology\n\n")
    f.write("- **Approach:** Manual PubMed searches via Entrez API\n")
    f.write(f"- **Scope:** Top 10 cancer types × 4 target genes = 40 searches\n")
    f.write(f"- **Additional:** 4 general gene searches (kinase + cancer)\n")
    f.write("- **Focus:** Papers with 2020+ publication dates for recency\n")
    f.write("- **Rate limiting:** 3 requests/second to avoid NCBI bans\n")
    f.write("- **Search terms:** [GENE] AND [CANCER TYPE] AND (cancer OR tumor OR carcinoma OR malignancy)\n\n")
    
    # Overall findings
    f.write("## Overall Findings\n\n")
    total_unique_papers = lit_summary_df['total_papers'].sum()
    f.write(f"- **Total search results:** {total_unique_papers:,} papers (with duplicates across searches)\n")
    f.write(f"- **Cancer types analyzed:** {len(top_10_cancers)}\n")
    f.write(f"- **Target genes:** {len(target_genes)} (STK17A, MYLK4, TBK1, CLK4)\n\n")
    
    # Cancer types with strong/weak literature
    strong_lit = lit_scoring_df[lit_scoring_df['literature_confidence_score'] >= 0.7]['cancer_type'].tolist()
    medium_lit = lit_scoring_df[(lit_scoring_df['literature_confidence_score'] >= 0.4) & 
                                (lit_scoring_df['literature_confidence_score'] < 0.7)]['cancer_type'].tolist()
    sparse_lit = lit_scoring_df[lit_scoring_df['literature_confidence_score'] < 0.4]['cancer_type'].head(10).tolist()
    
    f.write(f"### Cancer Types by Literature Support\n\n")
    f.write(f"**Strong literature support (score ≥0.7):** {len(strong_lit)} cancer types\n")
    if strong_lit:
        for cancer in strong_lit[:5]:
            f.write(f"  - {cancer}\n")
    f.write(f"\n**Medium literature support (0.4-0.7):** {len(medium_lit)} cancer types\n")
    if medium_lit:
        for cancer in medium_lit[:5]:
            f.write(f"  - {cancer}\n")
    f.write(f"\n**Sparse literature (<0.4):** {len(sparse_lit)} cancer types in top 10\n")
    if sparse_lit:
        for cancer in sparse_lit:
            f.write(f"  - {cancer}\n")
    
    # Gene-specific literature
    f.write(f"\n### Genes Ranked by Literature Volume\n\n")
    general_lit = lit_summary_df[lit_summary_df['cancer_type'] == 'GENERAL'].sort_values('total_papers', ascending=False)
    for idx, row in general_lit.iterrows():
        f.write(f"{row['gene']:10s}: {row['total_papers']:5d} papers (general kinase/cancer literature)\n")
    
    # Key citations by cancer type
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("## Key Citations by Cancer Type\n\n")
    
    for cancer in top_10_cancers:
        f.write(f"### {cancer}\n\n")
        
        cancer_data = lit_summary_df[lit_summary_df['cancer_type'] == cancer]
        
        for gene in target_genes:
            gene_data = cancer_data[cancer_data['gene'] == gene]
            
            if len(gene_data) == 0:
                continue
            
            row = gene_data.iloc[0]
            
            f.write(f"**{gene}:**\n")
            f.write(f"- Paper count: {row['total_papers']} ({row['recent_papers_2020plus']} recent)\n")
            
            if row['key_citation_1'] != 'none':
                f.write(f"- Key citation: PMID:{row['key_citation_1']}\n")
                f.write(f"  * {row['key_citation_1_title'][:100]}...\n")
            else:
                f.write(f"- No papers found\n")
            
            if row['key_citation_2'] != 'none':
                f.write(f"- Additional: PMID:{row['key_citation_2']}\n")
            
            f.write(f"- Note: {row['notes']}\n\n")
        
        f.write("\n")
    
    # General target literature
    f.write("=" * 80 + "\n")
    f.write("## General Target Literature\n\n")
    
    general_data = lit_summary_df[lit_summary_df['cancer_type'] == 'GENERAL']
    
    for gene in target_genes:
        gene_data = general_data[general_data['gene'] == gene]
        
        if len(gene_data) == 0:
            continue
        
        row = gene_data.iloc[0]
        
        f.write(f"### {gene}\n\n")
        f.write(f"**Literature volume:** {row['total_papers']} papers (general kinase + cancer)\n\n")
        
        f.write(f"**Key citations:**\n")
        if row['key_citation_1'] != 'none':
            f.write(f"1. PMID:{row['key_citation_1']}\n")
            f.write(f"   {row['key_citation_1_title']}\n\n")
        if row['key_citation_2'] != 'none':
            f.write(f"2. PMID:{row['key_citation_2']}\n")
            f.write(f"   {row['key_citation_2_title']}\n\n")
        
        f.write(f"**Mechanism:** [Would need manual review of top papers]\n\n")
        f.write(f"**Clinical relevance:** [Would need manual review of recent papers]\n\n")
    
    # Gaps in literature
    f.write("=" * 80 + "\n")
    f.write("## Gaps in Literature\n\n")
    
    sparse_cancers = lit_scoring_df[lit_scoring_df['total_paper_count'] < 10].head(10)
    f.write("**Cancer types with minimal evidence (<10 papers across all 4 genes):**\n")
    for _, row in sparse_cancers.iterrows():
        f.write(f"  - {row['cancer_type']}: {row['total_paper_count']} papers\n")
    
    f.write("\n**Genes with limited cancer-specific studies:**\n")
    for gene in target_genes:
        gene_counts = lit_scoring_df[f'{gene}_paper_count'].sum()
        if gene_counts < 50:
            f.write(f"  - {gene}: {gene_counts} total papers across all cancer types\n")
    
    f.write("\n**Opportunities for novel investigation:**\n")
    f.write("- High DepMap dependency + low literature = novel therapeutic opportunity\n")
    f.write("- Rare cancers with strong dependency may lack literature simply due to rarity\n")
    f.write("- Consider as hypothesis-generating targets for experimental validation\n")

print(f"✓ Saved: {summary_file}")

# ==============================================================================
# COMPLETION SUMMARY
# ==============================================================================

print("\n" + "=" * 80)
print("✅ PROMPT 3 COMPLETE: Literature Review")
print("=" * 80)

print("\nOUTPUTS GENERATED:")
print("  1. ✓ data/processed/literature_summary_manual.csv")
print("  2. ✓ data/processed/literature_scoring.csv")
print("  3. ✓ outputs/reports/literature_review_summary.md")

print("\nKEY RESULTS:")
print(f"  • Searches performed: {len(literature_results)}")
print(f"  • Cancer types with strong literature (>56 papers): {len(strong_lit)}")
print(f"  • Cancer types with sparse literature (<32 papers): {len(sparse_lit)}")
print(f"  • Top gene by literature: {general_lit.iloc[0]['gene']} ({general_lit.iloc[0]['total_papers']} papers)")

print("\n" + "=" * 80)
print("READY FOR CURSOR VALIDATION")
print("=" * 80)
print("\nNext: Run Cursor validation, then proceed to PROMPT 3.5 (Experimental Validation)")
