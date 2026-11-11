"""
consultas_evidencias.py
HU Q01 - Cinco consultas sobre la tabla evidencias del proyecto integrador.

Uso:
    python scripts/consultas_evidencias.py evidencias_limpio.csv

Lee el archivo LIMPIO (no el sucio), responde las cinco consultas con pandas,
imprime el titulo y el resultado de cada una, en orden, y guarda cada
resultado como evidencias_consulta_N.csv en la misma carpeta del archivo leido.
"""

import sys
from pathlib import Path

import pandas as pd

# Columnas que el archivo limpio debe tener para poder responder las consultas.
COLUMNAS_NECESARIAS = ["id", "titulo", "calificacion", "estado", "mes"]


def cargar_datos(ruta):
    """Lee el CSV limpio y verifica que existan las columnas necesarias."""
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS_NECESARIAS if c not in df.columns]
    if faltan:
        raise ValueError(
            f"Al archivo le faltan las columnas {faltan}. "
            "Revisa que sea evidencias_limpio.csv y no el archivo sucio."
        )
    return df


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de una consulta como evidencias_consulta_N.csv."""
    destino = carpeta / f"evidencias_consulta_{numero}.csv"
    resultado.to_csv(destino)
    return destino


def consulta_1_aprobadas(df):
    """Consulta 1: devuelve las entregas con estado APROBADA."""
    print("\n=== Consulta 1: ¿Cuáles son las entregas aprobadas? ===")
    aprobadas = df[df["estado"] == "APROBADA"]
    print(aprobadas.to_string(index=False))
    return aprobadas


def consulta_2_top10(df):
    """Consulta 2: devuelve las 10 entregas mejor calificadas."""
    print("\n=== Consulta 2: ¿Cuáles son las 10 entregas mejor calificadas? ===")
    top = df.nlargest(10, "calificacion")[["titulo", "calificacion", "estado"]]
    print(top.to_string(index=False))
    return top


def consulta_3_conteo_por_estado(df):
    """Consulta 3: cuenta cuántas entregas hay en cada estado."""
    print("\n=== Consulta 3: ¿Cuántas entregas hay por estado? ===")
    conteo = df["estado"].value_counts()
    print(conteo.to_string())
    return conteo


def consulta_4_resumen_por_estado(df):
    """Consulta 4 (GROUPBY): calificación promedio, mínima y máxima por estado."""
    print("\n=== Consulta 4: ¿Cuál es la calificación promedio, mínima y máxima por estado? ===")
    resumen = df.groupby("estado")["calificacion"].agg(["count", "mean", "min", "max"]).round(2)
    print(resumen.to_string())
    return resumen


def consulta_5_entregas_por_mes(df):
    """Consulta 5 (GROUPBY): cuenta cuántas entregas hubo cada mes."""
    print("\n=== Consulta 5: ¿Cuántas entregas hubo cada mes? ===")
    por_mes = df.groupby("mes")["id"].count()
    print(por_mes.to_string())
    return por_mes


def main():
    """Lee el CSV recibido, corre las cinco consultas en orden y guarda los resultados."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/consultas_evidencias.py evidencias_limpio.csv")
        sys.exit(1)

    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"No se encontró el archivo: {ruta}")
        sys.exit(1)

    try:
        df = cargar_datos(ruta)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

    carpeta = ruta.parent
    consultas = [
        consulta_1_aprobadas,
        consulta_2_top10,
        consulta_3_conteo_por_estado,
        consulta_4_resumen_por_estado,
        consulta_5_entregas_por_mes,
    ]

    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        destino = guardar(resultado, carpeta, numero)
        print(f"-> Guardado en {destino}")


if __name__ == "__main__":
    main()