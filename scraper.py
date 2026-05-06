import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> ACTIVANDO NAVEGADOR SIGILOSO (ULTRA MODE)", flush=True)
        # 1. Iniciamos el fetcher base
        self.fetcher = Fetcher()
        # 2. Usamos la nueva sintaxis que nos pide el log (Línea 25 de tu captura)
        # 'headless=True' para que no use recursos visuales, pero con sigilo activado
        self.fetcher.configure(engine='playwright', headless=True)
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana obligatoria - FotMob odia las peticiones ultra rápidas
        time.sleep(random.uniform(7.0, 12.0))
        
        # En modo Playwright configurado así, Scrapling ya gestiona las huellas,
        # pero reforzamos el Referer para que parezca navegación orgánica.
        headers = {
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            print(f">>> Navegando sigilosamente a ID {match_id}...", flush=True)
            # Usamos .get() que ahora pasará por el motor Playwright configurado
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ✅ ✅ ¡MURO DESTRUIDO! Datos obtenidos.", flush=True)
                data = json.loads(response.text)
                content = data.get('content', {})
                return {
                    "general": data.get('general', {}),
                    "stats": content.get('stats', {}),
                    "lineup": content.get('lineup', {}),
                    "shotmap": content.get('shotmap', {}),
                    "raw": data
                }
            else:
                print(f"❌ FotMob resiste (Status {response.status}). Revisa la IP.", flush=True)
                return None
                
        except Exception as e:
            print(f">>> ERROR EN EL SALTO DEL MURO: {str(e)}", flush=True)
            return None
