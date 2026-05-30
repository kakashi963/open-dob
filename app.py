from flask import Flask, request, jsonify
import requests
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# Disable SSL warnings - the Kerala govt site (result.kite.kerala.gov.in) has certificate chain issues
# that cause verification to fail in many environments (including Render).
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# --- PRE-GENERATED DATA ---
# Generate dates once at startup to save CPU time per request
START_DATE = datetime(2009, 1, 1)
END_DATE = datetime(2011, 12, 31)
DATES = []
curr = START_DATE
while curr <= END_DATE:
    DATES.append(curr.strftime("%Y%m%d"))
    curr += timedelta(days=1)

# --- CORE LOGIC ---

def strike_worker(regno, date_str):
    """Worker that handles both the check and the data retrieval in one thread."""
    first_digit = regno[0]
    url = f"https://results.kite.kerala.gov.in/K1TE@SPO@2025@9995994069/K1TE@SPO@20254069_{first_digit}/{date_str}{regno}.json"
    try:
        response = requests.get(url, timeout=3.0, verify=False)
        if response.status_code == 200:
            try:
                data = response.json()
                data['dob'] = f"{date_str[6:]}/{date_str[4:6]}/{date_str[:4]}"
                return data
            except:
                pass
    except:
        pass
    return None

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "open-dob"})

@app.route('/get_schools', methods=['GET'])
def get_schools():
    try:
        with open('schools.json', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return jsonify([])

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    scode = data.get('scode')
    url = "https://result.kite.kerala.gov.in/analysis//Analysis/getAjaxSubmitSchoolwiseResult"
    payload = {"scode": scode}

    # Retry logic because the Kerala site is often slow/unreliable
    max_retries = 3
    base_timeout = 30

    for attempt in range(1, max_retries + 1):
        try:
            timeout = base_timeout + (attempt * 10)  # 30s, 40s, 50s
            response = requests.post(url, data=payload, timeout=timeout, verify=False)
            rows = re.findall(r"<tr[^>]*>(.*?)</tr>", response.text, re.DOTALL)
            students = []
            for row in rows:
                cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
                clean_cells = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip() for c in cells]
                for i, val in enumerate(clean_cells):
                    if re.match(r"^\d{6,7}$", val) and i + 1 < len(clean_cells):
                        name = clean_cells[i+1]
                        if name and not name.isdigit() and len(name) > 2:
                            students.append({"regno": val, "name": name})
                            break
            return jsonify({"success": True, "students": students})

        except requests.exceptions.Timeout:
            if attempt == max_retries:
                return jsonify({
                    "success": False, 
                    "error": "The government server is taking too long to respond. Please try again in a minute."
                })
            # Small delay before retry
            import time
            time.sleep(1.5 * attempt)

        except Exception as e:
            if attempt == max_retries:
                return jsonify({"success": False, "error": "Archive temporarily unavailable. Please try again."})
            import time
            time.sleep(1 * attempt)

    return jsonify({"success": False, "error": "Unexpected error. Please try again."})

@app.route('/strike', methods=['POST'])
def strike():
    """Strike route using a fresh executor per request to prevent pool clogging."""
    data = request.json
    regno = data.get('regno')
    
    found_data = None
    # 150 workers - for local testing only (Render may struggle with this)
    with ThreadPoolExecutor(max_workers=150) as executor:
        futures = {executor.submit(strike_worker, regno, d): d for d in DATES}
        
        for future in as_completed(futures):
            res = future.result()
            if res:
                found_data = res
                # Terminate remaining futures for this specific request
                executor.shutdown(wait=False, cancel_futures=True)
                break
                
    if found_data:
        return jsonify({"success": True, "data": found_data})
    return jsonify({"success": False, "message": "DOB not found"})

if __name__ == '__main__':
    # For local development only. Production uses gunicorn via Procfile/render.yaml
    port = 5000
    print(f"[*] OPEN DOB starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
