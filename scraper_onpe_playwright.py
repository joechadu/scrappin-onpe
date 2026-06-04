import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright

async def scrape_onpe_santa_anita_playwright():
    ubigeo = "140143"
    resultados = []
    mesas_procesadas = set()
    
    print(f"Iniciando scraping (con Playwright headless browser) de actas para el Ubigeo {ubigeo}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a realistic user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # First visit the main page to get cookies and tokens if any
        await page.goto("https://resultadoelectoral.onpe.gob.pe/", wait_until="networkidle")

        pagina = 0
        tamanio = 15

        while True:
            # We fetch using the page context to automatically attach cookies and headers
            url_actas = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas?pagina={pagina}&tamanio={tamanio}&idAmbitoGeografico=1&idUbigeo={ubigeo}"
            
            try:
                # We use page.evaluate to run fetch inside the browser context, bypassing many WAFs
                response_text = await page.evaluate(f"""
                    async () => {{
                        const res = await fetch("{url_actas}", {{
                            headers: {{
                                "Accept": "application/json, text/plain, */*"
                            }}
                        }});
                        if (res.headers.get("Content-Type")?.includes("html")) {{
                            return "HTML";
                        }}
                        return await res.text();
                    }}
                """)

                if response_text == "HTML" or response_text is None:
                    print(f"ALERTA: La API devolvió HTML en la página {pagina}. Posible bloqueo.")
                    break

                try:
                    json_response = json.loads(response_text)
                except Exception as e:
                    print(f"Error parseando JSON: {response_text[:100]}")
                    break

                if isinstance(json_response, dict):
                    actas = json_response.get('data', json_response.get('actas', []))
                else:
                    actas = json_response

                if not actas:
                    print("No se encontraron más actas.")
                    break

                for acta_resumen in actas:
                    if not isinstance(acta_resumen, dict):
                        continue

                    if 'detalle' not in acta_resumen:
                        acta_id = acta_resumen.get('id')
                        if not acta_id:
                            continue

                        url_detalle = f"https://resultadoelectoral.onpe.gob.pe/presentacion-backend/actas/{acta_id}"
                        detalle_text = await page.evaluate(f"""
                            async () => {{
                                const res = await fetch("{url_detalle}", {{
                                    headers: {{
                                        "Accept": "application/json, text/plain, */*"
                                    }}
                                }});
                                if (res.headers.get("Content-Type")?.includes("html")) {{
                                    return "HTML";
                                }}
                                return await res.text();
                            }}
                        """)
                        
                        if detalle_text == "HTML" or detalle_text is None:
                            continue

                        try:
                            detalle_data = json.loads(detalle_text)
                            acta = detalle_data.get('data', {}) if isinstance(detalle_data, dict) else {}
                        except:
                            continue

                        await asyncio.sleep(0.5)
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
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error procesando la página {pagina}: {e}")
                break

        await browser.close()

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
    asyncio.run(scrape_onpe_santa_anita_playwright())
