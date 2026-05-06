import json
import time
import random
from scrapling.fetchers import StealthyFetcher

class FotMobScraper:
    def __init__(self):
        # Inicialización limpia para evitar el error de la captura anterior
        self.fetcher = StealthyFetcher()
        
        # HEADERS DE EVASIÓN: Miméticamos una petición AJAX real
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            # El secreto está en el Referer dinámico del partido
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        }

    def get_match_data(self, match_id):
        # Endpoint de la API
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # 1. REFERER DINÁMICO: Crucial para que no parezca un bot
        # Le decimos al servidor que venimos de la página de ese partido concreto
        self.headers["Referer"] = f"https://www.fotmob.com/es/matches/{match_id}"
        
        # 2. PAUSA HUMANA ALEATORIA LARGA:
        # El scraping de jugadoras es más agresivo, necesitamos más margen
        wait_time = random.uniform(5.0, 9.0)
        print(f"-> Sigilo activado: Esperando {wait_time:.2f}s antes de entrar al partido {match_id}")
        time.sleep(wait_time)
        
        try:
            response = self.fetcher.fetch(url, headers=self.headers)
            
            # Si detectamos un bloqueo (404 camuflado o 403)
            if response.status != 200:
                print(f"⚠️ Aviso: Status {response.status} en {match_id}. FotMob sospecha, saltando...")
                return None

            data = json.loads(response.text)
            content = data.get('content', {})
            
            # Retornamos la estructura para el scouting
            return {
                "general": data.get('general', {}),
                "stats": content.get('stats', {}),
                "lineup": content.get('lineup', {}),
                "shotmap": content.get('shotmap', {}),
                "raw": data
            }
            
        except Exception as e:
            print(f"❌ Error en la extracción del partido {match_id}: {e}")
            return None
