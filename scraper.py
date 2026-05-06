import json
import time
import random
from scrapling.fetchers import StealthyFetcher

class FotMobScraper:
    def __init__(self):
        self.fetcher = StealthyFetcher()
        # Headers para que FotMob nos trate como a un usuario real
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Cache-Control": "no-cache",
            "Referer": "https://www.fotmob.com/"
        }

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Añadimos un pequeño retardo aleatorio para no parecer un bot
        time.sleep(random.uniform(1.5, 3.0))
        
        print(f"-> Extrayendo datos del partido: {match_id}")
        
        # Pasamos los headers en la petición
        response = self.fetcher.fetch(url, headers=self.headers)
        
        if response.status != 200:
            print(f"⚠️ Error {response.status} en partido {match_id}. FotMob está bloqueando la petición.")
            return None

        try:
            data = json.loads(response.text)
            content = data.get('content', {})
            return {
                "general": data.get('general', {}),
                "stats": content.get('stats', {}),
                "lineup": content.get('lineup', {}),
                "shotmap": content.get('shotmap', {}),
                "raw": data
            }
        except Exception as e:
            print(f"❌ Error parseando JSON {match_id}: {e}")
            return None
