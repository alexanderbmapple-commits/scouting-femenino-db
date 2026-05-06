import json
import time
import random
import re
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> CAMBIO DE ESTRATEGIA: EXTRACCIÓN DESDE HTML", flush=True)
        self.fetcher = Fetcher()
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        # IMPORTANTE: Ya no llamamos a /api/matchDetails, sino a la URL visual del partido
        url = f"https://www.fotmob.com/es/matches/{match_id}"
        
        time.sleep(random.uniform(5.0, 10.0))
        
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,chrome-124",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        try:
            print(f">>> Cargando página HTML del partido {match_id}...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            print(f">>> STATUS HTML: {response.status}", flush=True)
            
            if response.status == 200:
                # Buscamos el JSON oculto en la etiqueta <script id="__NEXT_DATA__">
                # Scrapling nos permite buscar en el texto de la respuesta
                match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
                
                if match:
                    print(f"✅ ¡JSON ENCONTRADO DENTRO DEL HTML!", flush=True)
                    all_data = json.loads(match.group(1))
                    # Navegamos por el diccionario de Next.js para llegar a los datos del partido
                    props = all_data.get('props', {}).get('pageProps', {})
                    return props.get('content', {}).get('matchDetails', {})
                else:
                    print("❌ No se encontró el bloque de datos en el HTML.", flush=True)
            
            return None
                
        except Exception as e:
            print(f">>> ERROR CRÍTICO: {str(e)}", flush=True)
            return None
