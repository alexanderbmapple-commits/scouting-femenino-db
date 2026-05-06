import os
import json
import scrapling
from scrapling import StealthyFetcher
from supabase import create_client

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
fetcher = StealthyFetcher()

# Usamos directamente los endpoints de la API que cargan el calendario
league_configs = [
    {"id": 10385, "name": "Liga F (España)", "url": "https://www.fotmob.com/api/league?id=10385&season=2024%2F2025"},
    {"id": 9812, "name": "Champions Femenina", "url": "https://www.fotmob.com/api/league?id=9812&season=2024%2F2025"},
    {"id": 209, "name": "WSL (Inglaterra)", "url": "https://www.fotmob.com/api/league?id=209&season=2024%2F2025"},
    {"id": 212, "name": "D1 Arkema (Francia)", "url": "https://www.fotmob.com/api/league?id=212&season=2024%2F2025"}
]

def seed():
    for config in league_configs:
        print(f"--- Forzando extracción de {config['name']} ---")
        # Usamos Scrapling para que gestione las cookies y el bypass automáticamente
        page = fetcher.fetch(config['url'])
        
        if page.status == 200:
            try:
                # Al ser un endpoint de API, la respuesta ya es el JSON que queremos
                data = json.loads(page.text)
                
                # En la API, los partidos suelen estar en 'matches' -> 'allMatches' 
                # o en 'leagueView' -> 'matches'
                fixtures = []
                if 'matches' in data:
                    fixtures = data['matches'].get('allMatches', [])
                elif 'leagueView' in data:
                    fixtures = data['leagueView'].get('matches', {}).get('allMatches', [])

                if fixtures:
                    count = 0
                    for m in fixtures:
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
                    print(f"✅ ÉXITO TOTAL: {count} partidos de {config['name']} guardados.")
                else:
                    print(f"❌ La API no devolvió partidos para {config['name']}. Estructura recibida: {list(data.keys())}")
            except Exception as e:
                print(f"❌ Error procesando JSON de {config['name']}: {e}")
        else:
            print(f"⚠️ Error de conexión {page.status} para {config['name']}")

if __name__ == "__main__":
    seed()
