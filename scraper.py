import json
import time
import random
import requests

class FotMobScraper:
    def __init__(self):
        print("DEBUG: Inicializando FotMobScraper con Requests")
        self.session = requests.Session()
        
    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Bajamos la pausa a un rango menor para testear rápido
        wait_time = random.uniform(2.0, 4.0)
        print(f"DEBUG: Esperando {wait_time:.2f}s antes de pedir ID {match_id}...")
        time.sleep(wait_time)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "Origin": "https://www.fotmob.com"
        }
        
        try:
            print(f"DEBUG: Lanzando petición a: {url}")
            response = self.session.get(url, headers=headers, timeout=15)
            
            print(f"DEBUG: Respuesta recibida. Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"⚠️ Error de servidor en {match_id}: {response.status_code}")
                return None

            data = response.json()
            print(f"✅ JSON parseado correctamente para {match_id}")
            
            content = data.get('content', {})
            return {
                "general": data.get('general', {}),
                "stats": content.get('stats', {}),
                "lineup": content.get('lineup', {}),
                "shotmap": content.get('shotmap', {}),
                "raw": data
            }
            
        except Exception as e:
            print(f"❌ Error físico en la petición: {str(e)}")
            return None
