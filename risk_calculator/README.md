# DOC Risk Calculator

Web-based risk calculator for predicting 4-year knee replacement risk using the DOC (Digital Osteoarthritis Counseling) machine learning model.

## Features

- **User-friendly interface** with input validation
- **Real-time risk calculation** using Random Forest model (AUC: 0.862)
- **Visual risk display** with gauge chart
- **Risk categorization** (Low, Moderate, High, Very High)
- **Clinical interpretation** for each risk category
- **Mobile-responsive design**
- **Printable results**

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure model files are in the correct location:
   - `models/random_forest_best.pkl`
   - `models/scaler.pkl`
   - `models/feature_names.pkl`

## Running the Calculator

### Local Development

```bash
cd risk_calculator
python app.py
```

The calculator will be available at: `http://localhost:5001`

(Note: Port 5000 is often used by macOS AirPlay Receiver, so we use 5001 instead)

### Production Deployment

For deployment to Heroku, AWS, or other platforms:

1. **Heroku:**

   - Create `Procfile`: `web: gunicorn app:app`
   - Install gunicorn: `pip install gunicorn`
   - Deploy: `git push heroku main`

2. **AWS (EC2/Elastic Beanstalk):**
   - Use gunicorn or uWSGI as WSGI server
   - Configure nginx as reverse proxy

## Input Fields

- **Age:** 45-79 years
- **Sex:** Male or Female
- **BMI:** 15-50 kg/m²
- **Right Knee WOMAC Score:** 0-96
- **Left Knee WOMAC Score:** 0-96
- **Right Knee KL Grade:** 0-4
- **Left Knee KL Grade:** 0-4
- **Family History:** Yes or No

## Output

- **Risk Percentage:** Predicted probability of knee replacement within 4 years
- **Risk Category:**
  - Low: <5%
  - Moderate: 5-15%
  - High: 15-30%
  - Very High: >30%
- **Clinical Interpretation:** Guidance for clinicians

## Model Information

- **Algorithm:** Random Forest
- **Discrimination:** AUC = 0.862
- **Development Dataset:** OAI (N=4,796)
- **PROBAST Assessment:** LOW RISK OF BIAS

## Disclaimer

This calculator is for research and educational purposes only. Model predictions should not be used as the sole basis for clinical decision-making. Always use clinical judgment in conjunction with model predictions.

## License

For research and clinical use only.
