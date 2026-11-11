"""Reporte de evidencias (HU G01).

Lee evidencias_limpio.csv, crea tres graficas con matplotlib, las guarda en
reportes/ e imprime las conclusiones.

Uso:
    python src/reporte_evidencias.py data/limpio/evidencias_limpio.csv
"""

import os
import re
import sys

import matplotlib

matplotlib.use("Agg")  # Sin ventanas: el script nunca se queda esperando.
import matplotlib.pyplot as plt
import pandas as pd

CARPETA_REPORTES = "reportes"
RUTA_GRAFICA_1 = os.path.join(CARPETA_REPORTES, "evidencias_grafica_1.png")
RUTA_GRAFICA_2 = os.path.join(CARPETA_REPORTES, "evidencias_grafica_2.png")
RUTA_GRAFICA_3 = os.path.join(CARPETA_REPORTES, "evidencias_grafica_3.png")

# Una URL valida empieza por http:// o https://, tiene dominio con punto y no tiene espacios.
PATRON_URL = re.compile(r"^https?://([\w-]+\.)+[a-z]{2,}([/?#]\S*)?$", re.IGNORECASE)

NOTA_MINIMA = 0
NOTA_MAXIMA = 5


def leer_datos(ruta):
    """Lee el CSV de evidencias y termina con un mensaje claro si no se puede abrir."""
    if not os.path.isfile(ruta):
        print(f"No se encontro el archivo: {ruta}")
        sys.exit(1)
    return pd.read_csv(ruta, encoding="utf-8")


def buscar_columna(df, exactos, parcial, nombre):
    """Busca una columna por nombre exacto y, si no esta, por una parte del nombre."""
    columnas = {c.strip().lower(): c for c in df.columns}
    for candidato in exactos:
        if candidato in columnas:
            return columnas[candidato]
    for clave, original in columnas.items():
        if parcial in clave:
            return original
    print(f"No encontre la columna de {nombre}. Columnas disponibles: {list(df.columns)}")
    sys.exit(1)


def preparar_datos(df):
    """Renombra las columnas clave (estado, fecha, calificacion, url) y convierte sus tipos."""
    df = df.rename(
        columns={
            buscar_columna(df, ["estado"], "estado", "estado"): "estado",
            buscar_columna(df, ["fecha_entrega", "fecha"], "fecha", "fecha"): "fecha",
            buscar_columna(df, ["calificacion", "nota"], "calificacion", "calificacion"): "calificacion",
            buscar_columna(df, ["url", "enlace"], "url", "URL"): "url",
        }
    )
    df["estado"] = df["estado"].str.strip().str.lower()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["calificacion"] = pd.to_numeric(df["calificacion"], errors="coerce")
    return df


def guardar_grafica(ruta):
    """Ajusta el diseno, guarda la grafica actual con dpi=120 y la cierra."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_estados(df):
    """Grafica 1: barras con la cantidad de entregas por estado."""
    conteo = df["estado"].value_counts()
    conteo.plot(kind="bar", figsize=(8, 5), rot=0)
    plt.title("Entregas por estado")
    plt.xlabel("Estado de la entrega")
    plt.ylabel("Cantidad de entregas")
    return guardar_grafica(RUTA_GRAFICA_1)


def grafica_por_mes(df):
    """Grafica 2: linea con la cantidad de entregas por mes."""
    por_mes = df["fecha"].dt.to_period("M").value_counts().sort_index()
    por_mes.index = por_mes.index.astype(str)
    por_mes.plot(kind="line", marker="o", figsize=(8, 5))
    plt.title("Entregas por mes")
    plt.xlabel("Mes")
    plt.ylabel("Cantidad de entregas")
    return guardar_grafica(RUTA_GRAFICA_2)


def grafica_calificaciones(df):
    """Grafica 3: histograma de como se reparten las calificaciones."""
    df["calificacion"].plot(kind="hist", bins=10, figsize=(8, 5))
    plt.title("Distribucion de las calificaciones")
    plt.xlabel("Calificacion")
    plt.ylabel("Cantidad de entregas")
    return guardar_grafica(RUTA_GRAFICA_3)


def contar_errores(df):
    """Cuenta las calificaciones fuera del rango 0 a 5 y las URL con formato invalido."""
    notas = df["calificacion"].dropna()
    fuera_de_rango = int(((notas < NOTA_MINIMA) | (notas > NOTA_MAXIMA)).sum())
    urls_validas = df["url"].astype(str).str.strip().str.match(PATRON_URL)
    url_invalidas = int((~urls_validas).sum())
    return fuera_de_rango, url_invalidas


def imprimir_conclusiones(df):
    """Imprime las conclusiones: estados, mes con mas entregas y errores de calidad."""
    total = len(df)
    estados = df["estado"].fillna("")
    aprobadas = int(estados.str.contains("aprob").sum())
    rechazadas = int(estados.str.contains("rechaz").sum())

    por_mes = df["fecha"].dt.to_period("M").value_counts()
    mes_pico = str(por_mes.idxmax())
    entregas_pico = int(por_mes.max())

    fuera_de_rango, url_invalidas = contar_errores(df)

    print("\n=== CONCLUSIONES ===")
    print(f"1. Estado de las entregas (total: {total}):")
    print(f"   - Aprobadas: {aprobadas} ({aprobadas / total * 100:.1f}%)")
    print(f"   - Rechazadas: {rechazadas} ({rechazadas / total * 100:.1f}%)")
    print(f"2. Las entregas se concentran en {mes_pico}: {entregas_pico} de {int(por_mes.sum())} "
          f"({entregas_pico / por_mes.sum() * 100:.1f}%).")
    print("   Puede deberse a que ese mes coincide con una fecha limite o cierre de corte,")
    print("   y mucha gente entrega justo antes del plazo.")
    print("3. Calidad de los datos:")
    print(f"   - Calificaciones fuera del rango {NOTA_MINIMA} a {NOTA_MAXIMA}: {fuera_de_rango}")
    print(f"   - URL con formato invalido: {url_invalidas}")
    print("   El back debe validar que la nota este entre 0 y 5 y que la URL tenga un formato")
    print("   correcto (http/https y dominio) antes de guardar; si no, estos errores entran a la")
    print("   base de datos y distorsionan los promedios, los reportes y los enlaces de evidencia.")


def main():
    """Lee el CSV, crea las tres graficas, imprime sus rutas y las conclusiones."""
    if len(sys.argv) != 2:
        print("Uso: python src/reporte_evidencias.py data/limpio/evidencias_limpio.csv")
        sys.exit(1)

    df = preparar_datos(leer_datos(sys.argv[1]))
    os.makedirs(CARPETA_REPORTES, exist_ok=True)

    print("Graficas guardadas:")
    for ruta in (grafica_estados(df), grafica_por_mes(df), grafica_calificaciones(df)):
        print(f"  - {ruta}")

    imprimir_conclusiones(df)


if __name__ == "__main__":
    main()