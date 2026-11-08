"""HU G01 - Gráficas y conclusiones sobre la tabla empresas.

Uso:
    python scripts/reporte_empresas.py empresas_limpio.csv

Lee el CSV limpio, crea tres gráficas con matplotlib, las guarda en reportes/
e imprime la ruta de cada una y las conclusiones.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")  # Sin ventana: el script nunca se queda esperando
import matplotlib.pyplot as plt
import pandas as pd

CARPETA_REPORTES = "reportes"
DPI = 120


def cargar_datos(ruta_csv):
    """Lee el CSV limpio y deja la columna 'activa' como booleana."""
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")
    df = pd.read_csv(ruta_csv)

    faltantes = {"sector", "activa", "correo_valido"} - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas en el CSV: {sorted(faltantes)}")

    # Si el CSV trae 'True'/'False' como texto, se convierten a booleano
    for columna in ("activa", "correo_valido"):
        if df[columna].dtype == object:
            df[columna] = df[columna].astype(str).str.strip().str.lower() == "true"
    return df


def guardar_grafica(ruta):
    """Ajusta el diseño, guarda la figura con dpi=120 y la cierra."""
    plt.tight_layout()
    plt.savefig(ruta, dpi=DPI)
    plt.close()
    print(f"Gráfica guardada: {ruta}")


def grafica_1_por_sector(df):
    """Gráfica 1 (barras): cantidad de empresas por sector."""
    ruta = os.path.join(CARPETA_REPORTES, "empresas_grafica_1.png")
    por_sector = df["sector"].value_counts()

    plt.figure(figsize=(10, 6))
    por_sector.plot(kind="bar", color="#2b5c8f", edgecolor="black")
    plt.title("Cantidad de empresas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=45, ha="right")
    guardar_grafica(ruta)
    return ruta


def grafica_2_activas_inactivas(df):
    """Gráfica 2 (torta): proporción de empresas activas e inactivas."""
    ruta = os.path.join(CARPETA_REPORTES, "empresas_grafica_2.png")
    estados = df["activa"].value_counts().rename(
        index={True: "Activas", False: "Inactivas"}
    )

    plt.figure(figsize=(7, 7))
    estados.plot(kind="pie", autopct="%1.1f%%", startangle=90,
                 wedgeprops={"edgecolor": "black"})
    plt.title("Empresas activas vs inactivas")
    plt.xlabel("Estado de la empresa")
    plt.ylabel("Cantidad de empresas")
    guardar_grafica(ruta)
    return ruta


def grafica_3_apiladas(df):
    """Gráfica 3 (barras apiladas): activas e inactivas por sector."""
    ruta = os.path.join(CARPETA_REPORTES, "empresas_grafica_3.png")
    tabla = pd.crosstab(df["sector"], df["activa"]).rename(
        columns={True: "Activas", False: "Inactivas"}
    )
    # Orden fijo de las columnas y de los sectores (de mayor a menor total)
    tabla = tabla.reindex(columns=["Activas", "Inactivas"], fill_value=0)
    tabla = tabla.loc[tabla.sum(axis=1).sort_values(ascending=False).index]

    plt.figure(figsize=(10, 6))
    tabla.plot(kind="bar", stacked=True, color=["#4CAF50", "#F44336"],
               edgecolor="black", ax=plt.gca())
    plt.title("Empresas activas e inactivas por sector")
    plt.xlabel("Sector")
    plt.ylabel("Cantidad de empresas")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Estado")
    guardar_grafica(ruta)
    return ruta


def imprimir_conclusiones(df):
    """Calcula e imprime las conclusiones a partir de los datos."""
    total = len(df)
    por_sector = df["sector"].value_counts()
    maximo = por_sector.max()
    lideres = list(por_sector[por_sector == maximo].index)

    inactivas = int((~df["activa"]).sum())
    pct_inactivas = inactivas / total * 100
    invalidos = int((~df["correo_valido"]).sum())

    print("\n" + "=" * 60)
    print("CONCLUSIONES")
    print("=" * 60)

    print(f"1. Sector con más empresas: {' y '.join(lideres)} "
          f"({maximo} de {total} empresas, {maximo / total * 100:.1f}%).")

    print(f"2. Empresas inactivas: {inactivas} de {total} ({pct_inactivas:.1f}%). "
          "Son empresas registradas que no están operando en la plataforma: "
          "cuentan en el registro pero no generan actividad, así que hay que "
          "revisar por qué se inactivan (abandono, datos desactualizados) y "
          "evitar que inflen las métricas.")

    print(f"3. Correos inválidos: {invalidos} de {total}. "
          "Hay que validarlos también en el back: el front se puede saltar "
          "(otro cliente, la API directa, JavaScript desactivado), así que el "
          "servidor es la única barrera que garantiza que no entren datos malos "
          "y que se pueda contactar a la empresa.")


def main():
    """Punto de entrada: lee el CSV, genera las gráficas y muestra conclusiones."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/reporte_empresas.py empresas_limpio.csv",
              file=sys.stderr)
        sys.exit(1)

    try:
        df = cargar_datos(sys.argv[1])
        print(f"Datos cargados: {len(df)} empresas")
        os.makedirs(CARPETA_REPORTES, exist_ok=True)

        grafica_1_por_sector(df)
        grafica_2_activas_inactivas(df)
        grafica_3_apiladas(df)
        imprimir_conclusiones(df)
    except Exception as error:
        print(f"Error al generar el reporte: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()