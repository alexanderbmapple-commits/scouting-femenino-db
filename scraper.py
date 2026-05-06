import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> ACTIVANDO MODO ADAPTATIVO DE SCRA PLING", flush=True)
        # 1. Inicializamos el fetcher
        self.fetcher = Fetcher()
        # 2. Usamos el argumento que tu log confirma que existe (Línea 34)
        # Esto activa el motor de evasión inteligente automáticamente
        self.fetcher.configure(adaptive=True)
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana más larga: FotMob tiene un firewall muy sensible
        wait_time = random.uniform(8.0, 15.0)
        print(f">>> Sigilo: Esperando {wait_time:.2f}s para ID {match_id}...", flush=True)
        time.sleep(wait_time)
        
        # En modo adaptive, Scrapling gestiona casi todo, pero forzamos el Referer
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            print(f">>> Scrapling Adaptive: Pidiendo datos de {match_id}...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ✅ ✅ ¡LO TENEMOS! Muro saltado con éxito.", flush=True)
                return json.loads(response.text)
            
            # Si da 404 aquí, es que la IP de GitHub está totalmente quemada
            elif response.status == 404:
                print(f"⚠️ El servidor sigue bloqueando la IP (404).", flush=True)
                
            return None
                
        except Exception as e:
            print(f">>> ERROR EN EL MOTOR: {str(e)}", flush=True)
            return None
