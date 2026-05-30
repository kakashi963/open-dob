import requests
import re
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_schools(district_id=1):
    """Scrapes all schools for a given district from Sametham."""
    # Types: 1=Govt, 3=Aided, 4=UnAided
    types = [1, 3, 4]
    all_schools = []
    
    print(f"[*] Starting complete scrape for District {district_id}...")
    
    for t in types:
        url = f"https://sametham.kite.kerala.gov.in/publicView/schoolsLists/HS/dist/{district_id}/{t}"
        try:
            print(f"[*] Fetching type {t} from {url}")
            response = requests.get(url, verify=False, timeout=30)
            html = response.text
            
            # Regex to match: <a href=".../([0-9]{5,})">([0-9]{5,}) - ([^<]+)</a>
            # Matches the school code and name from the table
            matches = re.findall(r"href=\"https://sametham.kite.kerala.gov.in/(\d+)\">(\d+) - ([^<]+)</a>", html)
            
            for code, _, name in matches:
                # Clean up name
                clean_name = name.replace("&nbsp;", " ").strip()
                all_schools.append({"name": clean_name, "code": code})
                
            print(f"[*] Found {len(matches)} schools of type {t}.")
        except Exception as e:
            print(f"[!] Error scraping type {t}: {e}")
            
    # Remove duplicates based on code
    unique_schools = {s['code']: s for s in all_schools}.values()
    final_list = sorted(list(unique_schools), key=lambda x: x['name'])
    
    print(f"[*] Total unique schools found for District {district_id}: {len(final_list)}")
    
    with open('schools.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=4)
    print("[*] Successfully updated schools.json")

if __name__ == "__main__":
    scrape_schools(1) # 1 is Thiruvananthapuram
