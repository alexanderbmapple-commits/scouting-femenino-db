import json
import time
import random
import re
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> USANDO ARTILLERÍA PESADA: STEALTH BROWSER", flush=True)
        self.fetcher = Fetcher()
        # Intentamos forzar el modo 'adaptive' con el motor stealth 
        # para que use Playwright por debajo si está instalado
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        # Intentamos una URL alternativa que a veces no está tan protegida
        url = f"https://www.fotmob.com/es/match/{match_id}"
        
        # Pausa MUY larga. Si la IP está marcada, ir rápido solo empeora el ban.
        time.sleep(random.uniform(15.0, 25.0))
        
        # Cambiamos el referer a Google para simular tráfico de búsqueda orgánico
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "referer": "https://www.google.com/",
            "upgrade-insecure-requests": "1"
        }

        try:
            print(f">>> Intentando acceso orgánico al partido {match_id}...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ✅ ✅ ¡LO LOGRAMOS! El HTML ha respondido.", flush=True)
                match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
                if match:
                    all_data = json.loads(match.group(1))
                    props = all_data.get('props', {}).get('pageProps', {})
                    return props.get('content', {}).get('matchDetails', {})
            
            return None
                
        except Exception as e:
            print(f">>> ERROR EN MOTOR: {str(e)}", flush=True)
            return None
