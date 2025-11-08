from pathlib import Path

import pandas as pd

ENCABEZADOS_PATH = Path("../encabezados/jsons")
DOCUMENTOS_HISTORICO_PATH = Path("./data/documentos_historico.csv")
DOCUMENTOS_EXCLUIDOS_PATH = Path("./data/documentos_excluidos.csv")
DOCUMENTOS_SCRAPER_PATH = Path("./data/documentos_scraper.csv")


def construir_documentos_scraper() -> None:
    if not DOCUMENTOS_HISTORICO_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo histórico en {DOCUMENTOS_HISTORICO_PATH}"
        )

    encabezados = {path.stem for path in ENCABEZADOS_PATH.glob("*.json") if path.is_file()}

    excluidos = set()
    if DOCUMENTOS_EXCLUIDOS_PATH.exists():
        df_excluidos = pd.read_csv(DOCUMENTOS_EXCLUIDOS_PATH)
        columna_excluidos = "file_name" if "file_name" in df_excluidos.columns else "nombre"
        if columna_excluidos not in df_excluidos.columns:
            raise KeyError(
                "El archivo de excluidos debe contener la columna 'nombre' o 'file_name'."
            )
        excluidos = {Path(str(valor)).stem for valor in df_excluidos[columna_excluidos].dropna()}

    exclusiones = encabezados | excluidos

    df = pd.read_csv(DOCUMENTOS_HISTORICO_PATH)
    if "file_name" not in df.columns:
        raise KeyError("El archivo histórico debe contener la columna 'file_name'.")

    mask = df["file_name"].map(lambda nombre: Path(str(nombre)).stem not in exclusiones)
    df_filtrado = df[mask].copy()

    DOCUMENTOS_SCRAPER_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_filtrado.to_csv(DOCUMENTOS_SCRAPER_PATH, index=False)


if __name__ == "__main__":
    construir_documentos_scraper()
