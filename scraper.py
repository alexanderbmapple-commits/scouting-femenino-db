import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> ACTIVANDO MOTOR ADAPTATIVO DE SCRA PLING", flush=True)
        # Inicializamos el fetcher
        self.fetcher = Fetcher()
        # Usamos el argumento 'adaptive' que el sistema nos ha confirmado que acepta
        # Esto configura automáticamente la mejor estrategia contra firewalls
        self.fetcher.configure(engine='adaptive')

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa de seguridad para no quemar la IP de GitHub
        wait_time = random.uniform(5.0, 9.0)
        print(f">>> Sigilo Scrapling: Esperando {wait_time:.2f}s para ID {match_id}...", flush=True)
        time.sleep(wait_time)
        
        # Headers recomendados para que el motor adaptativo tenga éxito
        custom_headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            print(f">>> Scrapling procesando petición adaptativa...", flush=True)
            # El motor 'adaptive' gestiona internamente la evasión de bloqueos
            response = self.fetcher.get(url, headers=custom_headers)
            
            print(f">>> STATUS: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ¡CONSEGUIDO! Scrapling ha entrado en {match_id}", flush=True)
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
            print(f">>> ERROR EN MOTOR SCRA PLING: {str(e)}", flush=True)
            return None
