import json
import time
import random
from scrapling import StealthyFetcher

class FotMobScraper:
    def __init__(self):
        print(">>> CARGANDO SCRA PLING STEALTH MODE", flush=True)
        # El StealthyFetcher ya es, por definición, el motor adaptativo
        # No necesita .configure() para activarse en esta versión
        self.fetcher = StealthyFetcher()
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana para evitar bloqueos de IP en GitHub
        time.sleep(random.uniform(5.0, 8.0))
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            print(f">>> Scrapling: Intentando acceso sigiloso a {match_id}...", flush=True)
            # Fetch directo usando la tecnología Stealth de Scrapling
            response = self.fetcher.fetch(url, headers=headers)
            
            print(f">>> STATUS: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ¡BINGO! Scrapling ha burlado la seguridad.", flush=True)
                data = json.loads(response.text)
                content = data.get('content', {})
                return {
                    "general": data.get('general', {}),
                    "stats": content.get('stats', {}),
                    "lineup": content.get('lineup', {}),
                    "shotmap": content.get('shotmap', {}),
                    "raw": data
                }
            
            return None
                
        except Exception as e:
            print(f">>> ERROR EN MOTOR: {str(e)}", flush=True)
            return None
