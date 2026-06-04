from playwright.sync_api import sync_playwright

url = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/ubigeos/locales?idUbigeo=140143"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(5000)
        page.screenshot(path="screenshot.png")
        print("Page title:", page.title())
        with open("content.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        browser.close()

if __name__ == "__main__":
    run()
