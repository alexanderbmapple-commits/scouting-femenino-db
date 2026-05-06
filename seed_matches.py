import os
from scrapling import StealthyFetcher
from supabase import create_client

# Configuración de conexión con limpieza de "tuberías"
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)

# Inicializamos el fetcher de Scrapling (el "disfraz" profesional)
fetcher = StealthyFetcher()

leagues = [10385, 209, 9812, 208, 212]
seasons = ["2023/2024", "2024/2025"]

def seed():
    for league_id in leagues:
        for season in seasons:
            target_url = f"https://www.fotmob.com/api/leagues?id={league_id}&season={season}"
            print(f"Scrapeando sin muros: {target_url}")
            
            # Usamos Scrapling para saltar el bloqueo
            page = fetcher.fetch(target_url)
            
            if page.status != 200:
                print(f"Error {page.status} en {league_id}. Probando siguiente...")
                continue

            try:
                # Scrapling devuelve la respuesta en .json_content si es una API
                data = page.json()
                matches = data.get('matches', {}).get('allMatches', [])
                
                if not matches:
                    print(f"No se encontraron partidos para liga {league_id}")
                    continue

                for m in matches:
                    match_data = {
                        "id": str(m['id']),
                        "league_id": league_id,
                        "season": season,
                        "home_team": m['home']['name'],
                        "away_team": m['away']['name'],
                        "match_date": m['status']['utcTime'],
                        "status": "Finished",
                        "processed": False
                    }
                    # Insertamos en Supabase (upsert para no duplicar)
                    supabase.table("matches").upsert(match_data).execute()
                
                print(f"Liga {league_id} semillada con éxito.")

            except Exception as e:
                print(f"Error procesando datos de {league_id}: {e}")

if __name__ == "__main__":
    seed()
