# KiHealth Diabetes Risk Calculator

A Streamlit-based web application for assessing diabetes risk using KiHealth's proprietary Beta Score technology combined with transfer learning from large external datasets.

## Features

- **M2 Transfer Learning Model**: AUC 0.875, validated on 129 patients
- **Foundation Model**: Trained on 17,427 NHANES+CHNS patients
- **Three Clinical Modes**:
  - Screening (>24%): 100% Sensitivity, 60% Specificity
  - Balanced (>56%): 76% Sensitivity, 82% Specificity
  - Confirmation (>64%): 59% Sensitivity, 87% Specificity

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run risk_calculator.py
```

### Streamlit Cloud Deployment

1. Fork or clone this repository
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set main file path: `kihealth_ui/risk_calculator.py`
6. Deploy

## Input Parameters

### Primary Biomarker
- **% Unmethylated (Beta Score)**: KiHealth's proprietary methylation biomarker
  - 0-6%: Good - beta cells healthy
  - 6-10%: Borderline - monitor closely
  - 10-15%: Elevated - beta cell damage detected
  - 15-20%: High - significant beta cell death
  - 20%+: Very High - severe beta cell destruction

### Secondary Markers
- **HbA1c (%)**: Glycated hemoglobin
- **Fasting Insulin (uU/mL)**: Optional, improves HOMA-IR calculation
- **Fasting Glucose (mg/dL)**: Optional

## Model Architecture

```
Stage 1: Foundation Model
├── Input: HbA1c, HOMA-IR
├── Training: 17,427 NHANES+CHNS patients
└── Output: Traditional risk probability

Stage 2: Final Model
├── Input: Beta Score + Foundation Prediction
├── Training: 129 KiHealth patients
└── Output: Final risk probability (0-100%)
```

## Test Cases

| Patient Type | Beta Score | HbA1c | Expected Risk |
|--------------|------------|-------|---------------|
| Normal | 5% unmeth | 5.2% | ~32% |
| Prediabetic | 12% unmeth | 6.0% | ~56% |
| T1D | 26% unmeth | 10.2% | ~91% |

## Files

- `risk_calculator.py`: Main Streamlit application
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: Streamlit configuration

## Model Files (Required)

Located in `../Diabetes-KiHealth/TL-KiHealth/M2_Models/`:
- `foundation_combined.joblib`: Foundation model
- `foundation_scaler.joblib`: Foundation feature scaler
- `beta_foundation_model.joblib`: Final transfer learning model
- `beta_foundation_scaler.joblib`: Final model scaler

## License

Proprietary - KiHealth Inc.
