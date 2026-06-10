# pyrefly: ignore [missing-import]
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json
import pandas as pd
import traceback

def scrape_onpe_santa_anita_selenium():
    ubigeo = "140135"
    
    print(f"Iniciando scraping con Selenium (undetected_chromedriver) para el Ubigeo {ubigeo}...")
    
    # Configuramos las opciones
    options = uc.ChromeOptions()
    # No usamos headless para saltarnos el WAF de manera más segura
    
    driver = uc.Chrome(options=options, version_main=148)
    
    resultados = []
    mesas_procesadas = set()
    pagina = 0
    tamanio = 15
    
    try:
        while True:
            url_actas = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina={pagina}&tamanio={tamanio}&idAmbitoGeografico=1&idUbigeo={ubigeo}"
            driver.get(url_actas)
            time.sleep(1) # Esperar a que renderice o pase WAF
            
            # Obtener el texto del body que contiene el JSON
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                json_response = json.loads(body_text)
            except Exception as e:
                print(f"ALERTA: La API no devolvió JSON válido en la página {pagina}. {e}")
                break
                
            # Extraer las actas (en tu json se llama 'content' o 'data')
            if isinstance(json_response, dict):
                actas = json_response.get('data', {}).get('content', [])
                if not actas:
                    actas = json_response.get('data', json_response.get('actas', []))
            if not actas:
                print("No se encontraron más actas.")
                break
                
            for acta_resumen in actas:
                acta_id = acta_resumen.get('id')
                if not acta_id or not str(acta_id).endswith('10'):
                    continue
                    
                # Si no hay detalle válido, lo buscamos
                if not acta_resumen.get('detalle'):
                    url_detalle = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas/{acta_id}"
                    
                    max_retries = 3
                    for intento in range(max_retries):
                        driver.get(url_detalle)
                        time.sleep(1) # Un poco más de tiempo
                        
                        try:
                            detalle_text = driver.find_element(By.TAG_NAME, "body").text
                            detalle_data = json.loads(detalle_text)
                            acta = detalle_data.get('data', {}) if isinstance(detalle_data, dict) else {}
                            break # Exito
                        except Exception as e:
                            if intento == max_retries - 1:
                                print(f"Error parseando detalle del acta {acta_id} después de {max_retries} intentos.")
                                acta = {}
                            else:
                                print(f"Posible bloqueo o demora en detalle {acta_id}. Reintentando en 5 seg...")
                                time.sleep(5)
                else:
                    acta = acta_resumen
                
                mesa = acta.get('codigoMesa', 'Desconocido')
                
                if mesa in mesas_procesadas:
                    continue
                mesas_procesadas.add(mesa)
                
                local_nombre = acta.get('nombreLocalVotacion', 'Desconocido')
                detalles = acta.get('detalle') or []
                
                # Debug print
                print(f"Mesa: {mesa}, Local: {local_nombre}, Detalles encontrados: {len(detalles)}")
                
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
                    
            print(f"Página {pagina} procesada exitosamente. Total resultados hasta ahora: {len(resultados)}")
            pagina += 1
            time.sleep(1)
            
    except Exception as e:
        print(f"Error general en página {pagina}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass
            
    if resultados:
        print(f"Generando Excel con {len(resultados)} registros en total...")
        df = pd.DataFrame(resultados)
        
        df['Total Votos'] = pd.to_numeric(df['Total Votos'], errors='coerce').fillna(0)
        
        resumen = df.groupby(['Local de Votación', 'Partido Político', 'Candidato'])['Total Votos'].sum().reset_index()
        resumen = resumen.sort_values(by=['Local de Votación', 'Total Votos'], ascending=[True, False])
        
        excel_file = "Resultados_Presidenciales_2026.xlsx"
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
    scrape_onpe_santa_anita_selenium()
