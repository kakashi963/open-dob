import requests
import json

try:
    r = requests.post('http://localhost:5000/search', json={'scode': '42084'}, timeout=10)
    data = r.json()
    print(f"Total students found: {len(data['students'])}")
    kasinath = [s for s in data['students'] if "KASINATH" in s['name'].upper()]
    if kasinath:
        print(f"Success! Found Kasinath: {kasinath}")
    else:
        print("Kasinath NOT found in the parsed list.")
        # Print a few sample names
        print("Sample names:", [s['name'] for s in data['students'][:5]])
except Exception as e:
    print(f"Error: {e}")
