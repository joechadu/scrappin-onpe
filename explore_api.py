import urllib.request
import json

url_locales = 'https://resultadoelectoral.onpe.gob.pe/presentacion-backend/ubigeos/locales?idUbigeo=140143'
url_actas = 'https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina=0&tamanio=15&idAmbitoGeografico=1&idUbigeo=140143'

try:
    req = urllib.request.Request(url_locales, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json, text/plain, */*'})
    with urllib.request.urlopen(req) as response:
        print("Locales JSON:")
        print(response.read().decode('utf-8')[:2000])
except Exception as e:
    print("Error fetching locales:", e)
    
try:
    req2 = urllib.request.Request(url_actas, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json, text/plain, */*'})
    with urllib.request.urlopen(req2) as response:
        print("\nActas JSON:")
        print(response.read().decode('utf-8')[:2000])
except Exception as e:
    print("Error fetching actas:", e)
