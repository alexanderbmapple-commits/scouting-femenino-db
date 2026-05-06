import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> ACTIVANDO NAVEGADOR REAL (PLAYWRIGHT) CON SCRA PLING", flush=True)
        # El motor 'playwright' es el que realmente salta los muros más duros
        self.fetcher = Fetcher(engine='playwright')
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana aleatoria
        time.sleep(random.uniform(6.0, 10.0))
        
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            print(f">>> Scrapling (Browser Mode): Navegando a ID {match_id}...", flush=True)
            # Fetch con navegador real
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ✅ ¡MURO SALTADO! Datos obtenidos para {match_id}", flush=True)
                # En modo playwright, a veces el texto necesita un pequeño ajuste
                try:
                    data = json.loads(response.text)
                except:
                    # Si el primer intento falla, limpiamos posibles etiquetas HTML si las hubiera
                    data = json.loads(response.body)
                
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
            print(f">>> ERROR EN MOTOR NAVEGADOR: {str(e)}", flush=True)
            return None
