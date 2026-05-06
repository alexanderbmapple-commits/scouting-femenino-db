import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
fetcher = StealthyFetcher()

# URLs confirmadas para la versión WEB (las que no dan 404)
league_configs = [
    {"id": 10385, "name": "Liga F (España)", "url": "https://www.fotmob.com/leagues/10385/matches/liga-f?season=2024-2025"},
    {"id": 9812, "name": "Champions Femenina", "url": "https://www.fotmob.com/leagues/9812/matches/womens-champions-league"},
    {"id": 209, "name": "WSL (Inglaterra)", "url": "https://www.fotmob.com/leagues/209/matches/wsl"},
    {"id": 212, "name": "D1 Arkema (Francia)", "url": "https://www.fotmob.com/leagues/212/matches/d1-arkema"}
]

def find_matches_recursively(data):
    """Busca listas de partidos en cualquier profundidad del JSON"""
    if isinstance(data, dict):
        # Intentamos capturar cualquier campo que contenga 'matches'
        for k, v in data.items():
            if k in ['allMatches', 'leagueMatches', 'matches'] and isinstance(v, (list, dict)):
                if isinstance(v, list): return v
                if isinstance(v, dict) and 'allMatches' in v: return v['allMatches']
            
            res = find_matches_recursively(v)
            if res: return res
    elif isinstance(data, list):
        for item in data:
            res = find_matches_recursively(item)
            if res: return res
    return None

def seed():
    for config in league_configs:
        print(f"--- Procesando {config['name']} ---")
        # Forzamos headers de navegador real
        page = fetcher.fetch(config['url'])
        
        if page.status != 200:
            print(f"⚠️ Error {page.status} en {config['name']}. Probando alternativa...")
            page = fetcher.fetch(f"https://www.fotmob.com/leagues/{config['id']}/overview")

        try:
            data_element = page.css('script#__NEXT_DATA__').first
            if data_element:
                json_data = json.loads(data_element.text.strip())
                fixtures = find_matches_recursively(json_data)

                if fixtures:
                    count = 0
                    for m in fixtures:
                        if 'id' in m and 'home' in m:
                            match_data = {
                                "id": str(m['id']),
                                "league_id": config['id'],
                                "season": "2024/2025",
                                "home_team": m['home']['name'],
                                "away_team": m['away']['name'],
                                "match_date": m['status'].get('utcTime'),
                                "status": "Finished" if m['status'].get('finished') else "Upcoming",
                                "processed": False
                            }
                            supabase.table("matches").upsert(match_data).execute()
                            count += 1
                    print(f"✅ ¡CONSEGUIDO! {count} partidos de {config['name']} cargados.")
                else:
                    print(f"❌ No encontré la lista de partidos en el JSON de {config['name']}.")
            else:
                print(f"❌ No se pudo extraer el bloque __NEXT_DATA__ de {config['name']}.")
        except Exception as e:
            print(f"❌ Error en {config['name']}: {str(e)}")

if __name__ == "__main__":
    seed()
