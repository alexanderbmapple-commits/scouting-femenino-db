import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> ACTIVANDO MOTOR SCALING STEALTH", flush=True)
        # Inicializamos el Fetcher que gestiona automáticamente 
        # las huellas digitales del navegador para evitar bloqueos
        self.fetcher = Fetcher()

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Humanización obligatoria para no quemar la IP de GitHub
        wait_time = random.uniform(5.0, 8.0)
        print(f">>> Sigilo Scrapling: Esperando {wait_time:.2f}s para ID {match_id}...", flush=True)
        time.sleep(wait_time)
        
        # Scrapling permite enviar headers que parecen venir de una navegación real
        custom_headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": f"https://www.fotmob.com/es/matches/{match_id}",
            "Origin": "https://www.fotmob.com",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            # Usamos el método fetch de Scrapling que por defecto intenta 
            # evadir detecciones básicas de bots
            response = self.fetcher.get(url, headers=custom_headers)
            
            print(f">>> RESPUESTA SCRA PLING: {response.status}", flush=True)
            
            if response.status == 200:
                print(f"✅ ¡ÉXITO! Datos capturados por Scrapling para {match_id}", flush=True)
                data = json.loads(response.text)
                content = data.get('content', {})
                return {
                    "general": data.get('general', {}),
                    "stats": content.get('stats', {}),
                    "lineup": content.get('lineup', {}),
                    "shotmap": content.get('shotmap', {}),
                    "raw": data
                }
            
            elif response.status == 404:
                print(f"⚠️ El servidor sigue detectando el bot (404). Reintentando con cabeceras de App...", flush=True)
                # Intento extra cambiando una cabecera clave
                custom_headers["User-Agent"] = "com.fotmob.android/1.0"
                response = self.fetcher.get(url, headers=custom_headers)
                if response.status == 200:
                    return json.loads(response.text)

            return None
                
        except Exception as e:
            print(f">>> ERROR EN SCRA PLING: {str(e)}", flush=True)
            return None
