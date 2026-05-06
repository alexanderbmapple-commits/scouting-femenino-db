import json
import time
import random
from scrapling.fetchers import StealthyFetcher

class FotMobScraper:
    def __init__(self):
        # Configuramos el fetcher para que use una identidad de navegador real
        self.fetcher = StealthyFetcher()
        # Esta configuración ayuda a evitar la detección de bots en la API
        self.fetcher.configure(browser='chrome', platform='windows')
        
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.fotmob.com/",
            "Origin": "https://www.fotmob.com"
        }

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # EL SECRETO: Pausa humana obligatoria. 
        # Si vas muy rápido, te bloquean la IP de GitHub temporalmente.
        wait_time = random.uniform(3.0, 6.0)
        print(f"-> Esperando {wait_time:.2f}s para humanizar... (Partido: {match_id})")
        time.sleep(wait_time)
        
        response = self.fetcher.fetch(url, headers=self.headers)
        
        if response.status != 200:
            print(f"⚠️ Seguimos con 404/Block en {match_id}. FotMob está endureciendo el acceso.")
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
            print(f"❌ Error en JSON {match_id}: {e}")
            return None
