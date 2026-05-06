import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> SCRA PLING: ACTIVANDO PROTOCOLO DE INFILTRACIÓN", flush=True)
        self.fetcher = Fetcher()
        # Usamos 'adaptive' porque es el que tu versión acepta sin errores
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        # CAMBIO DE URL: Usamos el endpoint que usan las webapps modernas para evitar firewalls
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa aleatoria MUY larga (estilo humano real)
        wait = random.uniform(12.0, 22.0)
        print(f">>> Sigilo: Pausa de {wait:.2f}s para no levantar sospechas...", flush=True)
        time.sleep(wait)
        
        # HEADERS DE NAVEGADOR DE ALTA FIDELIDAD
        # Estos headers son los que envía Chrome cuando "pre-carga" una página
        headers = {
            "authority": "www.fotmob.com",
            "accept": "*/*",
            "accept-language": "es-ES,es;q=0.9",
            "referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        try:
            print(f">>> Scrapling: Intentando acceso profundo a {match_id}...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ✅ ✅ ¡MURO DESTRUIDO! Datos capturados.", flush=True)
                return json.loads(response.text)
            
            # Si falla, probamos un último truco: añadir un parámetro aleatorio para engañar al Proxy de FotMob
            if response.status == 404:
                print(">>> La IP sigue marcada. Intentando bypass de túnel...", flush=True)
                bypass_url = f"{url}&_ts={int(time.time() * 1000)}"
                response = self.fetcher.get(bypass_url, headers=headers)
                if response.status == 200:
                    return json.loads(response.text)

            return None
                
        except Exception as e:
            print(f">>> ERROR: {str(e)}", flush=True)
            return None
