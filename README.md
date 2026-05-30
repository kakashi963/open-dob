# OPEN DOB

Kerala school student DOB lookup tool (State Registry Archive).

## Local Development

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# or
source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

## Deploy to Render

### Recommended: Deploy via GitHub + Render Dashboard (Easiest)

1. **Push this repo to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Open DOB"
   git remote add origin https://github.com/YOUR_USERNAME/open-dob.git
   git branch -M main
   git push -u origin main
   ```

2. Go to [https://dashboard.render.com/web/new](https://dashboard.render.com/web/new)

3. Connect your GitHub repo

4. Use these settings:
   - **Name**: `open-dob`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 app:app`
   - **Plan**: Free (or paid if you need more resources)

5. Add these environment variables (optional but recommended):
   - `PYTHON_VERSION` = `3.11.9`

6. Click **Create Web Service**

Your app will be live at `https://open-dob.onrender.com`

### Alternative: Using render.yaml (Blueprint)

If you push the `render.yaml` in this repo, Render can deploy the entire service automatically from the dashboard using "Blueprint".

### Important Notes

- The `/strike` endpoint performs very aggressive parallel requests (150 workers) against Kerala's KITE results portal.
  - This can easily get the server IP blocked and uses significant CPU/memory per request.
  - Heavy usage will likely result in rate limiting or blocks from the source site.
- Free tier on Render spins down after 15 minutes of inactivity. First request after idle can take 30-60s.
- The app serves a large `schools.json` (~270KB) on every page load.

## Files

- `app.py` — Flask backend (search + DOB strike)
- `index.html` — Frontend (paper/ledger aesthetic)
- `schools.json` — School registry data
- `requirements.txt` — Python dependencies
- `Procfile` — For gunicorn on Render
- `render.yaml` — Blueprint configuration

## Tech

- Python 3.11 + Flask
- Gunicorn (production)
- Vanilla JS frontend (no build step)

---

**Disclaimer**: This tool scrapes public exam result pages. Use responsibly and respect the source website's terms of service and rate limits.