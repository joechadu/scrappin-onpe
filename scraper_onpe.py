import requests
import pandas as pd
import time

def scrape_onpe_santa_anita():
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
    tamanio = 15 # Usamos 15 como indico el usuario
    
    print(f"Iniciando scraping de actas para el Ubigeo {ubigeo}...")
    
    while True:
        url_actas = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina={pagina}&tamanio={tamanio}&idAmbitoGeografico=1&idUbigeo={ubigeo}"
        
        try:
            res_actas = requests.get(url_actas, headers=headers)
            
            if "html" in res_actas.headers.get("Content-Type", ""):
                print(f"ALERTA: La API devolvió HTML en la página {pagina}. Es posible que te estén bloqueando o el servicio esté en mantenimiento.")
                break
                
            json_response = res_actas.json()
            
            # Obtener el arreglo de actas
            # Si json_response tiene una propiedad 'data', la usamos, si no, probamos 'actas' o la raiz.
            if isinstance(json_response, dict):
                actas = json_response.get('data', json_response.get('actas', []))
            else:
                actas = json_response
                
            if not actas:
                print("No se encontraron más actas.")
                break # no hay más actas
                
            for acta_resumen in actas:
                # Si el acta en la paginación no trae el detalle completo, hacemos una peticion al endpoint de detalle
                if 'detalle' not in acta_resumen:
                    acta_id = acta_resumen.get('id')
                    if not acta_id:
                        continue
                        
                    url_detalle = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas/{acta_id}"
                    res_detalle = requests.get(url_detalle, headers=headers)
                    if "html" in res_detalle.headers.get("Content-Type", ""):
                        continue
                        
                    detalle_data = res_detalle.json()
                    acta = detalle_data.get('data', {})
                    time.sleep(0.5) # Pausa para evitar bloqueo por muchas peticiones rapidas
                else:
                    acta = acta_resumen
                
                mesa = acta.get('codigoMesa', 'Desconocido')
                
                # Evitar procesar dos veces la misma mesa
                if mesa in mesas_procesadas:
                    continue
                mesas_procesadas.add(mesa)
                
                local_nombre = acta.get('nombreLocalVotacion', 'Desconocido')
                detalles = acta.get('detalle', [])
                
                for item in detalles:
                    partido = item.get('descripcion', 'Desconocido')
                    votos = item.get('nvotos', 0)
                    
                    # Extraer el candidato
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
            time.sleep(1) # pausa para no saturar el servidor
            
        except Exception as e:
            print(f"Error procesando la página {pagina}: {e}")
            break
            
    if resultados:
        # Agrupar por local, partido y candidato
        print(f"Generando Excel con {len(resultados)} registros en total...")
        df = pd.DataFrame(resultados)
        
        # Convertir a numérico por si vienen como texto
        df['Total Votos'] = pd.to_numeric(df['Total Votos'], errors='coerce').fillna(0)
        
        # Agrupamos sumando los votos por Local, Partido y Candidato
        resumen = df.groupby(['Local de Votación', 'Partido Político', 'Candidato'])['Total Votos'].sum().reset_index()
        
        # Ordenamos los resultados por Local de Votación y luego por votos descendente
        resumen = resumen.sort_values(by=['Local de Votación', 'Total Votos'], ascending=[True, False])
        
        excel_file = "Resultados_Santa_Anita.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            locales = resumen['Local de Votación'].unique()
            for local in locales:
                df_local = resumen[resumen['Local de Votación'] == local]
                
                # Limpiar el nombre de la hoja (max 31 chars, sin caracteres especiales permitidos)
                sheet_name = local.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '').replace(':', '')
                sheet_name = sheet_name.strip()[:31]
                
                # Ocultar la columna 'Local de Votación' si se desea, o dejarla. La dejamos para claridad.
                df_local.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"\n¡Éxito! Se ha generado el archivo: {excel_file}")
    else:
        print("\nNo se pudieron obtener resultados para procesar.")

if __name__ == "__main__":
    scrape_onpe_santa_anita()
