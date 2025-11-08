from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

INPUT_DIR = "./api_outputs"
OUTPUT_DIR = "./jsons"

FILENAME_PATTERN = re.compile(r"^(?P<doc_id>[a-f0-9-]+)_page(?P<page>\d+)_\.json$", re.IGNORECASE)


def agrupar_paginas_por_documento(input_dir: Path) -> dict[str, dict[str, dict[str, Any]]]:
    documentos: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    for json_path in sorted(input_dir.glob("*.json")):
        match = FILENAME_PATTERN.match(json_path.name)
        if not match:
            print(f"⚠️  Nombre de archivo no coincide con el patrón esperado y se omitirá: {json_path.name}")
            continue

        doc_id = match.group("doc_id")
        page_id = match.group("page")

        try:
            with json_path.open(encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            print(f"⚠️  No se pudo leer '{json_path.name}': {exc}")
            continue

        output = data.get("output")
        if not isinstance(output, dict):
            print(f"⚠️  El archivo '{json_path.name}' no contiene un objeto 'output' válido.")
            continue

        documentos[doc_id][page_id] = output

    return documentos


def escribir_documentos(documentos: dict[str, dict[str, dict[str, Any]]], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for doc_id, pages in documentos.items():
        if not pages:
            continue

        paginas_ordenadas = {page: pages[page] for page in sorted(pages)}
        output_path = output_dir / f"{doc_id}.json"

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(paginas_ordenadas, file, ensure_ascii=False, indent=2, sort_keys=False)
            file.write("\n")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    input_dir = (base_dir / INPUT_DIR).resolve()
    output_dir = (base_dir / OUTPUT_DIR).resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"No se encontró el directorio de entrada: {input_dir}")

    documentos = agrupar_paginas_por_documento(input_dir)

    if not documentos:
        print("No se encontraron archivos JSON para normalizar.")
        return

    escribir_documentos(documentos, output_dir)

    total_docs = len(documentos)
    total_paginas = sum(len(pages) for pages in documentos.values())
    print(f"✓ Normalización completada: {total_docs} documentos y {total_paginas} páginas procesadas.")


if __name__ == "__main__":
    main()
