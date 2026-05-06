import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

# Configuración
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)

fetcher = StealthyFetcher()

# IDs: 10385 (ES), 209 (UK), 9812 (Champions), 212 (FR)
leagues = [10385, 209, 9812, 212]

def seed():
    for league_id in leagues:
        # Probamos con la URL base de la liga, que es la más estable
        target_url = f"https://www.fotmob.com/leagues/{league_id}/"
        print(f"--- Extrayendo Liga {league_id} ---")
        
        page = fetcher.fetch(target_url)
        
        if page.status != 200:
            print(f"⚠️ Salto liga {league_id}: Status {page.status}")
            continue

        try:
            # Extraemos el contenido crudo del script NEXT_DATA
            # Usamos .raw para obtener el string puro y evitar el error de la captura
            data_element = page.css('script#__NEXT_DATA__::text').first
            
            if data_element:
                # El .raw asegura que sea un string para json.loads
                json_text = data_element.raw.strip()
                json_data = json.loads(json_text)
                
                props = json_data.get('props', {}).get('pageProps', {})
                
                # Intentamos encontrar los partidos en las distintas secciones del JSON
                fixtures = []
                # Ruta 1: Overview
                fixtures = props.get('overview', {}).get('leagueMatches', [])
                
                # Ruta 2: Si la anterior falla, buscamos en el fallback de la API
                if not fixtures and 'fallback' in props:
                    for k in props['fallback']:
                        if 'allMatches' in props['fallback'][k]:
                            fixtures = props['fallback'][k]['allMatches']
                            break

                if fixtures:
                    for m in fixtures:
                        match_data = {
                            "id": str(m['id']),
                            "league_id": league_id,
                            "season": "2025/2026",
                            "home_team": m['home']['name'],
                            "away_team": m['away']['name'],
                            "match_date": m['status']['utcTime'],
                            "status": "Finished" if m['status'].get('finished') else "Upcoming",
                            "processed": False
                        }
                        supabase.table("matches").upsert(match_data).execute()
                    print(f"✅ ¡Éxito! {len(fixtures)} partidos cargados para {league_id}")
                else:
                    print(f"❓ No se encontraron datos de partidos en el JSON de {league_id}")
            else:
                print(f"❌ No se encontró el bloque de datos en el HTML de {league_id}")

        except Exception as e:
            print(f"❌ Error procesando {league_id}: {str(e)}")

if __name__ == "__main__":
    seed()
