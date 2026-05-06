import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        self.fetcher = Fetcher()
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        # URL limpia para evitar el error 404 visto en los logs
        url = f"https://www.fotmob.com/matches/{match_id}"
        time.sleep(random.uniform(5.0, 8.0))
        
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "referer": "https://www.google.com/"
        }

        try:
            response = self.fetcher.get(url, headers=headers)
            print(f">>> MATCH {match_id} | STATUS: {response.status}", flush=True)
            
            if response.status == 200:
                script_content = response.css('script#__NEXT_DATA__::text').first()
                if script_content:
                    return json.loads(script_content)
            return None
        except Exception as e:
            print(f"❌ Error en match {match_id}: {e}", flush=True)
            return None

    def process_metrics(self, data):
        # Extraemos la rama de datos que nos interesa
        props = data.get('props', {}).get('pageProps', {})
        content = props.get('content', {})
        details = content.get('matchDetails', {})
        
        return {
            "match_id": details.get('id'),
            "home_team": details.get('homeTeam', {}).get('name'),
            "away_team": details.get('awayTeam', {}).get('name'),
            "match_time": details.get('matchTimeUTC'),
            "data_extra": json.dumps(content) # Guardamos el bloque importante
        }
