IMAGE_CSV_PATH = "./encabezados.csv"
OUTPUT_DIR = "./api_outputs"


MODEL = "gpt-5-mini"
PROMPT = "EN BASE AL TEXTO DE LA IMAGEN DEVUELVE ÚNICAMENTE UN JSON CON LAS LLAVES: 'tipo' (ASISTENCIA O VOTACIÓN), 'fecha', 'hora', 'asunto'; SI ALGÚN VALOR NO SE IDENTIFICA PON 'null'; TODO EL CONTENIDO DEBE IR EN MAYÚSCULAS; NO AGREGUES COMENTARIOS NI TEXTO ADICIONAL."

NUM_WORKERS = 16  # Número de hilos para procesamiento paralelo
MAX_RETRIES = 3  # Número máximo de reintentos por imagen
RETRY_DELAY_BASE = 5  # Segundos de espera base entre reintentos (se multiplica exponencialmente)

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import pandas as pd
from utils_openai_ocr import process_image_ocr

# Lock para escritura segura en consola
print_lock = Lock()


def safe_print(message):
    """Imprime de forma segura en entorno multi-thread"""
    with print_lock:
        print(message)


def procesar_imagen(row_data, idx, total):
    """
    Procesa una imagen individual con reintentos

    Args:
        row_data: dict con la información de la fila (file_name, json_name, image_path)
        idx: índice actual
        total: total de imágenes a procesar

    Returns:
        tuple: (success: bool, file_name: str, error_msg: str or None)
    """
    file_name = row_data["file_name"]
    image_path = row_data["image_path"]
    json_name = row_data["json_name"]

    # Construir la ruta de salida
    output_path = os.path.join(OUTPUT_DIR, json_name)

    # Verificar que la imagen existe
    if not os.path.exists(image_path):
        safe_print(f"[{idx}/{total}] SALTADO - No existe: {image_path}")
        return (False, file_name, "Archivo no existe")

    # Intentar procesar con reintentos
    for intento in range(1, MAX_RETRIES + 1):
        try:
            safe_print(f"[{idx}/{total}] Procesando: {file_name} (intento {intento}/{MAX_RETRIES})")

            result = process_image_ocr(
                image_path=image_path,
                resize_percent=100,
                model=MODEL,
                max_tokens=2500,
                prompt=PROMPT,
                output_path=output_path,
            )

            safe_print(f"[{idx}/{total}] ✓ {file_name} - Guardado exitosamente")
            return (True, file_name, None)

        except Exception as e:
            error_msg = str(e)
            if intento < MAX_RETRIES:
                delay = RETRY_DELAY_BASE * (2 ** (intento - 1))  # Backoff exponencial: 5s, 10s, 20s
                safe_print(
                    f"[{idx}/{total}] ⚠ {file_name} - Error (reintentando en {delay}s): {error_msg}"
                )
                time.sleep(delay)
            else:
                safe_print(
                    f"[{idx}/{total}] ✗ {file_name} - Error final después de {MAX_RETRIES} intentos: {error_msg}"
                )
                return (False, file_name, error_msg)

    return (False, file_name, "Número máximo de reintentos alcanzado")


# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Leer el CSV
df = pd.read_csv(IMAGE_CSV_PATH)

# Obtener lista de archivos JSON ya procesados
archivos_procesados = set()
if os.path.exists(OUTPUT_DIR):
    for archivo in os.listdir(OUTPUT_DIR):
        if archivo.endswith(".json"):
            archivos_procesados.add(archivo)

print("\n" + "=" * 60)
print("📊 ESTADO DEL PROCESAMIENTO")
print("=" * 60)
print(f"📁 Total de imágenes en CSV: {len(df)}")
print(f"✅ Ya procesadas correctamente (se omitirán): {len(archivos_procesados)}")

# Filtrar el DataFrame para excluir los ya procesados
df_filtrado = df[~df["json_name"].isin(archivos_procesados)]

print(f"🔄 Pendientes por procesar: {len(df_filtrado)}")
print(f"⚙️  Trabajadores paralelos: {NUM_WORKERS}")
print(f"🔁 Reintentos máximos por imagen: {MAX_RETRIES}")
print(f"⏱️  Delay base entre reintentos: {RETRY_DELAY_BASE}s")

if len(archivos_procesados) > 0:
    porcentaje_completado = (len(archivos_procesados) / len(df)) * 100
    print(f"📈 Progreso total: {porcentaje_completado:.1f}% completado")

print("=" * 60)

# Verificar si hay algo que procesar
if len(df_filtrado) == 0:
    print("\n✨ ¡Todo está procesado! No hay imágenes pendientes.\n")
    exit(0)

# Preparar datos para procesamiento paralelo
tareas = []
for idx, (index, row) in enumerate(df_filtrado.iterrows(), 1):
    row_data = {
        "file_name": row["file_name"],
        "json_name": row["json_name"],
        "image_path": row["image_path"],
    }
    tareas.append((row_data, idx, len(df_filtrado)))

# Procesar en paralelo con ThreadPoolExecutor
start_time = time.time()
exitosos = 0
fallidos = 0
errores = []

print(f"\n🚀 Iniciando procesamiento paralelo...\n")

with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
    # Enviar todas las tareas
    futures = {executor.submit(procesar_imagen, *tarea): tarea for tarea in tareas}

    # Procesar resultados conforme se completan
    for future in as_completed(futures):
        try:
            success, file_name, error_msg = future.result()
            if success:
                exitosos += 1
            else:
                fallidos += 1
                if error_msg:
                    errores.append((file_name, error_msg))
        except Exception as e:
            fallidos += 1
            safe_print(f"✗ Error inesperado en thread: {str(e)}")

# Resumen final
elapsed_time = time.time() - start_time
total_procesados = exitosos + fallidos

print("\n" + "=" * 60)
print("RESUMEN DE PROCESAMIENTO")
print("=" * 60)
print(f"Total procesados: {total_procesados}")
print(f"✓ Exitosos: {exitosos}")
print(f"✗ Fallidos: {fallidos}")
print(f"⏱ Tiempo total: {elapsed_time:.2f} segundos")
if total_procesados > 0:
    print(f"⚡ Promedio: {elapsed_time/total_procesados:.2f} seg/imagen")
print("=" * 60)

# Mostrar errores si hay
if errores:
    print("\nERRORES ENCONTRADOS:")
    print("-" * 60)
    for file_name, error_msg in errores[:10]:  # Mostrar máximo 10 errores
        print(f"  • {file_name}: {error_msg}")
    if len(errores) > 10:
        print(f"  ... y {len(errores) - 10} errores más")
    print("-" * 60)
