import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

# Configuración
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)

fetcher = StealthyFetcher()

# IDs: 10385 (España), 209 (Inglaterra), 9812 (Champions), 212 (Francia)
leagues = [10385, 209, 9812, 212]

def seed():
    for league_id in leagues:
        # Usamos la URL principal de la liga para asegurar el 200 OK
        target_url = f"https://www.fotmob.com/leagues/{league_id}/overview/"
        print(f"--- Extrayendo Liga {league_id} desde {target_url} ---")
        
        page = fetcher.fetch(target_url)
        
        if page.status != 200:
            print(f"⚠️ Error {page.status} al acceder a la liga {league_id}")
            continue

        try:
            # CORRECCIÓN AQUÍ: .first sin paréntesis
            data_script = page.css('script#__NEXT_DATA__::text').first
            
            if data_script:
                json_data = json.loads(data_script)
                props = json_data.get('props', {}).get('pageProps', {})
                
                # Buscamos partidos en la sección 'overview' o 'fixtures' dentro del JSON
                fixtures = []
                # Intentamos varias rutas comunes en el JSON de FotMob
                if 'overview' in props and 'leagueMatches' in props['overview']:
                    fixtures = props['overview']['leagueMatches']
                elif 'fallback' in props:
                    # A veces los datos están en el cache de fallback
                    for key in props['fallback']:
                        if 'allMatches' in props['fallback'][key]:
                            fixtures = props['fallback'][key]['allMatches']
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
                    print(f"✅ Éxito: {len(fixtures)} partidos sincronizados para {league_id}")
                else:
                    print(f"❓ No se encontraron partidos listados para {league_id}")
            else:
                print(f"❌ No se detectó el bloque de datos (__NEXT_DATA__) para {league_id}")

        except Exception as e:
            print(f"❌ Error en liga {league_id}: {str(e)}")

if __name__ == "__main__":
    seed()
