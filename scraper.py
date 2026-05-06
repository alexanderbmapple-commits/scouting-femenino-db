import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> CONFIGURANDO MOTOR ADAPTATIVO DE SCRA PLING", flush=True)
        # Creamos el fetcher base
        self.fetcher = Fetcher()
        # ACTIVAMOS EL SIGILO: Esto genera una huella digital de navegador real (Chrome/Windows)
        # Esto soluciona el "warning" que aparecía en tu log anterior.
        self.fetcher.configure(browser_family='chrome', auto_match=True)

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa aleatoria para no saturar la IP
        time.sleep(random.uniform(5.0, 9.0))
        
        # Headers que Scrapling usará para mimetizarse
        custom_headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            print(f">>> Scrapling Fetching ID: {match_id}...", flush=True)
            # Usamos el motor adaptativo configurado arriba
            response = self.fetcher.get(url, headers=custom_headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ¡LO TENEMOS! Scrapling ha burlado la seguridad.", flush=True)
                data = json.loads(response.text)
                return {
                    "general": data.get('general', {}),
                    "stats": data.get('content', {}).get('stats', {}),
                    "lineup": data.get('content', {}).get('lineup', {}),
                    "shotmap": data.get('content', {}).get('shotmap', {}),
                    "raw": data
                }
            
            return None
                
        except Exception as e:
            print(f">>> ERROR EN SCRA PLING: {str(e)}", flush=True)
            return None
