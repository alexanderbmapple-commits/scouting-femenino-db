import os
from scraper import FotMobScraper
from supabase import create_client
# Antigravity se usa para orquestar los reintentos en el workflow

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
scraper = FotMobScraper()

def run_pipeline():
    # 1. Buscar partidos finalizados no procesados
    matches = supabase.table("matches").select("*").eq("status", "Finished").eq("processed", False).execute()
    
    for m in matches.data:
        print(f"Procesando match: {m['id']}")
        data = scraper.get_match_data(m['id'])
        
        if data:
            # 2. Guardar JSON bruto en Storage (Ahorra espacio en DB)
            file_path = f"{m['id']}_raw.json"
            # supabase.storage.from_('match-raw-data').upload(file_path, json.dumps(data))
            
            # 3. Calcular métricas y actualizar DB
            metrics = scraper.process_metrics(data)
            
            # 4. Insertar en player_match_stats y marcar como procesado
            # (Lógica de inserción masiva aquí)
            supabase.table("matches").update({"processed": True}).eq("id", m['id']).execute()

if __name__ == "__main__":
    run_pipeline()