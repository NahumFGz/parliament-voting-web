import warnings

warnings.filterwarnings("ignore")

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from tqdm import tqdm

# 🔧 Parámetros de descarga
MAX_WORKERS = 5  # número de descargas simultáneas
REQUEST_TIMEOUT = 200  # segundos máximos esperando respuesta del servidor por petición
MAX_RETRIES = 5  # número de reintentos por archivo
RETRY_DELAY = 60  # segundos de espera entre reintentos

# 📂 Archivos de entrada
DATA_FILE = "./data/documentos_scraper.csv"
DOWNLOAD_DIR = "./data/pdfs"

# Crear carpeta de destino si no existe
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Leer el DataFrame desde el TXT
try:
    df_result = pd.read_csv(
        DATA_FILE, sep=",", encoding="utf-8"
    )  # usa utf-8 para evitar errores de caracteres
except Exception as e:
    print(f"❌ Error al leer '{DATA_FILE}': {e}")
    exit(1)

# Verificar que existan columnas necesarias
required_cols = {"file_name", "clean_link"}
if not required_cols.issubset(df_result.columns):
    print(f"❌ El archivo debe contener las columnas: {required_cols}")
    exit(1)

# Subconjunto pendiente por descargar
total_archivos = len(df_result)
df_to_download = df_result


# Función de descarga con reintentos
def download_file(index, row):
    file_name = row["file_name"]
    file_path = os.path.join(DOWNLOAD_DIR, file_name)
    url = row["clean_link"]

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, verify=False, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return index, True, None
            else:
                last_error = f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            last_error = str(e)

        # Si no es el último intento, esperar antes de reintentar
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    # Si llegamos aquí, todos los intentos fallaron
    return index, False, f"Falló después de {MAX_RETRIES} intentos. Último error: {last_error}"


# Descarga paralela con barra de progreso
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {
        executor.submit(download_file, index, row): index
        for index, row in df_to_download.iterrows()
    }

    for future in tqdm(as_completed(futures), total=len(futures), desc="📥 Descargando archivos"):
        index, success, error = future.result()
        if success:
            continue
        else:
            print(f"⚠️ Error en índice {index}: {error}")
