import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json

def test_detalle():
    print("Iniciando prueba de detalle...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=148)
    
    url_detalle = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas/6156514014310"
    driver.get(url_detalle)
    time.sleep(3)
    
    body_text = driver.find_element(By.TAG_NAME, "body").text
    print("Respuesta del servidor:")
    print(body_text[:1000])
    
    driver.quit()

if __name__ == "__main__":
    test_detalle()
