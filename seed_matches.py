import os
from scrapling import StealthyFetcher
from supabase import create_client

# Configuración de conexión
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)

fetcher = StealthyFetcher()

# IDs de ligas solicitadas:
# 10385: Liga F (España)
# 209: WSL (Inglaterra)
# 9812: Champions Femenina
# 212: D1 Arkema (Francia)
leagues = [10385, 209, 9812, 212]

# Temporada actual 2025/2026
seasons = ["2025/2026", "2025"]

def seed():
    for league_id in leagues:
        for season in seasons:
            # Intentamos primero con el endpoint de 'leagues'
            target_url = f"https://www.fotmob.com/api/leagues?id={league_id}&season={season}"
            print(f"--- Intentando Liga {league_id} | Temporada {season} ---")
            
            page = fetcher.fetch(target_url)
            
            # Si da 404, probamos el endpoint alternativo 'league'
            if page.status != 200:
                target_url = f"https://www.fotmob.com/api/league?id={league_id}&season={season}"
                page = fetcher.fetch(target_url)
            
            if page.status == 200:
                try:
                    data = page.json()
                    
                    # Buscamos los partidos en las diferentes estructuras posibles del JSON de FotMob
                    matches = []
                    if 'matches' in data and 'allMatches' in data['matches']:
                        matches = data['matches']['allMatches']
                    elif 'leagueView' in data and 'matches' in data['leagueView']:
                        matches = data['leagueView']['matches'].get('allMatches', [])
                    
                    if not matches:
                        print(f"Conectado a {league_id}, pero no se encontraron partidos aún.")
                        continue

                    for m in matches:
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
                        # Upsert para no duplicar si el script se corre varias veces
                        supabase.table("matches").upsert(match_data).execute()
                    
                    print(f"✅ Éxito: Partidos cargados para la liga {league_id}")
                    break # Si funciona con un formato de temporada, no hace falta probar el siguiente

                except Exception as e:
                    print(f"❌ Error procesando datos de {league_id}: {e}")
            else:
                print(f"⚠️ No se pudo acceder a {league_id} (Status: {page.status})")

if __name__ == "__main__":
    seed()
