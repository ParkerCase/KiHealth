# DOC - Digital Osteoarthritis Counseling

Machine learning model for predicting 4-year knee replacement risk in patients with osteoarthritis.

## Project Overview

The DOC (Digital Osteoarthritis Counseling) model is a Random Forest-based prediction tool developed using the Osteoarthritis Initiative (OAI) dataset. The model predicts the risk of total knee replacement within 4 years based on baseline patient characteristics.

## Key Features

- **Model Performance:** AUC = 0.862, Brier Score = 0.0307 (after Platt scaling)
- **PROBAST Compliance:** LOW RISK OF BIAS across all 4 domains
- **Calibration:** Improved with Platt scaling (66.5% Brier score reduction)
- **Web Applications:**
  - Risk Calculator (Flask) - Single patient predictions
  - Validator (Vercel) - Batch CSV processing

## Repository Structure

```
DOC/
├── DOC_Validator_Vercel/     # Vercel deployment (validator.stroomai.com)
├── risk_calculator/          # Flask web app for single predictions
├── notebooks/                # Jupyter notebooks for analysis
├── models/                   # Trained models (gitignored - too large)
├── data/                     # Data files (gitignored)
└── scripts/                  # Utility scripts
```

## Quick Start

### Risk Calculator (Local)

```bash
cd risk_calculator
pip install -r requirements.txt
python app.py
```

Access at: `http://localhost:5001`

### Validator (Vercel)

```bash
cd DOC_Validator_Vercel
vercel dev  # Test locally
vercel deploy --prod  # Deploy to production
```

## Model Information

- **Algorithm:** Random Forest (calibrated with Platt scaling)
- **Dataset:** OAI (N=4,796 patients)
- **Outcome:** Total knee replacement within 48 months
- **Events:** 171 (3.57%)
- **Predictors:** 10 baseline variables
- **EPV Ratio:** 17.10 (adequate)

## Development

Developed by **StroomAI** in collaboration with **Dr. Maarten Moen** (NOC*NSF / Bergman Clinics).

## License

For research and clinical use only.

## Contact

parker@stroomai.com

