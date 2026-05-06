import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

# Configuración
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)

fetcher = StealthyFetcher()

# Ligas: 10385 (ES), 209 (UK), 9812 (Champions), 212 (FR)
leagues = [10385, 209, 9812, 212]

def seed():
    for league_id in leagues:
        # Intentamos obtener la página de fixtures de la temporada actual
        # La URL pública es más difícil de bloquear que la API interna
        target_url = f"https://www.fotmob.com/leagues/{league_id}/fixtures/"
        print(f"--- Extrayendo Liga {league_id} desde {target_url} ---")
        
        page = fetcher.fetch(target_url)
        
        if page.status != 200:
            print(f"⚠️ Error {page.status} al acceder a la liga {league_id}")
            continue

        try:
            # FotMob guarda casi todos sus datos en un objeto JSON dentro de un script 'next-data'
            # Buscamos el script que contiene el estado de la página
            data_script = page.css('script#__NEXT_DATA__::text').first()
            
            if data_script:
                json_data = json.loads(data_script)
                # Navegamos por la estructura de Next.js para encontrar los partidos
                # La ruta suele ser props -> pageProps -> fallback -> (url de la api)
                # O directamente en props -> pageProps -> matches
                all_matches = []
                
                # Intentamos encontrar la lista de partidos en el JSON embebido
                props = json_data.get('props', {}).get('pageProps', {})
                fixtures = props.get('fixtures', {}).get('allMatches', [])
                
                if not fixtures:
                    # Ruta alternativa en algunas versiones de la web
                    fixtures = props.get('fallback', {}).get(next(iter(props.get('fallback', {})), {}), {}).get('allMatches', [])

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
                    print(f"✅ Cargados {len(fixtures)} partidos para la liga {league_id}")
                else:
                    print(f"❓ No se encontraron partidos en el JSON de la liga {league_id}")
            else:
                print(f"❌ No se pudo encontrar el script de datos para la liga {league_id}")

        except Exception as e:
            print(f"❌ Error procesando liga {league_id}: {str(e)}")

if __name__ == "__main__":
    seed()
