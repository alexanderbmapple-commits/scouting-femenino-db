import os
import json
from scraper import FotMobScraper
from supabase import create_client

# Función de limpieza para evitar errores de codificación (UnicodeEncodeError)
def clean_data(obj):
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(i) for i in obj]
    elif isinstance(obj, str):
        # Eliminamos caracteres de salto de línea raros (\u2028, \u2029) y normalizamos
        return obj.replace('\u2028', ' ').replace('\u2029', ' ').strip()
    return obj

# Configuración de clientes
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
scraper = FotMobScraper()

def run_pipeline():
    # 1. Buscar partidos finalizados no procesados
    # Nota: Asegúrate de que el .eq("processed", False) esté en tu lógica si aplica
    matches = supabase.table("matches").select("*").eq("status", "Finished").execute()

    for m in matches.data:
        print(f"Procesando match: {m['id']}")
        raw_data = scraper.get_match_data(m['id'])
        
        if raw_data:
            # LIMPIEZA: Eliminamos caracteres invisibles que rompen la conexión
            data = clean_data(raw_data)

            # 2. Guardar JSON bruto en Storage (Opcional, según tu captura)
            file_path = f"{m['id']}_raw.json"
            # supabase.storage.from_('match-raw-data').upload(file_path, json.dumps(data))

            # 3. Calcular métricas
            metrics = scraper.process_metrics(data)
            # Limpiamos también las métricas por si vienen con textos raros
            metrics = clean_data(metrics)

            # 4. Insertar/Actualizar en la base de datos
            # Aquí iría tu lógica de inserción masiva en player_match_stats
            
            # Marcar partido como procesado
            supabase.table("matches").update({"processed": True}).eq("id", m['id']).execute()
            print(f"Match {m['id']} procesado correctamente.")

if __name__ == "__main__":
    run_pipeline()
