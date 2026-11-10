"""Limpia el CSV de categorias y exporta el catalogo deduplicado."""

import sys
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[3]
CARPETA_CRUDO = RAIZ / "data" / "crudo"
CARPETA_LIMPIO = RAIZ / "data" / "limpio"


def obtener_ruta_entrada() -> Path:
    """Obtiene el CSV indicado o usa el archivo sucio predeterminado."""
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("categorias_sucio.csv")
    if not ruta.is_absolute() and not ruta.exists():
        ruta = CARPETA_CRUDO / ruta.name
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontro el archivo de entrada: {ruta}")
    return ruta


def imprimir_metricas(df: pd.DataFrame, titulo: str) -> None:
    """Muestra las metricas solicitadas antes y despues de la limpieza."""
    print(f"\n===== {titulo} =====")
    print("df.shape:", df.shape)
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print("\ndf.duplicated().sum():", df.duplicated().sum())


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Corrige duplicados, espacios, nombres y nulos del conjunto."""
    columnas_requeridas = {"nombre", "descripcion", "area_responsable"}
    faltantes = columnas_requeridas.difference(df.columns)
    if faltantes:
        raise ValueError(
            "Faltan columnas requeridas en el CSV: "
            + ", ".join(sorted(faltantes))
        )

    df = df.drop_duplicates().copy()

    for columna in df.columns:
        if not pd.api.types.is_string_dtype(df[columna].dtype):
            continue
        df[columna] = df[columna].str.strip().str.replace(
            r"\s+", " ", regex=True
        )
        df[columna] = df[columna].replace(r"^\s*$", pd.NA, regex=True)

    df["nombre"] = df["nombre"].str.strip().str.title()
    df["nombre"] = (
        df["nombre"]
        .str.normalize("NFKD")
        .str.encode("ascii", "ignore")
        .str.decode("utf-8")
    )
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    df["area_responsable"] = df["area_responsable"].fillna("Sin asignar")
    df = df.dropna(subset=["nombre"]).copy()
    df["largo_desc"] = df["descripcion"].str.len()
    return df.drop_duplicates().copy()


def guardar_limpio(df: pd.DataFrame, catalogo: pd.DataFrame) -> list[Path]:
    """Guarda los datos limpios en los formatos del proyecto y el catálogo CSV."""
    CARPETA_LIMPIO.mkdir(parents=True, exist_ok=True)
    rutas = [
        CARPETA_LIMPIO / "categorias_limpio.csv",
        CARPETA_LIMPIO / "categorias_limpio.xlsx",
        CARPETA_LIMPIO / "categorias_limpio.json",
        CARPETA_LIMPIO / "categorias_catalogo.csv",
    ]
    df.to_csv(rutas[0], index=False, encoding="utf-8")
    df.to_excel(rutas[1], index=False, sheet_name="categorias")
    df.to_json(rutas[2], orient="records", force_ascii=False, indent=2)
    catalogo.to_csv(rutas[3], index=False, encoding="utf-8")
    return rutas


def main() -> None:
    ruta_entrada = obtener_ruta_entrada()
    df = pd.read_csv(ruta_entrada, dtype=str)
    filas_antes = len(df)

    imprimir_metricas(df, "ANTES DE LIMPIAR")
    df = limpiar(df)
    catalogo = df.drop_duplicates(subset=["nombre"]).copy()
    filas_eliminadas = filas_antes - len(df)

    imprimir_metricas(df, "DESPUES DE LIMPIAR")
    print(
        f"\nFilas antes: {filas_antes} | filas despues: {len(df)} "
        f"| filas eliminadas: {filas_eliminadas}"
    )
    print(f"Categorias unicas en el catalogo: {len(catalogo)}")

    for ruta in guardar_limpio(df, catalogo):
        print(f"\nGuardado: {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
