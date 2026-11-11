"""Genera graficas y conclusiones para los datos limpios de categorias."""

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RAIZ = Path(__file__).resolve().parents[3]
RUTA_LIMPIA = RAIZ / "data" / "limpio" / "categorias_limpio.csv"
RUTA_SUCIA = RAIZ / "data" / "crudo" / "categorias_sucio.csv"
CARPETA_REPORTES = RAIZ / "data" / "reportes"


def generar_reporte(ruta_csv: Path) -> None:
    """Crea las tres graficas solicitadas e imprime conclusiones basadas en datos."""
    df = pd.read_csv(ruta_csv)
    columnas_requeridas = {"nombre", "descripcion", "area_responsable"}
    faltantes = columnas_requeridas.difference(df.columns)
    if faltantes:
        raise ValueError(
            "Faltan columnas requeridas en el CSV: "
            + ", ".join(sorted(faltantes))
        )

    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    conteo = df["nombre"].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    conteo.plot(kind="barh")
    plt.title("Cantidad de registros por categoría")
    plt.xlabel("Cantidad de registros")
    plt.ylabel("Categoría")
    plt.tight_layout()
    plt.savefig(CARPETA_REPORTES / "categorias_grafica_1.png", dpi=120)
    plt.close()

    por_area = df["area_responsable"].value_counts()
    plt.figure(figsize=(8, 8))
    por_area.plot(kind="pie", autopct="%1.1f%%")
    plt.title("Reparto de registros por área responsable")
    plt.xlabel("Proporción de registros")
    plt.ylabel("Área responsable")
    plt.tight_layout()
    plt.savefig(CARPETA_REPORTES / "categorias_grafica_2.png", dpi=120)
    plt.close()

    if "largo_desc" in df.columns:
        df["largo_desc"] = pd.to_numeric(df["largo_desc"], errors="raise")
    else:
        df["largo_desc"] = df["descripcion"].fillna("").str.len()
    largos = df.groupby("nombre")["largo_desc"].mean().sort_index()
    plt.figure(figsize=(10, 6))
    largos.plot(kind="bar")
    plt.title("Largo promedio de la descripción por categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Largo promedio (caracteres)")
    plt.tight_layout()
    plt.savefig(CARPETA_REPORTES / "categorias_grafica_3.png", dpi=120)
    plt.close()

    print("\n=== CONCLUSIONES ===")
    if RUTA_SUCIA.is_file():
        filas_sucias = len(pd.read_csv(RUTA_SUCIA))
        filas_eliminadas = filas_sucias - len(df)
        print(
            f"Filas eliminadas: {filas_eliminadas} "
            f"(de {filas_sucias} filas sucias a {len(df)} filas limpias)."
        )
        print(
            "Las variantes de escritura se normalizaron en el nombre; "
            "no se eliminaron filas adicionales por esa normalización."
        )
    else:
        print(
            "Filas eliminadas: no se pudo calcular porque no se encontró "
            f"{RUTA_SUCIA} para comparar."
        )

    print(f"Categorías reales: {df['nombre'].nunique()} categorías únicas.")
    print(
        "El backend debe declarar `nombre` como único para impedir que se "
        "registren categorías repetidas con diferencias de mayúsculas, "
        "tildes o espacios."
    )

    categoria_mas_frecuente = conteo.idxmax()
    print(
        f"Categoría con más registros: {categoria_mas_frecuente} "
        f"({conteo.max()} registros)."
    )
    area_mas_frecuente = por_area.idxmax()
    print(
        f"Área con más registros: {area_mas_frecuente} "
        f"({por_area.max()} registros)."
    )
    print(
        "Categoría con mayor largo promedio de descripción: "
        f"{largos.idxmax()} ({largos.max():.1f} caracteres)."
    )

    for numero in range(1, 4):
        print(
            f"Gráfica {numero}: reportes/"
            f"categorias_grafica_{numero}.png"
        )


def main() -> None:
    ruta_csv = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_LIMPIA
    if not ruta_csv.is_absolute():
        ruta_csv = Path.cwd() / ruta_csv
    if not ruta_csv.is_file():
        raise FileNotFoundError(f"No se encontró el archivo CSV: {ruta_csv}")
    generar_reporte(ruta_csv)


if __name__ == "__main__":
    main()
