"""Reporte de la tabla registros (HU G01): tres gráficas con matplotlib.

Se puede usar de dos formas:
    - Desde main.py:  generar_reportes(df, carpeta) -> (rutas, conclusiones)
    - Solo:           python src/notebook/reportes/reporte_registros.py data/limpio/registros_limpio.csv

Lee registros_limpio.csv, guarda tres gráficas en reportes/ (dpi=120)
e imprime las conclusiones.
"""
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def guardar_grafica(carpeta, nombre_archivo):
    """Ajusta el diseño, guarda la figura actual con dpi=120, la cierra y devuelve la ruta."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = Path(carpeta) / nombre_archivo
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_estados(df, carpeta):
    """Gráfica 1 (barras): participaciones por estado."""
    conteo = df["estado"].value_counts()
    plt.figure(figsize=(7, 4.5))
    conteo.plot(kind="bar")
    plt.title("Participaciones por estado")
    plt.xlabel("Estado")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=0)
    return guardar_grafica(carpeta, "registros_grafica_1.png")


def grafica_meses(por_mes, carpeta):
    """Gráfica 2 (línea): participaciones por mes."""
    plt.figure(figsize=(8, 4.5))
    por_mes.plot(kind="line", marker="o")
    plt.title("Participaciones por mes")
    plt.xlabel("Mes")
    plt.ylabel("Número de participaciones")
    plt.xticks(rotation=45)
    return guardar_grafica(carpeta, "registros_grafica_2.png")


def grafica_retos(top_retos, carpeta):
    """Gráfica 3 (barras horizontales): los 10 retos con más participantes."""
    plt.figure(figsize=(8, 5))
    top_retos.sort_values().plot(kind="barh")  # el reto más popular queda arriba
    plt.title("Los 10 retos con más participantes")
    plt.xlabel("Número de participantes")
    plt.ylabel("Reto")
    return guardar_grafica(carpeta, "registros_grafica_3.png")


def calcular_por_mes(df):
    """Cuenta las participaciones por mes (AAAA-MM)."""
    fechas = pd.to_datetime(df["fecha_registro"], errors="coerce")
    por_mes = fechas.dropna().dt.to_period("M").value_counts().sort_index()
    por_mes.index = por_mes.index.astype(str)
    return por_mes


def calcular_top_retos(df):
    """Cuenta los usuarios distintos por reto y devuelve el top 10."""
    por_reto = df.groupby("id_reto")["id_usuario"].nunique()
    return por_reto.sort_values(ascending=False).head(10)


def nombre_mes(periodo):
    """Convierte '2026-03' en 'marzo de 2026'."""
    anio, mes = periodo.split("-")
    return f"{MESES[int(mes) - 1]} de {anio}"


def armar_conclusiones(df, por_mes, top_retos):
    """Devuelve la lista de conclusiones (texto) que responde la HU."""
    duplicadas = int(df.duplicated(subset=["id_usuario", "id_reto"]).sum())
    estado = df["estado"].value_counts()
    empate = int((top_retos == top_retos.iloc[0]).sum())

    conclusiones = [
        f"El reto más popular es '{top_retos.index[0]}' con {int(top_retos.iloc[0])} participantes."
        + (f" (Hay un empate: {empate} retos tienen {int(top_retos.iloc[0])} participantes.)" if empate > 1 else ""),
        f"El mes con más inscripciones fue {nombre_mes(por_mes.idxmax())}, con {int(por_mes.max())}.",
        f"Se encontraron {duplicadas} inscripciones duplicadas (mismo usuario en el mismo reto). "
        "El back debe bloquearlas con 409 Conflict: la inscripción ya existe, así que repetirla "
        "no es un error del formato de la petición (400) ni un fallo del servidor (500). Con el 409 "
        "se evita contar dos veces al mismo participante, se mantienen correctas las estadísticas "
        "y el front sabe que el usuario ya estaba inscrito. Lo ideal es respaldarlo con una "
        "restricción única (id_usuario, id_reto) en la base de datos.",
        f"El estado más frecuente es '{estado.index[0]}' con {int(estado.iloc[0])} de {len(df)} participaciones.",
    ]
    return conclusiones


def generar_reportes(df, carpeta):
    """Crea las 3 gráficas en `carpeta` y devuelve (lista de rutas, lista de conclusiones)."""
    por_mes = calcular_por_mes(df)
    top_retos = calcular_top_retos(df)
    rutas = [
        grafica_estados(df, carpeta),
        grafica_meses(por_mes, carpeta),
        grafica_retos(top_retos, carpeta),
    ]
    return rutas, armar_conclusiones(df, por_mes, top_retos)


def imprimir_conclusiones(conclusiones):
    print("\nCONCLUSIONES")
    print("-" * 60)
    for n, texto in enumerate(conclusiones, start=1):
        print(f"{n}. {texto}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python reporte_registros.py registros_limpio.csv")
    datos = pd.read_csv(sys.argv[1], encoding="utf-8")
    rutas_png, textos = generar_reportes(datos, "reportes")
    print("GRÁFICAS GUARDADAS")
    for r in rutas_png:
        print(r)
    imprimir_conclusiones(textos)