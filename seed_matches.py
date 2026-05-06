import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

# Configuración de credenciales
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)

fetcher = StealthyFetcher()

# IDs: 10385 (España), 209 (Inglaterra), 9812 (Champions), 212 (Francia)
leagues = [10385, 209, 9812, 212]

def seed():
    for league_id in leagues:
        # Usamos la URL base que es la que menos falla
        target_url = f"https://www.fotmob.com/leagues/{league_id}/overview"
        print(f"--- Procesando Liga {league_id} ---")
        
        page = fetcher.fetch(target_url)
        
        if page.status != 200:
            print(f"⚠️ Salto liga {league_id} por status {page.status}")
            continue

        try:
            # Extraemos el texto del script usando .text (la forma más compatible)
            # En Scrapling, page.css() devuelve una lista, tomamos el primero y su texto
            data_element = page.css('script#__NEXT_DATA__').first
            
            if data_element:
                # Obtenemos el texto plano contenido en la etiqueta
                json_text = data_element.text.strip()
                json_data = json.loads(json_text)
                
                props = json_data.get('props', {}).get('pageProps', {})
                
                # Buscamos los partidos (fixtures) en las rutas posibles del JSON
                fixtures = []
                if 'overview' in props:
                    fixtures = props['overview'].get('leagueMatches', [])
                
                if not fixtures and 'fallback' in props:
                    # Si no está en overview, buscamos en el cache del fallback
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
                        # Guardamos en Supabase
                        supabase.table("matches").upsert(match_data).execute()
                    print(f"✅ ÉXITO: {len(fixtures)} partidos cargados para la liga {league_id}")
                else:
                    print(f"❓ No encontré partidos en el JSON de {league_id}")
            else:
                print(f"❌ No localicé el bloque __NEXT_DATA__ en {league_id}")

        except Exception as e:
            print(f"❌ Error crítico en {league_id}: {str(e)}")

if __name__ == "__main__":
    seed()
