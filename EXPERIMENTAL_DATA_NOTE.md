# Experimental Data Received - Nov 1, 2025

## Update to Project Plan

On November 1, 2025, received experimental validation data from STARX team:

### New Data Received:
1. **IC50 Data (160 cell lines)** - Victoria & Tulasi
   - UMF-815K (Cpd1) IC50 values
   - UMF-815H (Cpd2) IC50 values
   - Location: `data/raw/StarXData/Copy of AQT cell based profiling160 cell lines815K815H_report_summary/IC50 values-Table 1.csv`

2. **RNAseq DEGs** - Hafsa
   - 6 differential expression files (K562, K666N)
   - Location: `data/raw/StarXData/DEGs/`

3. **Phosphoproteomics** - Erica
   - GBM43 treatment data
   - Location: `data/raw/StarXData/GBM43 Phosphoproteomics/`

4. **IP-MS** - Erica
   - Protein-protein interaction data
   - Location: `data/raw/StarXData/GBM43 IP-MS/`

### Impact on Analysis:
- Added **PROMPT 3.5** (Experimental Validation Integration)
- Updated **PROMPT 4** scoring to include 6th dimension (experimental validation)
- New weight distribution in final_integrated_rankings.csv
- Timeline extended by 6 hours (still achievable for Nov 10 delivery)

### Still Awaiting (Not Critical):
- Christian: 814H RNAseq + new proteomics
- Eduardo: Docking/structure files

---

## Copy Number Analysis Update (Nov 1, 2025)

### Finding:
Analysis revealed uniformly high amplification rates (99%+) across all target genes in most cancer types.

### Scientific Interpretation:
Target genes (STK17A, MYLK4, TBK1, CLK4) reside in genomically stable regions not subject to frequent focal amplifications or deletions. This is **positive for targetability** (genes are rarely deleted) but provides **limited discriminatory power** for patient stratification.

### Scoring Impact:
Copy number weight reduced from 10% to 5% in final integrated scoring. Extra 5% allocated to expression correlation (which shows strong variation). See `SCORING_WEIGHTS_UPDATE.md` for details.

### Final Evidence Weights:
- DepMap dependency: 30%
- Expression correlation: 25%
- Mutation context: 20%
- Experimental validation: 10%
- Literature support: 10%
- Copy number: 5%

---

**Status:** Analysis plan updated, proceeding on schedule.
**Next Step:** PROMPT 3 (Literature Review)
