import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> ACTIVANDO MOTOR ULTRA-SIGILO (CURL-CFFI)", flush=True)
        self.fetcher = Fetcher()
        # Usamos el motor curl_cffi para imitar la huella TLS de Chrome 124
        # Esto es lo más avanzado que existe para saltar bloqueos de IP
        self.fetcher.configure(engine='curl_cffi', impersonate='chrome124')

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa aleatoria para evitar patrones de bot
        time.sleep(random.uniform(8.0, 14.0))
        
        # Forzamos headers de un usuario real navegando
        headers = {
            "Accept": "*/*",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        try:
            print(f">>> Intentando ID {match_id} con huella digital Chrome...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ✅ ✅ ¡MURO SALTADO! Datos de {match_id} obtenidos.", flush=True)
                return json.loads(response.text)
            
            elif response.status == 404:
                # Si esto sigue dando 404, añadimos un pequeño truco de URL
                print(">>> Reintentando con bypass de cache...", flush=True)
                bypass_url = f"{url}&_={int(time.time())}"
                response = self.fetcher.get(bypass_url, headers=headers)
                if response.status == 200:
                    return json.loads(response.text)

            return None
                
        except Exception as e:
            print(f">>> ERROR EN MOTOR: {str(e)}", flush=True)
            return None
