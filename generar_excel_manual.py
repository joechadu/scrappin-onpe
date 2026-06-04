import json
import pandas as pd
import os
import glob

def consolidar_jsons():
    carpeta_jsons = "datos_manuales"
    
    # Buscar todos los archivos .json en la carpeta
    archivos = glob.glob(os.path.join(carpeta_jsons, "*.json"))
    
    if not archivos:
        print(f"No se encontraron archivos .json en la carpeta '{carpeta_jsons}'.")
        return
        
    print(f"Encontrados {len(archivos)} archivos JSON. Procesando...")
    
    resultados = []
    
    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Dependiendo de si copian el JSON directo de "data" o el objeto completo "success, message, data"
            if "data" in data and isinstance(data["data"], dict):
                actas = [data["data"]]
            elif "data" in data and isinstance(data["data"], list):
                actas = data["data"]
            elif isinstance(data, list):
                actas = data
            elif isinstance(data, dict) and "detalle" in data:
                actas = [data]
            else:
                print(f"Formato desconocido en {archivo}, se omitirá.")
                continue
                
            for acta in actas:
                mesa = acta.get("codigoMesa", "Desconocido")
                local_nombre = acta.get("nombreLocalVotacion", "Desconocido")
                detalles = acta.get("detalle", [])
                
                for item in detalles:
                    partido = item.get("descripcion", "Desconocido")
                    votos = item.get("nvotos", 0)
                    
                    candidato_info = item.get("candidato", [])
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
        except Exception as e:
            print(f"Error procesando el archivo {archivo}: {e}")
            
    if resultados:
        print(f"Generando Excel con {len(resultados)} registros en total...")
        df = pd.DataFrame(resultados)
        
        df['Total Votos'] = pd.to_numeric(df['Total Votos'], errors='coerce').fillna(0)
        
        # Agrupar sumando votos
        resumen = df.groupby(['Local de Votación', 'Partido Político', 'Candidato'])['Total Votos'].sum().reset_index()
        resumen = resumen.sort_values(by=['Local de Votación', 'Total Votos'], ascending=[True, False])
        
        excel_file = "Resultados_Consolidados_Manual.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            locales = resumen['Local de Votación'].unique()
            for local in locales:
                df_local = resumen[resumen['Local de Votación'] == local]
                sheet_name = local.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '').replace(':', '')
                sheet_name = sheet_name.strip()[:31]
                if not sheet_name:
                    sheet_name = "Local_Desconocido"
                df_local.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"\n¡Éxito! Se ha generado el archivo: {excel_file}")
    else:
        print("\nNo se pudieron extraer datos de los archivos JSON proporcionados.")

if __name__ == "__main__":
    consolidar_jsons()
