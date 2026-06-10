# 🗳️ Scraper ONPE — Resultados Presidenciales 2026

> **Extracción automatizada de resultados electorales presidenciales** desde el portal oficial de la [ONPE](https://resultadoelectoral.onpe.gob.pe/) (Oficina Nacional de Procesos Electorales del Perú).

---

## 📋 Descripción

Este proyecto contiene un conjunto de scrapers en Python diseñados para extraer los resultados de las **Elecciones Presidenciales 2026** directamente desde la API del portal de resultados electorales de la ONPE. Los datos se obtienen a nivel de **mesa de votación**, incluyendo:

- 🏛️ **Local de votación**
- 🗳️ **Código de mesa**
- 🏳️ **Partido político**
- 👤 **Candidato** (nombre completo)
- 📊 **Total de votos**

Los resultados se consolidan y exportan en archivos **Excel (.xlsx)** organizados por local de votación, con una hoja por cada centro.

---

## 🏗️ Arquitectura del Proyecto

```
presidenciales/
├── 📂 Excel/                         # Archivos Excel generados con resultados
│   ├── Resultados_El_Agustino_Presidenciales.xlsx
│   ├── Resultados_Muestra.xlsx
│   ├── Resultados_Santa_Anita.xlsx
│   └── Resultados_Santa_Anita_Presidenciales.xlsx
│
├── 🕷️ Scrapers principales
│   ├── scraper_onpe.py               # Scraper con requests (básico)
│   ├── scraper_onpe_selenium.py      # Scraper con undetected-chromedriver
│   ├── scraper_onpe_playwright.py    # Scraper con Playwright (async)
│   ├── scraper_onpe_bypassed.py      # Scraper con curl_cffi (TLS fingerprint)
│   └── scraper_onpe_cloudscraper.py  # Scraper con cloudscraper
│
├── 🧪 Scripts de exploración y testing
│   ├── explore_api.py                # Exploración de endpoints de la API
│   ├── intercept_api.py              # Interceptor de respuestas HTTP (Playwright)
│   ├── test_api.py                   # Pruebas de conectividad a la API
│   ├── test_selenium.py              # Pruebas con Selenium
│   ├── test_detalle.py               # Pruebas de endpoint de detalle
│   ├── test_eleccion.py              # Pruebas de endpoint de elección
│   └── test_parse.py                 # Pruebas de parseo de respuestas JSON
│
├── 🔧 Utilidades
│   ├── generar_excel_manual.py       # Consolidador de JSONs descargados manualmente
│   ├── screenshot.py                 # Captura de pantalla del sitio
│   └── main_page_script.py          # Script auxiliar de la página principal
│
├── 📄 Archivos de referencia
│   ├── sample.json                   # JSON de ejemplo (estructura de un acta)
│   ├── content.html                  # HTML capturado de referencia
│   └── main_page.html               # Página principal capturada
│
└── 📁 .venv/                         # Entorno virtual de Python
```

---

## 🔀 Estrategias de Scraping

El sitio de la ONPE implementa protecciones **WAF (Web Application Firewall)** que bloquean peticiones automatizadas. Por ello, el proyecto incluye **5 estrategias** diferentes:

| Estrategia | Archivo | Librería | Notas |
|---|---|---|---|
| **Básica** | `scraper_onpe.py` | `requests` | Peticiones HTTP directas. Puede ser bloqueada por el WAF. |
| **Selenium** | `scraper_onpe_selenium.py` | `undetected-chromedriver` | Navegador real automatizado. Evade la mayoría de detecciones. |
| **Playwright** | `scraper_onpe_playwright.py` | `playwright` | Navegador headless con `fetch()` interno. Hereda cookies del contexto. |
| **TLS Bypass** | `scraper_onpe_bypassed.py` | `curl_cffi` | Impersonación de TLS fingerprint de Chrome. Sin navegador. |
| **CloudScraper** | `scraper_onpe_cloudscraper.py` | `cloudscraper` | Bypass automático de Cloudflare y protecciones similares. |

> **💡 Recomendación:** Para los mejores resultados, usar `scraper_onpe_selenium.py` o `scraper_onpe_playwright.py`.

---

## 🔗 API de la ONPE

Los scrapers consumen los siguientes endpoints:

```
BASE_URL = https://resultadoelectoral.onpe.gob.pe/presentacion-backend
```

| Endpoint | Descripción |
|---|---|
| `GET /actas?pagina={p}&tamanio={t}&idAmbitoGeografico=1&idUbigeo={ubigeo}` | Lista paginada de actas por ubigeo |
| `GET /actas/{id}` | Detalle completo de un acta específica |
| `GET /ubigeos/locales?idUbigeo={ubigeo}` | Locales de votación por ubigeo |

### Estructura de respuesta (JSON)

```json
{
  "success": true,
  "data": {
    "codigoMesa": "061565",
    "nombreLocalVotacion": "IE 0096 ENRIQUE PALACIOS MENDIBURO",
    "totalElectoresHabiles": 299,
    "totalVotosEmitidos": 261,
    "totalVotosValidos": 236,
    "detalle": [
      {
        "descripcion": "FUERZA POPULAR",
        "nvotos": 60,
        "candidato": [
          {
            "nombres": "KEIKO SOFIA",
            "apellidoPaterno": "FUJIMORI",
            "apellidoMaterno": "HIGUCHI"
          }
        ]
      }
    ]
  }
}
```

---

## ⚙️ Instalación

### Requisitos previos

- **Python 3.10+**
- **Google Chrome** (para Selenium) o **Chromium** (para Playwright)

### Configuración

```bash
# 1. Clonar el repositorio
git clone https://github.com/joechadu/scrappin-onpe.git
cd scrappin-onpe

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Instalar dependencias según la estrategia deseada
```

### Dependencias por estrategia

```bash
# Base (común a todos)
pip install pandas openpyxl

# Para scraper_onpe.py
pip install requests

# Para scraper_onpe_selenium.py
pip install undetected-chromedriver selenium

# Para scraper_onpe_playwright.py
pip install playwright
playwright install chromium

# Para scraper_onpe_bypassed.py
pip install curl-cffi

# Para scraper_onpe_cloudscraper.py
pip install cloudscraper
```

---

## 🚀 Uso

### Ejecutar un scraper

```bash
# Scraper recomendado (Selenium)
python scraper_onpe_selenium.py

# Alternativa con Playwright
python scraper_onpe_playwright.py

# Alternativas ligeras (sin navegador)
python scraper_onpe_bypassed.py
python scraper_onpe_cloudscraper.py
python scraper_onpe.py
```

### Cambiar el distrito/ubigeo

En cada scraper, modifica la variable `ubigeo` al inicio de la función principal:

```python
ubigeo = "140135"  # Ejemplo: Santa Anita = 140135 / 140143
```

> Puedes obtener los códigos de ubigeo desde el portal de la ONPE o usando `explore_api.py`.

### Consolidar datos manuales

Si descargaste JSONs manualmente desde el navegador:

```bash
# Colocar archivos .json en la carpeta datos_manuales/
python generar_excel_manual.py
```

---

## 📊 Salida

Los scrapers generan archivos **Excel (.xlsx)** con la siguiente estructura:

- **Una hoja por local de votación** (nombre del centro educativo o local)
- Cada hoja contiene las columnas:

| Columna | Descripción |
|---|---|
| Local de Votación | Nombre del centro de votación |
| Partido Político | Agrupación política |
| Candidato | Nombre completo del candidato |
| Total Votos | Suma de votos obtenidos |

Los datos se agrupan por local → partido → candidato con los votos sumados, y se ordenan de mayor a menor cantidad de votos.

---

## 🧪 Scripts de Testing

| Script | Propósito |
|---|---|
| `test_api.py` | Verificar conectividad y formato de respuesta de la API |
| `test_selenium.py` | Probar que Selenium/Chrome funcionen correctamente |
| `test_detalle.py` | Probar el endpoint de detalle de un acta específica |
| `test_eleccion.py` | Probar el endpoint de elecciones |
| `test_parse.py` | Verificar el parseo correcto de las respuestas JSON |
| `explore_api.py` | Explorar endpoints disponibles (locales, actas) |
| `intercept_api.py` | Interceptar y loguear todas las respuestas HTTP del sitio |

---

## ⚠️ Consideraciones

- **Uso responsable**: Este proyecto es para fines de análisis electoral con datos públicos. Respetar los términos de uso del portal de la ONPE.
- **Rate limiting**: Los scrapers incluyen pausas (`time.sleep()`) entre peticiones para no saturar el servidor.
- **Protección WAF**: El sitio puede cambiar sus mecanismos de protección. Si un scraper deja de funcionar, probar con otra estrategia.
- **Datos públicos**: Toda la información extraída es de acceso público a través del portal oficial de resultados de la ONPE.

---

## 📝 Licencia

Este proyecto es de código abierto con fines educativos y de transparencia electoral.

---

<p align="center">
  <br>
  ```diff
+    ****    *****   ******  *****
+   *    *   *    *  *       *    *
+   *    *   *****   ****    *    *
+   *    *   *    *  *       *    *
+    ****    *****   ******  *****
```
</p>
