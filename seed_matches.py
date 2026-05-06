import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
fetcher = StealthyFetcher()

# Mapeo de URLs manual para evitar el 404
# He verificado que estas rutas son las que FotMob usa actualmente para la web
league_configs = [
    {"id": 10385, "name": "Liga F (España)", "url": "https://www.fotmob.com/leagues/10385/overview/liga-f"},
    {"id": 209, "name": "WSL (Inglaterra)", "url": "https://www.fotmob.com/leagues/209/overview/wsl"},
    {"id": 9812, "name": "Champions Femenina", "url": "https://www.fotmob.com/leagues/9812/overview/womens-champions-league"},
    {"id": 212, "name": "D1 Arkema (Francia)", "url": "https://www.fotmob.com/leagues/212/overview/d1-arkema"}
]

def find_matches_recursively(data):
    if isinstance(data, dict):
        if 'allMatches' in data and data['allMatches']: return data['allMatches']
        if 'leagueMatches' in data and data['leagueMatches']: return data['leagueMatches']
        for v in data.values():
            res = find_matches_recursively(v)
            if res: return res
    elif isinstance(data, list):
        for item in data:
            res = find_matches_recursively(item)
            if res: return res
    return None

def seed():
    for config in league_configs:
        print(f"--- Intentando con {config['name']} ---")
        page = fetcher.fetch(config['url'])
        
        if page.status != 200:
            print(f"⚠️ Sigue dando error {page.status} en {config['name']}. Probando URL base...")
            page = fetcher.fetch(f"https://www.fotmob.com/leagues/{config['id']}/")

        if page.status == 200:
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
                                    "season": "2025/2026",
                                    "home_team": m['home']['name'],
                                    "away_team": m['away']['name'],
                                    "match_date": m['status'].get('utcTime'),
                                    "status": "Finished" if m['status'].get('finished') else "Upcoming",
                                    "processed": False
                                }
                                supabase.table("matches").upsert(match_data).execute()
                                count += 1
                        print(f"✅ ÉXITO: {count} partidos de {config['name']} sincronizados.")
                    else:
                        print(f"❓ No se encontraron partidos en el JSON de {config['name']}")
            except Exception as e:
                print(f"❌ Error en {config['name']}: {e}")
        else:
            print(f"❌ Imposible acceder a {config['name']} (Status {page.status})")

if __name__ == "__main__":
    seed()
