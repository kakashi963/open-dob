import requests
import re
import json
import urllib3
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_districts(district_ids):
    """Scrapes all schools for a list of districts and merges them."""
    # Types: 1=Govt, 3=Aided, 4=UnAided
    types = [1, 3, 4]
    
    # Load existing schools if file exists
    all_schools = []
    if os.path.exists('schools.json'):
        try:
            with open('schools.json', 'r', encoding='utf-8') as f:
                all_schools = json.load(f)
            print(f"[*] Loaded {len(all_schools)} existing schools from schools.json")
        except:
            print("[!] Error loading existing schools.json, starting fresh.")
    
    for dist_id in district_ids:
        print(f"[*] Starting complete scrape for District {dist_id}...")
        for t in types:
            url = f"https://sametham.kite.kerala.gov.in/publicView/schoolsLists/HS/dist/{dist_id}/{t}"
            try:
                print(f"[*] Fetching type {t} from {url}")
                response = requests.get(url, verify=False, timeout=30)
                html = response.text
                
                # Regex to match: <a href=".../([0-9]{5,})">([0-9]{5,}) - ([^<]+)</a>
                matches = re.findall(r"href=\"https://sametham.kite.kerala.gov.in/(\d+)\">(\d+) - ([^<]+)</a>", html)
                
                for code, _, name in matches:
                    clean_name = name.replace("&nbsp;", " ").strip()
                    all_schools.append({"name": clean_name, "code": code})
                    
                print(f"[*] Found {len(matches)} schools of type {t}.")
            except Exception as e:
                print(f"[!] Error scraping type {t} for district {dist_id}: {e}")
            
    # Deduplicate based on school code
    unique_schools = {s['code']: s for s in all_schools}.values()
    final_list = sorted(list(unique_schools), key=lambda x: x['name'])
    
    print(f"[*] Final total unique schools in database: {len(final_list)}")
    
    with open('schools.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=4)
    print("[*] Successfully updated schools.json")

if __name__ == "__main__":
    # 1: TVM, 2: KLM
    scrape_districts([2])
