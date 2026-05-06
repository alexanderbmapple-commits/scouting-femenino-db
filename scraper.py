import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> INICIALIZANDO SCRA PLING (MODO ADAPTATIVO DIRECTO)", flush=True)
        # Inicializamos con el motor que tu log sugiere: 'adaptive'
        self.fetcher = Fetcher(auto_match=True) 
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana para no alertar al firewall de FotMob
        time.sleep(random.uniform(5.0, 10.0))
        
        # Forzamos los headers para que coincidan con una navegación real
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            print(f">>> Scrapling: Pidiendo datos del partido {match_id}...", flush=True)
            # Realizamos la petición
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ¡ÉXITO! Scrapling ha burlado el 404.", flush=True)
                data = json.loads(response.text)
                return {
                    "general": data.get('general', {}),
                    "stats": data.get('content', {}).get('stats', {}),
                    "lineup": data.get('content', {}).get('lineup', {}),
                    "shotmap": data.get('content', {}).get('shotmap', {}),
                    "raw": data
                }
            else:
                print(f"❌ Fallo con Status {response.status}. Intentando siguiente...", flush=True)
                return None
                
        except Exception as e:
            print(f">>> ERROR CRÍTICO EN MOTOR: {str(e)}", flush=True)
            return None
