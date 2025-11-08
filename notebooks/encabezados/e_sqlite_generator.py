from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Sequence

JSON_PATH = Path("./db/encabezados_unificados.json")
SQLITE_PATH = Path("../../public/db/encabezados.sqlite")


def load_registros(json_path: Path) -> list[dict[str, Any]]:
    if not json_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo JSON en {json_path}")

    with json_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, list):
        raise ValueError("El archivo JSON debe contener una lista de objetos.")

    return data


def preparar_columnas(registros: Iterable[dict[str, Any]]) -> Sequence[str]:
    columnas: list[str] = []
    for registro in registros:
        for clave in registro.keys():
            if clave not in columnas:
                columnas.append(clave)
    if "id" in columnas:
        columnas.remove("id")
        columnas.insert(0, "id")
    return columnas


def asegurar_directorio(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def crear_tabla(conn: sqlite3.Connection, columnas: Sequence[str]) -> None:
    conn.execute("DROP TABLE IF EXISTS encabezados;")

    definiciones = []
    for columna in columnas:
        definicion = f'"{columna}" TEXT'
        if columna == "id":
            definicion += " PRIMARY KEY"
        definiciones.append(definicion)

    sentencia = f'CREATE TABLE encabezados ({", ".join(definiciones)});'
    conn.execute(sentencia)
    conn.commit()


def normalizar_valor(valor: Any) -> Any:
    if isinstance(valor, (str, int, float)) or valor is None:
        return valor
    return json.dumps(valor, ensure_ascii=False)


def insertar_registros(
    conn: sqlite3.Connection, columnas: Sequence[str], registros: Iterable[dict[str, Any]]
) -> None:
    placeholders = ", ".join(["?"] * len(columnas))
    columnas_sql = ", ".join(f'"{col}"' for col in columnas)
    sentencia = f"INSERT OR REPLACE INTO encabezados ({columnas_sql}) VALUES ({placeholders});"

    filas = []
    for registro in registros:
        fila = [normalizar_valor(registro.get(columna)) for columna in columnas]
        filas.append(fila)

    conn.executemany(sentencia, filas)
    conn.commit()


def generar_sqlite(json_path: Path = JSON_PATH, sqlite_path: Path = SQLITE_PATH) -> Path:
    registros = load_registros(json_path)
    columnas = preparar_columnas(registros)

    asegurar_directorio(sqlite_path)

    with sqlite3.connect(sqlite_path) as conn:
        crear_tabla(conn, columnas)
        insertar_registros(conn, columnas, registros)

    return sqlite_path


def main() -> None:
    destino = generar_sqlite()
    print(f"Base de datos creada/actualizada en {destino}")


if __name__ == "__main__":
    main()
