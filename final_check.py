import requests
import json

try:
    r = requests.post('http://localhost:5000/search', json={'scode': '42084'}, timeout=15)
    data = r.json()
    print(f"Total students found: {len(data['students'])}")
    kasinath = [s for s in data['students'] if "KASINATH" in s['name'].upper()]
    if kasinath:
        print(f"SUCCESS: Found Kasinath! -> {kasinath}")
    else:
        print("Kasinath still missing. Sample names:")
        print([s['name'] for s in data['students'][:10]])
except Exception as e:
    print(f"Error: {e}")
