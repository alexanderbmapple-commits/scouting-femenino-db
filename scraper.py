import json
import time
import random
import requests

class FotMobScraper:
    def __init__(self):
        # Usamos una sesión de requests para mantener cookies y headers consistentes
        self.session = requests.Session()
        
    def get_match_data(self, match_id):
        # 1. Endpoint de la API
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # 2. HEADERS TOTALMENTE REALISTAS
        # He cambiado el User-Agent a uno más reciente y añadí headers de control
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "Origin": "https://www.fotmob.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache"
        }
        
        # 3. PAUSA HUMANA (Entre 4 y 8 segundos)
        wait_time = random.uniform(4.0, 8.0)
        print(f"-> Sigilo Total: Esperando {wait_time:.2f}s para partido {match_id}...")
        time.sleep(wait_time)
        
        try:
            # Realizamos la petición con la sesión
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"⚠️ Seguimos bloqueados: Status {response.status_code} en ID {match_id}")
                return None

            data = response.json()
            content = data.get('content', {})
            
            print(f"✅ ¡ÉXITO! Datos obtenidos para el partido {match_id}")
            
            return {
                "general": data.get('general', {}),
                "stats": content.get('stats', {}),
                "lineup": content.get('lineup', {}),
                "shotmap": content.get('shotmap', {}),
                "raw": data
            }
            
        except Exception as e:
            print(f"❌ Error crítico en partido {match_id}: {e}")
            return None
