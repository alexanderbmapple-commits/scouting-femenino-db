import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
fetcher = StealthyFetcher()

# Configuración con las rutas de 'matches' confirmadas
league_configs = [
    {"id": 10385, "name": "Liga F (España)", "url": "https://www.fotmob.com/leagues/10385/matches/liga-f"},
    {"id": 9812, "name": "Champions Femenina", "url": "https://www.fotmob.com/leagues/9812/matches/womens-champions-league"},
    {"id": 209, "name": "WSL (Inglaterra)", "url": "https://www.fotmob.com/leagues/209/matches/wsl"},
    {"id": 212, "name": "D1 Arkema (Francia)", "url": "https://www.fotmob.com/leagues/212/matches/d1-arkema"}
]

def find_matches_recursively(data):
    if isinstance(data, dict):
        # Buscamos en todas las variantes de nombres que usa FotMob
        for key in ['allMatches', 'leagueMatches', 'matches']:
            if key in data and data[key]:
                # Si es una lista directa, la devolvemos
                if isinstance(data[key], list): return data[key]
                # Si es un dict (como en matches: {allMatches: []}), bajamos un nivel
                if isinstance(data[key], dict) and 'allMatches' in data[key]:
                    return data[key]['allMatches']
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
        print(f"--- Extrayendo {config['name']} ---")
        # Forzamos un referer para que FotMob crea que venimos de su propia home
        page = fetcher.fetch(config['url'], headers={"Referer": "https://www.fotmob.com/"})
        
        if page.status != 200:
            print(f"⚠️ Reintentando {config['name']} con URL base...")
            page = fetcher.fetch(f"https://www.fotmob.com/leagues/{config['id']}/")

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
                    print(f"✅ ÉXITO TOTAL: {count} partidos de {config['name']} en la base de datos.")
                else:
                    print(f"❌ No se localizaron partidos en el JSON de {config['name']}.")
            else:
                print(f"❌ Error crítico: No hay bloque de datos en el HTML de {config['name']}.")
        except Exception as e:
            print(f"❌ Fallo en {config['name']}: {e}")

if __name__ == "__main__":
    seed()
