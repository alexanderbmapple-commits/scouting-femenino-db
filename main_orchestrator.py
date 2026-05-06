import os
import json
import io
from scraper import FotMobScraper
from supabase import create_client
import sys

# Forzamos la salida estándar a UTF-8 para evitar errores en GitHub Actions
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clean_data(obj):
    """Función de limpieza para evitar errores de codificación y caracteres invisibles."""
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(i) for i in obj]
    elif isinstance(obj, str):
        return obj.replace('\u2028', ' ').replace('\u2029', ' ').strip()
    return obj

# Configuración de clientes
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
scraper = FotMobScraper()

def run_pipeline():
    print(">>> INICIANDO PIPELINE DE EXTRACCIÓN Y GUARDADO DIRECTO", flush=True)
    
    # 1. Buscamos partidos pendientes en la tabla 'matches'
    # Nota: Asegúrate de que la columna 'processed' existe en tu tabla
    try:
        response = supabase.table("matches").select("*").eq("processed", False).execute()
        matches = response.data
    except Exception as e:
        print(f"❌ Error al consultar partidos pendientes: {e}")
        return

    print(f"Se han encontrado {len(matches)} partidos pendientes.", flush=True)

    for m in matches:
        match_id = m['id']
        print(f"\n--- Procesando match: {match_id} ---", flush=True)
        
        try:
            # 2. Obtenemos los datos brutos del scraper
            raw_data = scraper.get_match_data(match_id)
            
            if raw_data:
                # Limpiamos los datos de caracteres raros
                data = clean_data(raw_data)
                
                # 3. Procesamos las métricas específicas
                # (Asumiendo que process_metrics devuelve un diccionario con las estadísticas)
                metrics = scraper.process_metrics(data)
                metrics = clean_data(metrics)
                
                # Añadimos el ID del partido a las métricas para la relación en la DB
                metrics['match_id'] = match_id 

                # 4. INSERTAR EN SUPABASE (Tabla de destino de estadísticas)
                print(f" -> Intentando insertar en Supabase...", flush=True)
                supabase.table("player_match_stats").insert(metrics).execute()

                # 5. MARCAR PARTIDO COMO PROCESADO
                # Esto es vital para que si el script se corta, no repita el trabajo
                supabase.table("matches").update({"processed": True}).eq("id", match_id).execute()
                print(f"✅ Match {match_id} completado e insertado.", flush=True)
                
            else:
                print(f"⚠️ Salto de partido {match_id}: No se recibió respuesta de FotMob.", flush=True)

        except Exception as e:
            print(f"❌ Error crítico en el match {match_id}: {str(e)}", flush=True)
            continue # Pasa al siguiente partido a pesar del error

if __name__ == "__main__":
    run_pipeline()
