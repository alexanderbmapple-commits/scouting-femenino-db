import json
import time
import random
from scrapling.fetchers import StealthyFetcher

class FotMobScraper:
    def __init__(self):
        # Inicializamos el fetcher sin argumentos que den error
        self.fetcher = StealthyFetcher()
        
        # Configuramos los headers manualmente para simular un navegador real
        # Esto sustituye al .configure() que fallaba en tu captura de pantalla
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.fotmob.com/",
            "Origin": "https://www.fotmob.com",
            "X-Requested-With": "XMLHttpRequest"
        }

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        
        # Pausa humana aleatoria para evitar que nos marquen como bot
        # Procesar 700 partidos requiere paciencia para no ser bloqueados
        wait_time = random.uniform(3.5, 6.0)
        print(f"-> Humanizando... Esperando {wait_time:.2f}s (Partido: {match_id})")
        time.sleep(wait_time)
        
        response = self.fetcher.fetch(url, headers=self.headers)
        
        # Si FotMob nos da un 404/403, devolvemos None para que el orquestador siga con el siguiente
        if response.status != 200:
            print(f"⚠️ Aviso: Status {response.status} en {match_id}. FotMob está limitando el acceso.")
            return None

        try:
            data = json.loads(response.text)
            content = data.get('content', {})
            return {
                "general": data.get('general', {}),
                "stats": content.get('stats', {}),
                "lineup": content.get('lineup', {}),
                "shotmap": content.get('shotmap', {}),
                "raw": data
            }
        except Exception as e:
            print(f"❌ Error parseando JSON {match_id}: {e}")
            return None
