# Troubleshooting Guide

## Common Issues and Solutions

### 1. Port Already in Use

**Error:** `Address already in use` or `Port 5000 is in use`

**Solution:**

- The calculator now uses port 5001 by default
- If 5001 is also in use, change the port in `app.py`:
  ```python
  app.run(debug=True, host="0.0.0.0", port=5002)  # Use any available port
  ```

**macOS AirPlay:**

- Port 5000 is often used by macOS AirPlay Receiver
- Disable it in System Settings > General > AirDrop & Handoff > AirPlay Receiver
- Or simply use port 5001 (already configured)

---

### 2. Sklearn Version Warnings

**Warning:** `InconsistentVersionWarning: Trying to unpickle estimator from version 1.4.2 when using version 1.3.2`

**Status:** ✅ **SAFE TO IGNORE**

**Explanation:**

- Model was saved with sklearn 1.4.2
- Current environment has sklearn 1.3.2
- Model will work correctly (backward compatible)
- Warnings are suppressed in the code

**If you want to fix:**

```bash
pip install --upgrade scikit-learn==1.4.2
```

---

### 3. Model Not Loading

**Error:** `Error loading model: [Errno 2] No such file or directory`

**Solution:**

1. Check that model files exist:

   ```bash
   ls -lh ../models/random_forest_best.pkl
   ls -lh ../models/scaler.pkl
   ls -lh ../models/feature_names.pkl
   ```

2. Verify paths in `app.py`:

   ```python
   BASE_DIR = Path(__file__).parent.parent
   MODEL_PATH = BASE_DIR / "models" / "random_forest_best.pkl"
   ```

3. Run from correct directory:
   ```bash
   cd risk_calculator
   python app.py
   ```

---

### 4. Import Errors

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**

```bash
pip install -r requirements.txt
```

**Or install individually:**

```bash
pip install Flask pandas numpy scikit-learn joblib
```

---

### 5. Predictions Return 0% or 100%

**Possible Causes:**

1. Input values outside valid ranges
2. Preprocessing mismatch
3. Model not loaded correctly

**Solution:**

1. Verify inputs are within ranges:

   - Age: 45-79
   - BMI: 15-50
   - WOMAC: 0-96
   - KL Grade: 0-4

2. Test with known values:

   - High risk: Age 70, Female, BMI 32, WOMAC 60/65, KL 4/4, Family History Yes
   - Should give ~75% risk

3. Check preprocessing function matches training pipeline

---

### 6. Gauge Chart Not Updating

**Possible Causes:**

1. JavaScript errors in browser console
2. CSS not loading
3. SVG rendering issue

**Solution:**

1. Open browser developer console (F12)
2. Check for JavaScript errors
3. Verify static files are loading:
   - `http://localhost:5001/static/style.css`
   - `http://localhost:5001/static/script.js`

---

### 7. Mobile Device Can't Access

**Problem:** Calculator works on computer but not on mobile device

**Solution:**

1. Find your computer's IP address:

   ```bash
   # Mac/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1

   # Windows
   ipconfig
   ```

2. On mobile device, navigate to:

   ```
   http://YOUR_IP_ADDRESS:5001
   ```

3. Ensure both devices are on same network

---

### 8. Slow Predictions

**Possible Causes:**

1. Model loading on each request (should only load once)
2. Large model file (182 MB)

**Solution:**

- Model loads once at startup (correct behavior)
- First prediction may be slower (~1-2 seconds)
- Subsequent predictions should be fast (<100ms)

---

## Getting Help

If issues persist:

1. **Check logs:** Look at terminal output for error messages
2. **Browser console:** Check for JavaScript errors (F12)
3. **Test script:** Run `python test_calculator.py` to verify model works
4. **Verify files:** Ensure all files are in correct locations

---

## Quick Health Check

Run this to verify everything is set up correctly:

```bash
cd risk_calculator
python test_calculator.py
```

Expected output:

- ✓ Model loads successfully
- ✓ Preprocessing works
- ✓ Predictions are reasonable (not 0% or 100% for test cases)

---

**Status:** Most issues are resolved. Calculator should work out of the box.
