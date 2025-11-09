from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

JSONS_DIR = Path("./jsons")
DOCUMENTS_HISTORICOS_CSV_PATH = Path("../scraping/data/documentos_historico.csv")
OUTPUT_PATH = Path("../../public/db/encabezados_unificados.json")
ERRORES_PATH = Path("./errores.csv")


def _orden_pagina(pagina: str) -> tuple[int, str]:
    try:
        return (int(pagina), pagina)
    except ValueError:
        return (0, pagina)


def _normalizar_pagina(pagina: str) -> str:
    try:
        return str(int(pagina))
    except ValueError:
        return pagina


def _formatear_pagina(pagina: str) -> str:
    pagina_norm = _normalizar_pagina(pagina)
    try:
        return f"page{int(pagina_norm):03d}"
    except ValueError:
        return f"page{pagina_norm}"


def cargar_jsons(jsons_dir: Path) -> Iterable[Path]:
    if not jsons_dir.exists():
        raise FileNotFoundError(f"No se encontró el directorio con JSONs: {jsons_dir}")

    return sorted(jsons_dir.glob("*.json"))


def cargar_urls(documentos_csv_path: Path) -> dict[str, str]:
    if not documentos_csv_path.exists():
        print(
            f"[ADVERTENCIA] No se encontró el CSV de documentos históricos: {documentos_csv_path}"
        )
        return {}

    urls_por_id: dict[str, str] = {}

    with documentos_csv_path.open(encoding="utf-8", newline="") as file:
        lector = csv.DictReader(file)
        for fila in lector:
            file_name = (fila.get("file_name") or "").strip()
            clean_link = (fila.get("clean_link") or "").strip()

            if not file_name or not clean_link:
                continue

            if file_name.lower().endswith(".pdf"):
                doc_id = file_name[:-4]
            else:
                doc_id = file_name

            urls_por_id[doc_id] = clean_link

    return urls_por_id


def _normalizar_fecha(fecha: str | None) -> str | None:
    if not fecha:
        return None

    fecha = fecha.strip()

    # Reemplazar guiones o puntos por barras para compatibilidad
    fecha = fecha.replace("-", "/").replace(".", "/")

    # Si la fecha trae espacios entre números, los normalizamos
    fecha = re.sub(r"\s+", "", fecha)

    # Asegurarse que el año tenga cuatro dígitos (si trae dos, asumimos 20xx)
    partes = fecha.split("/")
    if len(partes) == 3 and len(partes[2]) == 2:
        partes[2] = f"20{partes[2]}"
        fecha = "/".join(partes)

    try:
        fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
    except ValueError:
        return None

    return fecha_dt.strftime("%Y-%m-%d")


def _normalizar_hora(hora: str | None) -> str | None:
    if not hora:
        return None

    hora = hora.strip().upper()

    # Reemplazar puntos, espacios y caracteres no numéricos antes del sufijo
    hora = hora.replace(".", "")

    # Corregir casos como "06:54:PM" -> "06:54PM"
    hora = re.sub(r":\s*(AM|PM)$", r"\1", hora)

    # Quitar sufijos mal espaciados, e.g., "06:54: PM" -> "06:54 PM"
    hora = re.sub(r"(?<=\d)(AM|PM)$", r" \1", hora)
    hora = re.sub(r"\s+(AM|PM)$", r" \1", hora)

    # Normalizar múltiples espacios
    hora = re.sub(r"\s+", " ", hora)

    # Corregir casos "00:06 AM" -> "12:06 AM" antes de usar formato de 12 horas
    if re.search(r"\b00:(\d{1,2})(?::\d{1,2})?\s*(AM|PM)$", hora):
        hora = re.sub(r"\b00:", "12:", hora, count=1)

    # Quitar segundos si existen: "06:54:32 PM" -> "06:54:32 PM"
    # Mantenerlos para parsing directo

    formatos = [
        "%I:%M %p",
        "%I:%M%p",
        "%I:%M:%S %p",
        "%I:%M:%S%p",
        "%H:%M",
        "%H:%M:%S",
    ]

    for formato in formatos:
        try:
            hora_dt = datetime.strptime(hora, formato)
            return hora_dt.strftime("%H:%M:%S")
        except ValueError:
            continue

    return None


