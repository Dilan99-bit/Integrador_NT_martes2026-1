"""Ejecuta las cinco consultas de la HU Q01 sobre categorias limpias."""

import sys
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parents[3]
RUTA_LIMPIA = RAIZ / "data" / "limpio" / "categorias_limpio.csv"
CARPETA_SALIDA = RAIZ / "data" / "limpio"
COLUMNAS_REQUERIDAS = {
    "id",
    "nombre",
    "descripcion",
    "area_responsable",
}


def cargar_datos(ruta_csv: Path) -> pd.DataFrame:
    """Carga el CSV limpio y valida sus columnas necesarias."""
    df = pd.read_csv(ruta_csv)
    faltantes = COLUMNAS_REQUERIDAS.difference(df.columns)
    if faltantes:
        raise ValueError(
            "Faltan columnas requeridas en el CSV: "
            + ", ".join(sorted(faltantes))
        )
    if "largo_desc" not in df.columns:
        df["largo_desc"] = df["descripcion"].fillna("").str.len()
    return df


def imprimir_y_guardar(
    numero: int,
    pregunta: str,
    resultado: pd.DataFrame | pd.Series,
    carpeta_salida: Path,
) -> None:
    """Imprime una respuesta y la guarda en su archivo CSV."""
    print(f"\n=== Consulta {numero}: {pregunta} ===")
    print(resultado.to_string() if not resultado.empty else "(sin resultados)")

    ruta_salida = carpeta_salida / f"categorias_consulta_{numero}.csv"
    resultado.to_csv(ruta_salida, encoding="utf-8")
    print(f"Guardado: {ruta_salida}")


def consulta_1_conteo_por_categoria(
    df: pd.DataFrame, carpeta_salida: Path
) -> None:
    """Cuenta cuantas veces aparece cada categoria."""
    conteo = df["nombre"].value_counts()
    conteo.index.name = "nombre"
    conteo.name = "cantidad"
    imprimir_y_guardar(
        1, "Cuantas veces aparece cada categoria", conteo, carpeta_salida
    )


def consulta_2_sin_descripcion(
    df: pd.DataFrame, carpeta_salida: Path
) -> None:
    """Filtra las filas cuya descripcion fue rellenada por la limpieza."""
    sin_desc = df[df["descripcion"] == "Sin descripcion"]
    imprimir_y_guardar(
        2, "Categorias sin descripcion", sin_desc, carpeta_salida
    )


def consulta_3_largo_promedio(
    df: pd.DataFrame, carpeta_salida: Path
) -> None:
    """Calcula con groupby el largo promedio de descripcion por categoria."""
    largos = (
        df.groupby("nombre")["largo_desc"]
        .mean()
        .round(1)
        .sort_values(ascending=False)
    )
    largos.index.name = "nombre"
    largos.name = "largo_promedio"
    imprimir_y_guardar(
        3,
        "Largo promedio de la descripcion por categoria",
        largos,
        carpeta_salida,
    )


def consulta_4_categorias_por_area(
    df: pd.DataFrame, carpeta_salida: Path
) -> None:
    """Cuenta con groupby cuantos registros de categorias tiene cada area."""
    por_area = (
        df.groupby("area_responsable")["id"]
        .count()
        .sort_values(ascending=False)
    )
    por_area.index.name = "area_responsable"
    por_area.name = "cantidad_categorias"
    imprimir_y_guardar(
        4, "Cuantas categorias maneja cada area", por_area, carpeta_salida
    )


def consulta_5_tabla_cruzada(
    df: pd.DataFrame, carpeta_salida: Path
) -> None:
    """Cuenta con groupby doble las categorias registradas en cada area."""
    tabla = (
        df.groupby(["area_responsable", "nombre"])["id"]
        .count()
        .unstack(fill_value=0)
    )
    imprimir_y_guardar(
        5, "Categorias por area (tabla cruzada)", tabla, carpeta_salida
    )


def main() -> None:
    """Ejecuta las consultas en orden y guarda las cinco respuestas."""
    if len(sys.argv) > 2:
        raise ValueError(
            "Uso: python src/consultas_categorias.py [categorias_limpio.csv]"
        )

    ruta_csv = Path(sys.argv[1]) if len(sys.argv) == 2 else RUTA_LIMPIA
    if not ruta_csv.is_absolute():
        ruta_csv = Path.cwd() / ruta_csv
    if not ruta_csv.is_file():
        raise FileNotFoundError(f"No se encontro el archivo CSV: {ruta_csv}")

    df = cargar_datos(ruta_csv)
    ejecutar_consultas(df, CARPETA_SALIDA)


def ejecutar_consultas(df: pd.DataFrame, carpeta_salida: Path) -> None:
    """Ejecuta y guarda las cinco consultas de categorías."""
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    consulta_1_conteo_por_categoria(df, carpeta_salida)
    consulta_2_sin_descripcion(df, carpeta_salida)
    consulta_3_largo_promedio(df, carpeta_salida)
    consulta_4_categorias_por_area(df, carpeta_salida)
    consulta_5_tabla_cruzada(df, carpeta_salida)


if __name__ == "__main__":
    main()
