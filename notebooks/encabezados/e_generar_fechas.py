import json
from datetime import datetime
from pathlib import Path

INPUT_PATH = Path("../../public/db/encabezados_unificados.json")
OUTPUT_PATH = Path("../../public/db/encabezados_fechas.json")

_FMT = "%Y-%m-%d %H:%M:%S"


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as f:
        registros: list[dict] = json.load(f)

    fechas: list[datetime] = []
    for item in registros:
        raw = item.get("fecha_hora")
        if not raw or not isinstance(raw, str):
            continue
        try:
            fechas.append(datetime.strptime(raw.strip(), _FMT))
        except ValueError:
            continue

    if not fechas:
        raise ValueError(f"No hay fechas válidas en {INPUT_PATH}")

    min_dt = min(fechas)
    max_dt = max(fechas)

    salida = {
        "fecha_min": min_dt.strftime(_FMT),
        "fecha_max": max_dt.strftime(_FMT),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
