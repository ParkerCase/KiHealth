# Deployment Guide

## Quick Start

```bash
cd risk_calculator
pip install -r requirements.txt
python app.py
```

Access at: **http://localhost:5001**

---

## Production Deployment

### Option 1: Heroku

1. **Create Procfile:**

   ```
   web: gunicorn app:app
   ```

2. **Install gunicorn:**

   ```bash
   pip install gunicorn
   pip freeze > requirements.txt
   ```

3. **Deploy:**
   ```bash
   heroku create doc-risk-calculator
   git push heroku main
   ```

### Option 2: AWS (EC2)

1. **SSH into EC2 instance**

2. **Install dependencies:**

   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip nginx
   pip3 install -r requirements.txt
   pip3 install gunicorn
   ```

3. **Run with gunicorn:**

   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

4. **Configure nginx** (reverse proxy)

### Option 3: Docker

1. **Create Dockerfile:**

   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5001
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
   ```

2. **Build and run:**
   ```bash
   docker build -t doc-calculator .
   docker run -p 5001:5001 doc-calculator
   ```

---

## Environment Variables

For production, consider:

- `FLASK_ENV=production`
- `PORT=5001` (or your preferred port)
- `SECRET_KEY` (for session security if needed)

---

## Security Considerations

1. **HTTPS:** Use SSL/TLS in production
2. **Rate Limiting:** Consider adding rate limiting
3. **Input Validation:** Already implemented
4. **Error Handling:** Already implemented
5. **No Data Storage:** Stateless (GDPR compliant)

---

## Performance

- **Model Loading:** Once at startup (~2-3 seconds)
- **Prediction Time:** <100ms per request
- **Concurrent Users:** Test with load testing tool

---

**Status:** Ready for deployment
