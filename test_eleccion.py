import undetected_chromedriver as uc
import time
import json

def test():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=148)
    
    url1 = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina=0&tamanio=15&idAmbitoGeografico=1&idUbigeo=140143"
    url2 = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina=0&tamanio=15&idAmbitoGeografico=1&idUbigeo=140143&idEleccion=10"
    
    driver.get(url1)
    time.sleep(2)
    b1 = driver.find_element('tag name', 'body').text
    print("URL1 Total Registros:", json.loads(b1).get('data', {}).get('totalRegistros'))
    
    driver.get(url2)
    time.sleep(2)
    b2 = driver.find_element('tag name', 'body').text
    print("URL2 Total Registros:", json.loads(b2).get('data', {}).get('totalRegistros'))
    
    driver.quit()

if __name__ == "__main__":
    test()
