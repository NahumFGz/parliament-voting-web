import multiprocessing
import os
import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
from ultralytics import YOLO

# ⚙️ Configuraciones para votación
input_dir = "./data/classification/votacion"
output_dir = "./data/zones"
model_path = "./data/weights_yolo_zones_best.pt"

# 🔧 Configuración de paralelización
# Si es 0, procesa secuencialmente. Si > 0, usa ese número de workers
NUM_WORKERS = 8  # Puedes cambiar este valor según necesites

# 🎯 Configuraciones de márgenes verticales (% del alto de la zona)
# Porcentaje de expansión en el eje Y para la zona de encabezado
MARGEN_ENCABEZADO_ABAJO = 0.04  # 5% hacia abajo (0.05 = 5%)


def aplicar_margenes_verticales(x_min, y_min, x_max, y_max, label, img_height):
    """
    Aplica márgenes verticales según el tipo de zona detectada.

    Args:
        x_min, y_min, x_max, y_max: Coordenadas de la zona
        label: Nombre de la clase (encabezado, columnas, pie)
        img_height: Alto de la imagen completa

    Returns:
        Tupla (x_min, y_min_ajustada, x_max, y_max_ajustada)
    """
    alto_zona = y_max - y_min
    label_lower = label.lower()

    # Aplicar márgenes según el tipo de zona
    if "encabezado" in label_lower:
        # Encabezado: expandir hacia abajo
        incremento = int(alto_zona * MARGEN_ENCABEZADO_ABAJO)
        y_max_ajustado = min(y_max + incremento, img_height)
        return x_min, y_min, x_max, y_max_ajustado

    # Si no coincide con ninguna zona conocida, devolver original
    return x_min, y_min, x_max, y_max


def procesar_imagen(args):
    """
    Procesa una imagen individual: detecta zonas, aplica márgenes y guarda recortes.

    Args:
        args: Tupla con (idx, img_file, input_dir, output_dir, model_path, total_imgs)

    Returns:
        str: Mensaje de estado del procesamiento
    """
    idx, img_file, input_dir, output_dir, model_path, total_imgs = args

    # Cargar modelo YOLO en cada proceso
    model = YOLO(model_path)

    if idx % 100 == 0 or idx == 1:
        print(f"\n📊 Progreso: {idx}/{total_imgs} imágenes procesadas")

    image_path = os.path.join(input_dir, img_file)
    image_bgr = cv2.imread(image_path)

    if image_bgr is None:
        return f"[⚠️] No se pudo leer la imagen: {image_path}"

    # 📍 Predecir zonas
    results = model.predict(
        source=image_bgr, conf=0.01, max_det=3, agnostic_nms=True, verbose=False
    )
    for result in results:
        detecciones = result.boxes
        labels = result.names

        base_name = os.path.splitext(img_file)[0]

        # Obtener dimensiones de la imagen
        img_height, img_width = image_bgr.shape[:2]

        for i, box in enumerate(detecciones):
            x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
            label = labels[int(box.cls[0])]
            label_lower = label.lower()

            # Solo guardar zonas de encabezado
            if "encabezado" not in label_lower:
                continue

            # Aplicar márgenes verticales según el tipo de zona
            x_min, y_min, x_max, y_max = aplicar_margenes_verticales(
                x_min, y_min, x_max, y_max, label, img_height
            )

            # Recortar zona
            zona = image_bgr[y_min:y_max, x_min:x_max]

            # Guardar recorte
            zona_filename = f"{base_name}{label_lower}{i+1}.jpg"
            zona_path = os.path.join(output_dir, zona_filename)

            cv2.imwrite(zona_path, zona)

    return f"✅ Procesada: {img_file}"


# 🧹 Limpiar carpeta destino antes de iniciar
if os.path.exists(output_dir):
    for elemento in os.listdir(output_dir):
        ruta_elemento = os.path.join(output_dir, elemento)
        if os.path.isdir(ruta_elemento):
            shutil.rmtree(ruta_elemento)
        else:
            os.remove(ruta_elemento)

# 📂 Crear carpeta destino si no existe
os.makedirs(output_dir, exist_ok=True)

# 📋 Listar imágenes válidas
img_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
total_imgs = len(img_files)
print(f"📦 Total de imágenes detectadas: {total_imgs}")

# 🔧 Calcular número de workers óptimo
max_workers = None
if NUM_WORKERS > 0:
    cpu_count = multiprocessing.cpu_count()
    max_available = max(1, cpu_count - 2)  # Dejar 2 CPUs libres
    max_workers = min(NUM_WORKERS, max_available)
    print(
        f"🚀 Modo paralelo activado: usando {max_workers} workers (CPUs disponibles: {cpu_count})"
    )
else:
    print(f"🐌 Modo secuencial activado")

# 🔁 Procesar imágenes
# Preparar argumentos para cada imagen
args_list = [
    (idx, img_file, input_dir, output_dir, model_path, total_imgs)
    for idx, img_file in enumerate(img_files, start=1)
]

if NUM_WORKERS == 0:
    # Modo secuencial: procesar una por una
    for args in args_list:
        resultado = procesar_imagen(args)
        if "⚠️" in resultado:
            print(resultado)
else:
    # Modo paralelo: usar ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        resultados = executor.map(procesar_imagen, args_list)

        # Mostrar resultados (opcional, para ver errores)
        for resultado in resultados:
            if "⚠️" in resultado:
                print(resultado)

print(f"\n✅ Procesamiento completado: {total_imgs} imágenes")
