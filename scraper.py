import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> CONFIGURACIÓN MANUAL DE SCRA PLING", flush=True)
        # Usamos Fetcher base para tener control total
        self.fetcher = Fetcher()
        # Configuramos el sigilo manualmente para evitar que use valores por defecto
        self.fetcher.configure(auto_match=True)
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana necesaria
        time.sleep(random.uniform(5.0, 8.0))
        
        # Forzamos headers REALES de un navegador
        # Es CRUCIAL que el Referer sea el mismo dominio de FotMob
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "Origin": "https://www.fotmob.com",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        try:
            print(f">>> Scrapling: Accediendo a {match_id} con Referer real...", flush=True)
            # Usamos .get() directamente con nuestros headers forzados
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ¡CONSEGUIDO! Datos capturados para {match_id}", flush=True)
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
