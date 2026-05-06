import os
from scrapling import StealthyFetcher
from supabase import create_client

# Conexión limpia
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)

fetcher = StealthyFetcher()

# Configuración de Ligas Femeninas
# 10385: España | 209: Inglaterra | 9812: Champions | 212: Francia
leagues = [10385, 209, 9812, 212]
# Probamos con el ID de temporada que FotMob usa internamente para 25/26
seasons = ["20252026", "2025"] 

def seed():
    for league_id in leagues:
        success = False
        for season in seasons:
            # URL simplificada que suele saltarse mejor los bloqueos de API
            target_url = f"https://www.fotmob.com/api/leagues?id={league_id}"
            print(f"--- Consultando Liga {league_id} ---")
            
            page = fetcher.fetch(target_url)
            
            if page.status == 200:
                try:
                    data = page.json()
                    # Buscamos los partidos en la sección de 'matches'
                    matches_data = data.get('matches', {})
                    all_matches = matches_data.get('allMatches', [])

                    if not all_matches:
                        # Reintento: a veces los datos están en leagueView
                        all_matches = data.get('leagueView', {}).get('matches', {}).get('allMatches', [])

                    if all_matches:
                        for m in all_matches:
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
                        
                        print(f"✅ ¡ÉXITO! Datos cargados para liga {league_id}")
                        success = True
                        break # Pasamos a la siguiente liga
                except Exception as e:
                    print(f"❌ Error al procesar JSON de {league_id}: {e}")
            
        if not success:
            print(f"⚠️ No se pudo obtener datos para liga {league_id} tras varios intentos.")

if __name__ == "__main__":
    seed()
