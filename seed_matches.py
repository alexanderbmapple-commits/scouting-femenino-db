import os
import json
from scrapling import StealthyFetcher
from supabase import create_client

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
fetcher = StealthyFetcher()

# Configuración con los IDs y nombres exactos que me has pasado
league_configs = [
    {"id": 9907, "name": "Liga F (España)", "url": "https://www.fotmob.com/es/leagues/9907/matches/liga-f"},
    {"id": 9375, "name": "Champions Femenina", "url": "https://www.fotmob.com/es/leagues/9375/matches/womens-champions-league"},
    {"id": 9677, "name": "Premiere Ligue (Francia)", "url": "https://www.fotmob.com/es/leagues/9677/matches/premiere-ligue-feminine"},
    {"id": 9227, "name": "WSL (Inglaterra)", "url": "https://www.fotmob.com/es/leagues/9227/matches/wsl"},
    {"id": 10178, "name": "Serie A (Italia)", "url": "https://www.fotmob.com/es/leagues/10178/matches/serie-femminile"}
]

def find_matches_recursively(data):
    """Busca la lista de partidos dentro del objeto JSON de FotMob"""
    if isinstance(data, dict):
        for k in ['allMatches', 'leagueMatches', 'matches']:
            if k in data and data[k]:
                if isinstance(data[k], list): return data[k]
                if isinstance(data[k], dict) and 'allMatches' in data[k]: return data[k]['allMatches']
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
        print(f"--- Sincronizando {config['name']} (ID: {config['id']}) ---")
        # Forzamos un referer para evitar bloqueos
        page = fetcher.fetch(config['url'], headers={"Referer": "https://www.fotmob.com/"})
        
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
                                # Usamos upsert para no duplicar si ya existen
                                supabase.table("matches").upsert(match_data).execute()
                                count += 1
                        print(f"✅ ÉXITO: {count} partidos de {config['name']} en la base de datos.")
                    else:
                        print(f"❓ No se detectaron partidos en el JSON de {config['name']}")
                else:
                    print(f"❌ Error: No se encontró el bloque de datos __NEXT_DATA__ en {config['name']}")
            except Exception as e:
                print(f"❌ Fallo al procesar {config['name']}: {e}")
        else:
            print(f"❌ Error de conexión {page.status} para {config['name']}")

if __name__ == "__main__":
    seed()
