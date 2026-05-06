import os
import json
import io
import sys
from scraper import FotMobScraper
from supabase import create_client

# Forzamos la salida estándar a UTF-8 para evitar errores de caracteres en los logs de GitHub
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def clean_data(obj):
    """Limpia caracteres invisibles o problemáticos que rompen la conexión con la DB."""
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(i) for i in obj]
    elif isinstance(obj, str):
        return obj.replace('\u2028', ' ').replace('\u2029', ' ').strip()
    return obj

# Inicialización de clientes
url = os.getenv("SUPABASE_URL", "").strip()
key = os.getenv("SUPABASE_KEY", "").strip()
supabase = create_client(url, key)
scraper = FotMobScraper()

def run_pipeline():
    print(">>> INICIANDO PROCESO DE EXTRACCIÓN CON DOBLE RESPALDO", flush=True)
    
    # 1. Obtener los partidos que aún no han sido procesados
    try:
        response = supabase.table("matches").select("*").eq("processed", False).execute()
        matches = response.data
        print(f"Total de partidos pendientes: {len(matches)}", flush=True)
    except Exception as e:
        print(f"❌ Error al conectar con Supabase: {e}", flush=True)
        return

    # Lista para acumular resultados en caso de que necesitemos el archivo local
    datos_acumulados = []

    for m in matches:
        match_id = m['id']
        print(f"\n--- Trabajando en Match ID: {match_id} ---", flush=True)
        
        # 2. Extraer datos del scraper
        raw_data = scraper.get_match_data(match_id)
        
        if raw_data:
            # 3. Procesar y limpiar métricas
            try:
                metrics = scraper.process_metrics(raw_data)
                metrics = clean_data(metrics)
                metrics['match_id'] = match_id # Aseguramos el vínculo
                
                # AÑADIR AL ARCHIVO LOCAL DE SEGURIDAD
                datos_acumulados.append(metrics)
                with open("resultados_seguridad.json", "w", encoding="utf-8") as f:
                    json.dump(datos_acumulados, f, ensure_ascii=False, indent=4)
                
                # 4. SUBIDA A SUPABASE
                print(f" -> Intentando subir a tabla 'player_match_stats'...", flush=True)
                supabase.table("player_match_stats").insert(metrics).execute()

                # 5. MARCAR COMO COMPLETADO
                supabase.table("matches").update({"processed": True}).eq("id", match_id).execute()
                print(f"✅ ÉXITO: Partido {match_id} guardado y marcado.", flush=True)

            except Exception as e:
                print(f"⚠️ Error procesando datos de {match_id}: {e}", flush=True)
                print(f"Nota: Los datos se han guardado en el archivo local de seguridad.", flush=True)
        else:
            print(f"❌ No se pudo obtener información para el partido {match_id}", flush=True)

    print("\n>>> PIPELINE FINALIZADO", flush=True)

if __name__ == "__main__":
    run_pipeline()
