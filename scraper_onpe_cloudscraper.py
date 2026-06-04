import cloudscraper
import pandas as pd
import time

def scrape_onpe_santa_anita_cloudscraper():
    ubigeo = "140143"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://resultadoelectoral.onpe.gob.pe",
        "Referer": "https://resultadoelectoral.onpe.gob.pe/"
    }

    resultados = []
    mesas_procesadas = set()

    pagina = 0
    tamanio = 15
    
    print(f"Iniciando scraping (con cloudscraper bypass) de actas para el Ubigeo {ubigeo}...")
    
    scraper = cloudscraper.create_scraper()
    
    while True:
        url_actas = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina={pagina}&tamanio={tamanio}&idAmbitoGeografico=1&idUbigeo={ubigeo}"
        
        try:
            res_actas = scraper.get(url_actas, headers=headers, timeout=15)
            
            if "html" in res_actas.headers.get("Content-Type", ""):
                print(f"ALERTA: La API devolvió HTML en la página {pagina}. El bypass falló o el endpoint está caído.")
                break
                
            try:
                json_response = res_actas.json()
            except Exception as e:
                print(f"Error parseando JSON: la respuesta fue: {res_actas.text[:200]}")
                break
            
            if isinstance(json_response, str):
                print(f"La API devolvió un string en vez de JSON: {json_response[:100]}")
                break
                
            if isinstance(json_response, dict):
                actas = json_response.get('data', json_response.get('actas', []))
            else:
                actas = json_response
                
            if not actas:
                print("No se encontraron más actas.")
                break
                
            if isinstance(actas, str):
                print(f"Estructura inesperada: {str(actas)[:100]}")
                break
                
            for acta_resumen in actas:
                if not isinstance(acta_resumen, dict):
                    continue
                    
                if 'detalle' not in acta_resumen:
                    acta_id = acta_resumen.get('id')
                    if not acta_id:
                        continue
                        
                    url_detalle = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas/{acta_id}"
                    res_detalle = scraper.get(url_detalle, headers=headers, timeout=10)
                    if "html" in res_detalle.headers.get("Content-Type", ""):
                        continue
                        
                    try:
                        detalle_data = res_detalle.json()
                        acta = detalle_data.get('data', {}) if isinstance(detalle_data, dict) else {}
                    except:
                        continue
                        
                    time.sleep(0.5)
                else:
                    acta = acta_resumen
                
                mesa = acta.get('codigoMesa', 'Desconocido')
                
                if mesa in mesas_procesadas:
                    continue
                mesas_procesadas.add(mesa)
                
                local_nombre = acta.get('nombreLocalVotacion', 'Desconocido')
                detalles = acta.get('detalle', [])
                
                for item in detalles:
                    partido = item.get('descripcion', 'Desconocido')
                    votos = item.get('nvotos', 0)
                    
                    candidato_info = item.get('candidato', [])
                    if candidato_info and len(candidato_info) > 0:
                        c = candidato_info[0]
                        nombre_candidato = f"{c.get('nombres', '')} {c.get('apellidoPaterno', '')} {c.get('apellidoMaterno', '')}".strip()
                    else:
                        nombre_candidato = "N/A"
                        
                    resultados.append({
                        "Local de Votación": local_nombre,
                        "Mesa": mesa,
                        "Partido Político": partido,
                        "Candidato": nombre_candidato,
                        "Total Votos": votos
                    })
                    
            print(f"Página {pagina} procesada exitosamente...")
            pagina += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"Error general procesando la página {pagina}: {e}")
            break
            
    if resultados:
        print(f"Generando Excel con {len(resultados)} registros en total...")
        df = pd.DataFrame(resultados)
        
        df['Total Votos'] = pd.to_numeric(df['Total Votos'], errors='coerce').fillna(0)
        
        resumen = df.groupby(['Local de Votación', 'Partido Político', 'Candidato'])['Total Votos'].sum().reset_index()
        resumen = resumen.sort_values(by=['Local de Votación', 'Total Votos'], ascending=[True, False])
        
        excel_file = "Resultados_Santa_Anita.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            locales = resumen['Local de Votación'].unique()
            for local in locales:
                df_local = resumen[resumen['Local de Votación'] == local]
                sheet_name = local.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '').replace(':', '')
                sheet_name = sheet_name.strip()[:31]
                df_local.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"\n¡Éxito! Se ha generado el archivo: {excel_file}")
    else:
        print("\nNo se pudieron obtener resultados para procesar.")

if __name__ == "__main__":
    scrape_onpe_santa_anita_cloudscraper()
