import json
import time
import random
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> REVOLVIENDO AL MODO DE ÉXITO (HTML-ACCESS)", flush=True)
        self.fetcher = Fetcher()
        # Mantenemos 'adaptive' porque es el que tu versión de Scrapling acepta sin errores
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        # La URL que nos dio el 200 en la Captura de pantalla 2026-05-06 a las 12.16.48.jpg
        url = f"https://www.fotmob.com/es/matches/{match_id}"
        
        # Pausa de seguridad para mantener el acceso
        time.sleep(random.uniform(7.0, 12.0))
        
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "referer": "https://www.google.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        try:
            print(f">>> Intentando acceso al partido {match_id}...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS: {response.status}", flush=True)
            
            if response.status == 200:
                print("✅ Conexión establecida. Extrayendo datos...", flush=True)
                
                # En lugar de Regex, usamos el selector de Scrapling para buscar el script
                # Esto es mucho más seguro y menos propenso a fallos
                script_tag = response.css('script#__NEXT_DATA__::text').first()
                
                if script_tag:
                    data = json.loads(script_tag)
                    # Navegamos por la estructura de FotMob
                    props = data.get('props', {}).get('pageProps', {})
                    match_details = props.get('content', {}).get('matchDetails', {})
                    
                    if match_details:
                        print(f"✅ Datos de {match_id} extraídos correctamente.", flush=True)
                        return match_details
                
                print("⚠️ No se pudo encontrar el bloque __NEXT_DATA__ en el HTML.", flush=True)
            
            return None
                
        except Exception as e:
            print(f">>> ERROR EN PROCESO: {str(e)}", flush=True)
            return None
