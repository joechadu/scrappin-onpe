import json
import pandas as pd

def test_json():
    with open("sample.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    resultados = []
    acta = data.get("data", {})
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
        
    if resultados:
        df = pd.DataFrame(resultados)
        df['Total Votos'] = pd.to_numeric(df['Total Votos'], errors='coerce').fillna(0)
        resumen = df.groupby(['Local de Votación', 'Partido Político', 'Candidato'])['Total Votos'].sum().reset_index()
        resumen = resumen.sort_values(by=['Local de Votación', 'Total Votos'], ascending=[True, False])
        excel_file = "Resultados_Muestra.xlsx"
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            locales = resumen['Local de Votación'].unique()
            for local in locales:
                df_local = resumen[resumen['Local de Votación'] == local]
                sheet_name = local.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '').replace(':', '')
                sheet_name = sheet_name.strip()[:31]
                df_local.to_excel(writer, sheet_name=sheet_name, index=False)
        print("Excel generado exitosamente.")
    else:
        print("No se encontraron resultados.")

if __name__ == "__main__":
    test_json()
