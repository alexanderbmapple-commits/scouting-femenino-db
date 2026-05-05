import requests
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Lista de ligas y temporadas que quieres
leagues = [10385, 209, 9812, 208, 212]
seasons = ["2023/2024", "2024/2025"]

def seed():
    for league_id in leagues:
        for season in seasons:
            # FotMob API interna para obtener calendario (simplificado)
            url = f"https://www.fotmob.com/api/leagues?id={league_id}&season={season}"
            response = requests.get(url).json()
            
            # Extraemos los partidos de las rondas/semanas
            matches = response.get('matches', {}).get('allMatches', [])
            
            for m in matches:
                data = {
                    "id": str(m['id']),
                    "league_id": league_id,
                    "season": season,
                    "home_team": m['home']['name'],
                    "away_team": m['away']['name'],
                    "match_date": m['status']['utcTime'],
                    "status": "Finished", # Como es backfill, ya terminaron
                    "processed": False
                }
                # Insertamos en Supabase (ignora si ya existe)
                supabase.table("matches").upsert(data).execute()
    print("Semillado completado. ¡Ya tienes la lista de trabajo!")

if __name__ == "__main__":
    seed()
