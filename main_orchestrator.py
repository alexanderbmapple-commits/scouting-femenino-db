import os
import json
from scraper import FotMobScraper
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
scraper = FotMobScraper()

def run_pipeline():
    # 1. Obtenemos pendientes
    matches = supabase.table("matches").select("*").eq("processed", False).execute()
    acumulado = []

    for m in matches.data:
        match_id = m['id']
        raw_data = scraper.get_match_data(match_id)
        
        if raw_data:
            metrics = scraper.process_metrics(raw_data)
            acumulado.append(metrics)
            
            # Guardado inmediato en archivo local (Seguridad técnica)
            with open("temp_results.json", "w", encoding="utf-8") as f:
                json.dump(acumulado, f, ensure_ascii=False, indent=4)

            # Intento de subida a Supabase
            try:
                supabase.table("player_match_stats").insert(metrics).execute()
                supabase.table("matches").update({"processed": True}).eq("id", match_id).execute()
                print(f"✅ Guardado en DB y Archivo: {match_id}")
            except Exception as e:
                print(f"⚠️ Error en DB (pero guardado en archivo): {e}")

if __name__ == "__main__":
    run_pipeline()
