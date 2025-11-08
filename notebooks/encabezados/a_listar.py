from __future__ import annotations

import csv
import re
from pathlib import Path

INPUT_DIR = Path("../scraping/data/zones")
OUTPUT_PATH = Path("./encabezados.csv")


def build_records(input_dir: Path) -> list[tuple[str, str, str]]:
    pattern = re.compile(r"_encabezado\d+_")
    records: list[tuple[str, str, str]] = []

    for image_path in sorted(input_dir.iterdir()):
        if not image_path.is_file():
            continue
        if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        file_name = image_path.name
        stem = image_path.stem
        json_stem = pattern.sub("_", stem)
        if json_stem == stem:
            json_stem = stem
        json_name = f"{json_stem}.json"
        records.append((file_name, json_name, str(image_path)))

    return records


def write_csv(records: list[tuple[str, str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open(mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["file_name", "json_name", "image_path"])
        writer.writerows(records)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    input_dir = (base_dir / INPUT_DIR).resolve()
    output_path = (base_dir / OUTPUT_PATH).resolve()

    if not input_dir.exists():
        raise FileNotFoundError(f"No se encontró el directorio de entrada: {input_dir}")

    records = build_records(input_dir)
    write_csv(records, output_path)


if __name__ == "__main__":
    main()
