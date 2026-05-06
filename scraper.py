import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> ACTIVANDO MODO ADAPTATIVO (COMPATIBLE v0.3)", flush=True)
        # Inicializamos el fetcher sin argumentos para evitar el ValueError
        self.fetcher = Fetcher()
        # Usamos 'adaptive' que es el argumento que tu log confirma como válido
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana real para que el firewall no se despierte
        wait_time = random.uniform(10.0, 18.0)
        print(f">>> Sigilo: Esperando {wait_time:.2f}s...", flush=True)
        time.sleep(wait_time)
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        try:
            print(f">>> Scrapling Adaptive: Intentando ID {match_id}...", flush=True)
            # El modo adaptive gestionará la huella digital por nosotros
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ¡MURO SALTADO! Datos de {match_id} capturados.", flush=True)
                return json.loads(response.text)
            
            elif response.status == 404:
                # TRUCO FINAL: Si el 404 persiste, intentamos la URL móvil
                print(">>> Reintentando con cabecera de App móvil...", flush=True)
                headers["User-Agent"] = "FotMob/1.0 (iPhone; iOS 15.0; Scale/3.00)"
                response = self.fetcher.get(url, headers=headers)
                if response.status == 200:
                    return json.loads(response.text)

            return None
                
        except Exception as e:
            print(f">>> ERROR EN PROCESO: {str(e)}", flush=True)
            return None
