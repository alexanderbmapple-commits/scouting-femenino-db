import json
from scrapling import Selector
from scrapling.fetchers import StealthyFetcher

class FotMobScraper:
    def __init__(self):
        # Inicializamos el fetcher con capacidades de bypass
        self.fetcher = StealthyFetcher()

    def get_match_data(self, match_id):
        """
        Obtiene los detalles completos de un partido (alineaciones, stats, disparos)
        utilizando el endpoint de la API de FotMob.
        """
        # Usamos el endpoint de la API que devuelve JSON puro
        url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
        print(f"-> Extrayendo datos del partido: {match_id}")
        
        response = self.fetcher.fetch(url)
        
        if response.status != 200:
            print(f"⚠️ Error {response.status} al obtener detalles del partido {match_id}")
            return None

        try:
            # Cargamos el texto de la respuesta como un diccionario de Python
            data = json.loads(response.text)
            
            # Estructura organizada para que el main_orchestrator la procese fácilmente
            content = data.get('content', {})
            return {
                "general": data.get('general', {}),
                "stats": content.get('stats', {}),
                "lineup": content.get('lineup', {}),
                "shotmap": content.get('shotmap', {}),
                "raw": data  # Guardamos todo el JSON por si necesitamos métricas extra luego
            }
        except Exception as e:
            print(f"❌ Error parseando el JSON del partido {match_id}: {e}")
            return None

    def process_metrics(self, data):
        """
        Lógica para procesar métricas avanzadas (Posición Dinámica, etc.)
        Si tu main_orchestrator ya hace esto, puedes dejarlo como un pasamanos.
        """
        if not data:
            return None
        
        # Aquí puedes añadir cálculos personalizados si fuera necesario
        return data
