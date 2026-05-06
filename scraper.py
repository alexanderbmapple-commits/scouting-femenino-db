import json
import time
import random
import re
from scrapling import Fetcher

class FotMobScraper:
    def __init__(self):
        print(">>> MOTOR DE EXTRACCIÓN HTML ACTIVADO", flush=True)
        self.fetcher = Fetcher()
        self.fetcher.configure(adaptive=True)

    def get_match_data(self, match_id):
        # Usamos la URL que ya sabemos que funciona según tu última captura
        url = f"https://www.fotmob.com/es/matches/{match_id}"
        
        # Mantenemos el sigilo pero bajamos un poco la pausa ya que el 200 es estable
        time.sleep(random.uniform(5.0, 10.0))
        
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "referer": "https://www.google.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        try:
            print(f">>> Leyendo HTML del partido {match_id}...", flush=True)
            response = self.fetcher.get(url, headers=headers)
            
            if response.status == 200:
                # El JSON está encerrado en <script id="__NEXT_DATA__" ...>...</script>
                # Usamos un regex más robusto por si hay espacios o saltos de línea
                pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
                match = re.search(pattern, response.text, re.DOTALL)
                
                if match:
                    print("✅ Bloque de datos localizado. Procesando...", flush=True)
                    raw_json = match.group(1).strip()
                    all_data = json.loads(raw_json)
                    
                    # Estructura típica de Next.js en FotMob:
                    # props -> pageProps -> content -> matchDetails
                    props = all_data.get('props', {}).get('pageProps', {})
                    match_details = props.get('content', {}).get('matchDetails', {})
                    
                    if match_details:
                        return match_details
                    else:
                        print("⚠️ El JSON se leyó pero 'matchDetails' está vacío.", flush=True)
                else:
                    print("❌ Error: No se encontró la etiqueta __NEXT_DATA__.", flush=True)
            else:
                print(f"❌ Error de red: Status {response.status}", flush=True)
            
            return None
                
        except Exception as e:
            print(f">>> ERROR DE EXTRACCIÓN: {str(e)}", flush=True)
            return None
