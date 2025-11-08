from pathlib import Path

TABLE_HTML_PATH = Path("./data/Table.html")
DOCUMENTOS_HISTORICO_PATH = Path("./data/documentos_historico.csv")

########################################
# 1. Leer los datos de table
########################################
from bs4 import BeautifulSoup

with open(TABLE_HTML_PATH, "r", encoding="utf-8") as file:
    html = file.read()

# Crear un objeto BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

import re

# Lista para guardar resultados
result = []

# Variables para rastrear la jerarquía actual
current_periodo_parlamentario = None
current_periodo_anual = None
current_legislatura = None


# Función para limpiar espacios adicionales
def clean_text(text):
    # Reemplazar múltiples espacios con uno solo
    return re.sub(r"\s+", " ", text).strip()


# Recorrer todas las filas de la tabla
for tr in soup.find_all("tr", valign="top"):
    # Verificar si contiene un Periodo Parlamentario
    font_periodo_parlamentario = tr.find(
        "font", string=lambda text: text and "Congreso de la República" in text
    )
    if font_periodo_parlamentario:
        current_periodo_parlamentario = clean_text(font_periodo_parlamentario.text)

    # Verificar si contiene un Periodo Anual de Sesiones
    font_periodo_anual = tr.find(
        "font", string=lambda text: text and "Período Anual de Sesiones" in text
    )
    if font_periodo_anual:
        current_periodo_anual = clean_text(font_periodo_anual.text)

    # Verificar si contiene una Legislatura
    font_legislatura = tr.find("font", string=lambda text: text and "Legislatura" in text)
    if font_legislatura:
        current_legislatura = clean_text(font_legislatura.text)

    # Buscar todos los enlaces en la fila
    a_tags = tr.find_all("a", href=True)

    # Procesar solo si hay enlaces
    if a_tags:
        # Buscar el enlace que tenga texto (no vacío)
        link_text = None
        link = None

        # Si el enlace tiene texto
        for a_tag in a_tags:
            text = clean_text(a_tag.get_text())
            if text:
                link = a_tag["href"]
                link_text = text
                break

        # Si encontramos un enlace con texto, guardarlo
        if link and link_text:
            result.append(
                {
                    "periodo_parlamentario": current_periodo_parlamentario,
                    "periodo_anual": current_periodo_anual,
                    "legislatura": current_legislatura,
                    "descripcion": link_text,
                    "link": link,
                }
            )

# Mostrar los resultados
for item in result[13:15]:
    print(f"Periodo Parlamentario: {item['periodo_parlamentario']}")
    print(f"Periodo Anual de Sesiones: {item['periodo_anual']}")
    print(f"Legislatura: {item['legislatura']}")
    print(f"Descripción: {item['descripcion']}")
    print(f"Link: {item['link']}")
    print("-" * 40)

print("Total de resultados:", len(result))

# Debug de los datos de los links
from collections import Counter

link_types = Counter()
for item in result:
    if "javascript:openWindow(" in item["link"]:
        link_types["javascript"] += 1
    else:
        link_types["otros"] += 1

print(link_types)

###################################################################
# 2. Generar los links de descarga y nombre de cada archivo
###################################################################

import re
import unicodedata
import uuid

import pandas as pd


def clean_filename(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("utf-8")
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text.strip().lower()


def generate_uuid_filename(url):
    """Genera un nombre de archivo único basado en la URL usando UUID5"""
    full_uuid = uuid.uuid5(uuid.NAMESPACE_URL, url)
    return f"{str(full_uuid)}.pdf"


# Filtrar los links válidos
clean_results = [item for item in result if "javascript:openWindow(" in item["link"]]

# Crear DataFrame
df_result = pd.DataFrame(clean_results)

# Extraer el link limpio
base_link = "https://www2.congreso.gob.pe/Sicr/RelatAgenda/PlenoComiPerm20112016.nsf/"
df_result["clean_link"] = df_result["link"].str.extract(r"javascript:openWindow\('([^']+)'\)")
df_result["clean_link"] = base_link + df_result["clean_link"]
df_result.drop("link", axis=1, inplace=True)

# Generar nombre de archivo único basado en clean_link
df_result["file_name"] = df_result["clean_link"].apply(generate_uuid_filename)

# Seleccionar columnas finales (AGREGADA 'file_name')
df_result = df_result[
    [
        "periodo_parlamentario",
        "periodo_anual",
        "legislatura",
        "descripcion",
        "clean_link",
        "file_name",
    ]
]

# ------------------------------------------------------------------
# 3. Unificar con histórico y generar salidas
# ------------------------------------------------------------------

if DOCUMENTOS_HISTORICO_PATH.exists():
    df_historico = pd.read_csv(DOCUMENTOS_HISTORICO_PATH)

    # Asegurar que el histórico tenga las columnas necesarias
    columnas_faltantes = set(df_result.columns) - set(df_historico.columns)
    if columnas_faltantes:
        for columna in columnas_faltantes:
            df_historico[columna] = pd.NA
else:
    df_historico = pd.DataFrame(columns=df_result.columns)

documentos_existentes = set(df_historico.get("file_name", []))
df_nuevos = df_result[~df_result["file_name"].isin(documentos_existentes)].copy()

if not df_nuevos.empty:
    df_historico = pd.concat([df_nuevos, df_historico], ignore_index=True)

# Limpiar duplicados por file_name para mantener datos consistentes
df_historico = df_historico.drop_duplicates(subset="file_name", keep="first")

# Guardar salidas
df_historico.to_csv(DOCUMENTOS_HISTORICO_PATH, sep=",", header=True, index=False, encoding="utf-8")

print("Total histórico:", len(df_historico))
print("Documentos nuevos:", len(df_nuevos))
if not df_nuevos.empty:
    print(df_nuevos[["descripcion", "clean_link", "file_name"]])
else:
    print("No se encontraron documentos nuevos.")
