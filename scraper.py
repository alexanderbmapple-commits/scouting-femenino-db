import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> USANDO ARTILLERÍA PESADA: STEALTH BROWSER", flush=True)
        self.fetcher = Fetcher()
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        # URL que confirmamos que da Status 200
        url = f"https://www.fotmob.com/es/matches/{match_id}"
        
        # Pausa aleatoria para evitar bloqueos
        time.sleep(random.uniform(5.0, 10.0))
        
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "referer": "https://www.google.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        try:
            print(f">>> Intentando acceso orgánico al partido {match_id}...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS RECIBIDO: {response.status}", flush=True)
            
            if response.status == 200:
                # USAMOS SELECTOR CSS (Más fiable que Regex)
                # Buscamos el script que tiene el ID __NEXT_DATA__
                script_content = response.css('script#__NEXT_DATA__::text').first()
                
                if script_content:
                    all_data = json.loads(script_content)
                    # Navegamos por la estructura de FotMob
                    props = all_data.get('props', {}).get('pageProps', {})
                    content = props.get('content', {})
                    match_details = content.get('matchDetails', {})
                    
                    if match_details:
                        print(f"✅ ✅ ✅ ¡DATOS EXTRAÍDOS! (ID: {match_id})", flush=True)
                        return content # Devolvemos 'content' porque suele traer más info útil
                
                print(f"⚠️ No se encontró el bloque de datos en el HTML del match {match_id}", flush=True)
            
            return None
                
        except Exception as e:
            print(f">>> ERROR EN MOTOR SCRAPER: {str(e)}", flush=True)
            return None

    def process_metrics(self, data):
        """
        Esta función procesa el JSON bruto y lo convierte en un formato 
        listo para tu tabla 'player_match_stats' en Supabase.
        """
        # Extraemos lo básico para que la inserción no falle
        details = data.get('matchDetails', {})
        
        # Ejemplo de mapeo de campos (Ajusta según tus columnas en Supabase)
        metrics = {
            "match_id": details.get('matchId'),
            "match_date": details.get('matchTimeUTC'),
            "home_team": details.get('homeTeam', {}).get('name'),
            "away_team": details.get('awayTeam', {}).get('name'),
            "raw_json": json.dumps(data) # Guardamos todo el JSON por si acaso
        }
        
        return metrics
