import asyncio
from playwright.async_api import async_playwright

async def run_mobile_test():
    async with async_playwright() as p:
        # Using iPhone 13 Pro Max for a large mobile viewport
        iphone = p.devices['iPhone 13 Pro Max']
        browser = await p.chromium.launch(headless=True)
        # Create a context with the device emulation
        context = await browser.new_context(**iphone)
        page = await context.new_page()
        
        print("[*] Navigating to http://localhost:5000 in Mobile Mode...")
        await page.goto("http://localhost:5000")
        
        # Take a screenshot to see how it looks on mobile
        await page.screenshot(path="mobile_view.png")
        print("[*] Screenshot saved as mobile_view.png")
        
        # Test 1: Check if header is visible
        title = await page.inner_text("header h1")
        print(f"[*] Header found: {title}")
        
        # Test 2: Search for a school (using 'A E M' from our earlier peek at schools.json)
        print("[*] Testing school search...")
        await page.fill("#schoolNameInput", "A E M")
        await page.wait_for_selector(".autocomplete-item")
        
        # Click the first result
        print("[*] School selected from autocomplete.")
        try:
            await page.click(".autocomplete-item:first-child", timeout=5000)
        except:
            print("[!] Click intercepted, attempting forced click...")
            await page.click(".autocomplete-item:first-child", force=True)
        
        # Test 3: Retrieve Registry
        print("[*] Querying registry...")
        await page.click("#searchBtn")
        
        # Wait for results to load
        await page.wait_for_selector(".student-card")
        results_count = await page.inner_text("#resultsCount")
        print(f"[*] Search results: {results_count}")
        
        # Take a final screenshot of the results list
        await page.screenshot(path="mobile_results.png")
        print("[*] Final results screenshot saved as mobile_results.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_mobile_test())
