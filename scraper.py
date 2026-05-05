import json
from scrapling import Selector
from scrapling.fetchers import StealthyFetcher

class FotMobScraper:
    def __init__(self):
        self.fetcher = StealthyFetcher()

    def get_match_data(self, match_id):
        url = f"https://www.fotmob.com/matches/{match_id}"
        response = self.fetcher.get(url)
        selector = Selector(response.text)
        
        # Extracción del JSON embebido
        raw_json = selector.css('script#__NEXT_DATA__::text').first()
        if not raw_json:
            return None
            
        data = json.loads(raw_json)
        props = data.get('props', {}).get('pageProps', {})
        content = props.get('content', {})
        
        return {
            "general": props.get('general', {}),
            "stats": content.get('stats', {}),
            "lineup": content.get('lineup', {}),
            "shotmap": content.get('shotmap', {}),
            "raw": data # Para guardar en el bucket
        }

    def process_metrics(self, data):
        # Lógica de Posición Dinámica y Métricas Pro
        lineup = data['lineup'].get('lineup', [])
        # Aquí se implementaría la lógica de coordenadas para el Packing
        # Por brevedad, simulamos el retorno de las métricas calculadas
        metrics = {
            "packing": self._calculate_packing(data),
            "opp_half_rec": self._calculate_recoveries(data),
            "dynamic_pos": self._infer_position(data)
        }
        return metrics

    def _calculate_packing(self, data):
        # Lógica: Pases que rompen líneas basadas en coordenadas iniciales del rival
        return 0 # Placeholder funcional

    def _infer_position(self, data):
        # Análisis de "average positions" para re-categorizar jugadora
        return "Winger"