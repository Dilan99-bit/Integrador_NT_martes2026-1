"""Consultas de la HU Q01 sobre la tabla retos (archivo LIMPIO).

Uso (desde cualquier carpeta):
    python src/notebook/consulta/consultas_retos.py

Lee data/limpio/retos_limpio.csv, resuelve cinco consultas con pandas, imprime
el titulo y el resultado de cada una, y guarda data/limpio/retos_consulta_N.csv.
"""
import os
import sys
from pathlib import Path

import pandas as pd

# src/notebook/consulta/consultas_retos.py -> parents[3] es la raiz del proyecto
CARPETA_PROYECTO = Path(__file__).resolve().parents[3]
CARPETA_LIMPIO = CARPETA_PROYECTO / "data" / "limpio"
RUTA_ENTRADA = CARPETA_LIMPIO / "retos_limpio.csv"

COLUMNAS = ["id", "nombre", "estado", "duracion_dias", "fecha_inicio"]


def cargar_datos(ruta):
    """Lee retos_limpio.csv, valida las columnas y convierte la fecha."""
    if not os.path.exists(ruta):
        sys.exit(f"Error: no se encontró el archivo '{ruta}'.")
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        sys.exit(f"Error: faltan las columnas {faltan} en '{ruta}'.")
    # El CSV guarda la fecha como texto: se convierte para poder usar .dt
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    return df


def guardar(resultado, carpeta, numero):
    """Guarda el resultado de la consulta N en retos_consulta_N.csv."""
    destino = os.path.join(carpeta, f"retos_consulta_{numero}.csv")
    resultado.to_csv(destino)
    return destino


def consulta_1(df):
    """Consulta 1: ¿qué retos están en curso?"""
    print("\nConsulta 1 - ¿Qué retos están en curso?")
    en_curso = df[df["estado"] == "EN_CURSO"]
    print(en_curso.to_string(index=False) if len(en_curso) else "(ninguno)")
    return en_curso


def consulta_2(df):
    """Consulta 2: ¿cuáles son los 10 retos más largos?"""
    print("\nConsulta 2 - ¿Cuáles son los 10 retos más largos?")
    largos = df.nlargest(10, "duracion_dias")[["nombre", "duracion_dias", "estado"]]
    print(largos.to_string(index=False))
    return largos


def consulta_3(df):
    """Consulta 3: ¿cuántos retos hay por estado?"""
    print("\nConsulta 3 - ¿Cuántos retos hay por estado?")
    conteo = df["estado"].value_counts()
    print(conteo.to_string())
    return conteo


def consulta_4(df):
    """Consulta 4 (groupby): duración promedio, mínima y máxima por estado."""
    print("\nConsulta 4 - ¿Cuál es la duración promedio, mínima y máxima por estado?")
    resumen = df.groupby("estado")["duracion_dias"].agg(["count", "mean", "min", "max"])
    resumen["mean"] = resumen["mean"].round(2)
    print(resumen.to_string())
    return resumen


def consulta_5(df):
    """Consulta 5 (groupby): ¿cuántos retos empiezan cada mes?"""
    print("\nConsulta 5 - ¿Cuántos retos empiezan cada mes?")
    por_mes = df.groupby(df["fecha_inicio"].dt.to_period("M"))["id"].count()
    por_mes.index = por_mes.index.astype(str)  # "2026-01" en vez de Period
    por_mes.index.name = "mes"
    print(por_mes.to_string())
    return por_mes


def main():
    """Lee el archivo, ejecuta las cinco consultas en orden y guarda los CSV."""
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_ENTRADA
    df = cargar_datos(ruta)
    carpeta = CARPETA_LIMPIO

    consultas = [consulta_1, consulta_2, consulta_3, consulta_4, consulta_5]
    for numero, consulta in enumerate(consultas, start=1):
        resultado = consulta(df)
        destino = guardar(resultado, carpeta, numero)
        print(f"-> Guardado en {destino}")


if __name__ == "__main__":
    main()
