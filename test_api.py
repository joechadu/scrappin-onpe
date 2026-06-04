import requests

url_locales = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/ubigeos/locales?idUbigeo=140143"
url_actas = "https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina=0&tamanio=15&idAmbitoGeografico=1&idUbigeo=140143"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-PE,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://resultadoelectoral.onpe.gob.pe",
    "Referer": "https://resultadoelectoral.onpe.gob.pe/",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive"
}

r = requests.get(url_locales, headers=headers)
print("Status locales:", r.status_code)
print("Content-Type:", r.headers.get('content-type'))
print(r.text[:500])

r2 = requests.get(url_actas, headers=headers)
print("\nStatus actas:", r2.status_code)
print("Content-Type:", r2.headers.get('content-type'))
print(r2.text[:500])
