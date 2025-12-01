# DOC Risk Calculator - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd risk_calculator
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python app.py
```

Or use the startup script:

```bash
./start.sh
```

### 3. Open in Browser

Navigate to: **http://localhost:5001**

(Note: Port 5000 is often used by macOS AirPlay Receiver, so we use 5001 instead)

### 4. Test the Calculator

Try these sample inputs:

**High Risk Example:**

- Age: 70
- Sex: Female
- BMI: 32
- Right WOMAC: 60
- Left WOMAC: 65
- Right KL Grade: 4
- Left KL Grade: 4
- Family History: Yes

**Expected:** ~75% risk (Very High)

**Low Risk Example:**

- Age: 50
- Sex: Male
- BMI: 24
- Right WOMAC: 5
- Left WOMAC: 8
- Right KL Grade: 1
- Left KL Grade: 1
- Family History: No

**Expected:** ~0.1% risk (Low)

---

## 📋 Requirements

- Python 3.8+
- Flask
- Model files in `../models/`:
  - `random_forest_best.pkl`
  - `scaler.pkl`
  - `feature_names.pkl`

---

## 🐛 Troubleshooting

### Model Not Loading

- Check that model files exist in `../models/`
- Verify file paths in `app.py`

### Port Already in Use

- Change port in `app.py`: `app.run(port=5001)`

### Import Errors

- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

---

## 📱 Testing on Mobile

1. Find your computer's IP address:

   - Mac/Linux: `ifconfig | grep inet`
   - Windows: `ipconfig`

2. Start server with: `app.run(host='0.0.0.0', port=5000)`

3. On mobile device, navigate to: `http://YOUR_IP:5000`

---

## ✅ Success!

If you see the calculator form and can calculate risks, you're all set!

**Next Steps:**

- Test with real patient data (anonymized)
- Review with clinical team
- Plan deployment strategy

---

**Status:** ✅ Ready for testing
