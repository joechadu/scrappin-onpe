import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json
import pandas as pd

def test_selenium_json():
    print("Iniciando Selenium con undetected_chromedriver...")
    options = uc.ChromeOptions()
    # No usamos headless para evitar deteccion inicial
    driver = uc.Chrome(options=options, version_main=148)
    ubigeo = "140143"
    pagina = 0
    tamanio = 15
    
    url = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina={pagina}&tamanio={tamanio}&idAmbitoGeografico=1&idUbigeo={ubigeo}"
    print(f"Navegando a: {url}")
    
    driver.get(url)
    time.sleep(5) # wait for page to load or cloudflare challenge
    
    try:
        # the JSON should be visible in the body
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print("Texto obtenido (primeros 200 chars):")
        print(body_text[:200])
        
        # Try to parse it
        data = json.loads(body_text)
        print("¡JSON parseado exitosamente!")
    except Exception as e:
        print(f"Error o respuesta no es JSON: {e}")
        # Let's save a screenshot to see what's happening
        driver.save_screenshot("selenium_test.png")
        print("Screenshot guardado en selenium_test.png")
        
    driver.quit()

if __name__ == "__main__":
    test_selenium_json()
