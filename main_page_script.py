from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to main page...")
        page.goto("https://resultadoelectoral.onpe.gob.pe/", wait_until="networkidle")
        time.sleep(5)
        
        # intercept and print all API calls from the main page
        print("Taking screenshot...")
        page.screenshot(path="main_page.png")
        print("Title:", page.title())
        with open("main_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        print("Links on page:")
        for a in page.query_selector_all('a'):
            href = a.get_attribute('href')
            text = a.inner_text().strip()
            if href:
                print(f"{text}: {href}")
                
        browser.close()

if __name__ == "__main__":
    run()
