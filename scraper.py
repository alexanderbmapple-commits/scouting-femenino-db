import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> MOTOR SCRA PLING: MODO CAMALEÓN ACTIVADO", flush=True)
        # No guardamos el fetcher en el init para forzar uno nuevo cada vez
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa aleatoria MUY agresiva (necesitamos que el firewall se "olvide" de nosotros)
        time.sleep(random.uniform(10.0, 20.0))
        
        try:
            # CREAMOS UN FETCH_ER NUEVO PARA CADA PARTIDO
            # Esto genera una huella digital (Fingerprint) totalmente distinta cada vez
            fetcher = Fetcher(auto_match=True)
            
            # Usamos el motor 'adaptive' que el sistema nos recomendó en el log anterior
            fetcher.configure(adaptive=True)
            
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
                "X-Requested-With": "XMLHttpRequest",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }

            print(f">>> Intentando ID {match_id} con identidad nueva...", flush=True)
            response = fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ✅ ✅ ¡MURO SALTADO! Datos de {match_id} capturados.", flush=True)
                return json.loads(response.text)
            
            elif response.status == 404:
                print(f"❌ La IP de GitHub sigue quemada para el ID {match_id}.", flush=True)
                
            return None
                
        except Exception as e:
            print(f">>> ERROR EN IDENTIDAD: {str(e)}", flush=True)
            return None