def _combinar_fecha_hora(fecha: str | None, hora: str | None) -> str | None:
    fecha_norm = _normalizar_fecha(fecha)
    hora_norm = _normalizar_hora(hora)

    if not fecha_norm or not hora_norm:
        return None

    return f"{fecha_norm} {hora_norm}"


def construir_registros(
    json_paths: Iterable[Path], urls_por_id: dict[str, str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    registros: list[dict[str, Any]] = []
    errores: list[dict[str, Any]] = []

    for json_path in json_paths:
        doc_id = json_path.stem

        try:
            with json_path.open(encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            print(f"[ADVERTENCIA] No se pudo leer '{json_path.name}': {exc}")
            continue

        if not isinstance(data, dict):
            print(f"[ADVERTENCIA] El archivo '{json_path.name}' no contiene un objeto JSON válido.")
            continue

        for pagina, pagina_data in sorted(data.items(), key=lambda item: _orden_pagina(item[0])):
            if not isinstance(pagina_data, dict):
                print(
                    f"[ADVERTENCIA] La página '{pagina}' de '{json_path.name}' no es un objeto válido."
                )
                continue

            pagina_normalizada = _normalizar_pagina(pagina)
            pagina_formateada = _formatear_pagina(pagina)

            fecha_original = pagina_data.get("fecha")
            hora_original = pagina_data.get("hora")
            fecha_hora = _combinar_fecha_hora(fecha_original, hora_original)

            if not fecha_hora:
                errores.append(
                    {
                        "id": doc_id,
                        "pagina": pagina_normalizada,
                        "fecha": fecha_original,
                        "hora": hora_original,
                    }
                )

            url_base = urls_por_id.get(doc_id)
            if url_base:
                url_pag = f"{url_base}#page={pagina_normalizada}"
            else:
                url_pag = None

            registros.append(
                {
                    "id": f"{doc_id}_{pagina_formateada}",
                    "tipo": pagina_data.get("tipo"),
                    "fecha_hora": fecha_hora,
                    "asunto": pagina_data.get("asunto"),
                    "pagina": pagina_normalizada,
                    "url": url_pag,
                }
            )

    return registros, errores


def escribir_registros(registros: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(registros, file, ensure_ascii=False, indent=2, sort_keys=False)
        file.write("\n")


def escribir_errores(errores: list[dict[str, Any]], errores_path: Path) -> None:
    if not errores:
        if errores_path.exists():
            errores_path.unlink()
        return

    errores_path.parent.mkdir(parents=True, exist_ok=True)

    with errores_path.open("w", encoding="utf-8", newline="") as file:
        campos = ["id", "pagina", "fecha", "hora"]
        escritor = csv.DictWriter(file, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(errores)


def ordenar_registros_por_fecha_desc(registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
    registros_con_fecha = [r for r in registros if r.get("fecha_hora")]
    registros_sin_fecha = [r for r in registros if not r.get("fecha_hora")]

    registros_con_fecha.sort(key=lambda r: r["fecha_hora"], reverse=True)

    return registros_con_fecha + registros_sin_fecha


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    jsons_dir = (base_dir / JSONS_DIR).resolve()
    output_path = (base_dir / OUTPUT_PATH).resolve()
    documentos_csv_path = (base_dir / DOCUMENTS_HISTORICOS_CSV_PATH).resolve()
    errores_path = (base_dir / ERRORES_PATH).resolve()

    json_paths = cargar_jsons(jsons_dir)
    urls_por_id = cargar_urls(documentos_csv_path)
    registros, errores = construir_registros(json_paths, urls_por_id)

    if not registros:
        print("No se generaron registros a partir de los JSONs disponibles.")
        return

    registros = ordenar_registros_por_fecha_desc(registros)
    escribir_registros(registros, output_path)
    escribir_errores(errores, errores_path)

    print(f"[OK] Se generaron {len(registros)} registros en '{output_path}'.")
    if errores:
        print(
            f"[ADVERTENCIA] {len(errores)} registros no pudieron convertir fecha/hora. Ver '{errores_path}'."
        )
    else:
        print("[OK] Todas las fechas y horas se normalizaron correctamente.")


if __name__ == "__main__":
    main()
