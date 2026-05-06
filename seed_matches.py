import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
fetcher = StealthyFetcher()

# IDs: España (10385), Inglaterra (209), Champions (9812), Francia (212)
leagues = [10385, 209, 9812, 212]

def find_matches_recursively(data):
    """Busca cualquier lista que parezca contener partidos en el JSON"""
    if isinstance(data, dict):
        # Si encontramos 'allMatches' o 'leagueMatches', lo devolvemos
        if 'allMatches' in data and data['allMatches']:
            return data['allMatches']
        if 'leagueMatches' in data and data['leagueMatches']:
            return data['leagueMatches']
        # Si no, seguimos buscando en los hijos
        for v in data.values():
            result = find_matches_recursively(v)
            if result: return result
    elif isinstance(data, list):
        for item in data:
            result = find_matches_recursively(item)
            if result: return result
    return None

def seed():
    for league_id in leagues:
        # Probamos con la URL de la temporada actual (2025/2026)
        target_url = f"https://www.fotmob.com/leagues/{league_id}/overview"
        print(f"--- Escaneando Liga {league_id} ---")
        
        page = fetcher.fetch(target_url)
        if page.status != 200:
            print(f"⚠️ Error {page.status} en {league_id}")
            continue

        try:
            data_element = page.css('script#__NEXT_DATA__').first
            if data_element:
                json_data = json.loads(data_element.text.strip())
                
                # Buscamos los partidos en TODO el objeto JSON
                fixtures = find_matches_recursively(json_data)

                if fixtures:
                    count = 0
                    for m in fixtures:
                        # Verificamos que tenga los datos mínimos
                        if 'id' in m and 'home' in m:
                            match_data = {
                                "id": str(m['id']),
                                "league_id": league_id,
                                "season": "2025/2026",
                                "home_team": m['home']['name'],
                                "away_team": m['away']['name'],
                                "match_date": m['status'].get('utcTime'),
                                "status": "Finished" if m['status'].get('finished') else "Upcoming",
                                "processed": False
                            }
                            supabase.table("matches").upsert(match_data).execute()
                            count += 1
                    print(f"✅ ¡CONSEGUIDO! {count} partidos insertados para {league_id}")
                else:
                    print(f"❓ No se detectaron listas de partidos en el JSON de {league_id}")
        except Exception as e:
            print(f"❌ Error en {league_id}: {e}")

if __name__ == "__main__":
    seed()
