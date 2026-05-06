import os
import json
import io
import sys
from scraper import FotMobScraper
from supabase import create_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clean_data(obj):
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(i) for i in obj]
    elif isinstance(obj, str):
        return obj.replace('\u2028', ' ').replace('\u2029', ' ').strip()
    return obj

url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
scraper = FotMobScraper()

def run_pipeline():
    print(">>> INICIANDO PROCESO CON DOBLE RESPALDO", flush=True)
    
    try:
        # Forzamos el booleano explícito para evitar errores de tipo en la query
        response = supabase.table("matches").select("*").eq("processed", False).execute()
        matches = response.data
        print(f"Partidos pendientes encontrados: {len(matches)}", flush=True)
    except Exception as e:
        print(f"❌ Error Supabase inicial: {e}", flush=True)
        return

    datos_acumulados = []

    for m in matches:
        match_id = m['id']
        print(f"\n--- Procesando: {match_id} ---", flush=True)
        
        raw_data = scraper.get_match_data(match_id)
        
        if raw_data:
            try:
                metrics = scraper.process_metrics(raw_data)
                metrics = clean_data(metrics)
                metrics['match_id'] = match_id
                
                # Respaldo en archivo local
                datos_acumulados.append(metrics)
                with open("resultados_seguridad.json", "w", encoding="utf-8") as f:
                    json.dump(datos_acumulados, f, ensure_ascii=False, indent=4)
                
                # Inserción en Supabase
                supabase.table("player_match_stats").insert(metrics).execute()
                # Marcado como procesado
                supabase.table("matches").update({"processed": True}).eq("id", match_id).execute()
                print(f"✅ OK: {match_id} guardado.", flush=True)

            except Exception as e:
                print(f"⚠️ Fallo en match {match_id}: {e}", flush=True)
        else:
            print(f"❌ No se pudo scrapear {match_id}", flush=True)

if __name__ == "__main__":
    run_pipeline()
