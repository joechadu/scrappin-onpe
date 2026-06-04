import json
from playwright.sync_api import sync_playwright

url = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/ubigeos/locales?idUbigeo=140143"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(response):
            if "woff" not in response.url and "js" not in response.url and "css" not in response.url and "google" not in response.url:
                print(f"URL: {response.url} | Status: {response.status} | Content-Type: {response.headers.get('content-type', '')}")

        page.on("response", handle_response)
        
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        browser.close()

if __name__ == "__main__":
    run()
