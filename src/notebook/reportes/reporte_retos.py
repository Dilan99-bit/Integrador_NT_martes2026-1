"""Reporte gráfico de la tabla retos del proyecto integrador (HU G01 de Kaizen).

Uso (desde cualquier carpeta):
    python src/notebook/graficas/reporte_retos.py

Lee data/limpio/retos_limpio.csv, crea tres gráficas con matplotlib (barras,
línea e histograma), las guarda en reportes/ e imprime la ruta de cada una y
las conclusiones.
"""

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Sin ventana: solo guarda las imágenes, no se queda esperando.
import matplotlib.pyplot as plt
import pandas as pd

# Columnas que el archivo limpio debe tener para poder graficar.
COLUMNAS = ["estado", "fecha_inicio", "duracion_dias"]

# src/notebook/graficas/reporte_retos.py -> parents[3] es la raíz del proyecto
CARPETA_PROYECTO = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = CARPETA_PROYECTO / "data" / "limpio" / "retos_limpio.csv"

# Carpeta donde se guardan las imágenes.
CARPETA = str(CARPETA_PROYECTO / "reportes")

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# Posibles razones por mes. Son hipótesis: los datos solo dicen CUÁNDO empiezan
# los retos, no POR QUÉ, y hay que confirmarlas con el equipo.
MOTIVOS = {
    1: "inicio de año: la gente se pone metas nuevas y arranca el semestre académico",
    2: "arranque de actividades y de clases después de las vacaciones de fin de año",
    3: "arranque de actividades y de clases después de las vacaciones de fin de año",
    6: "la mitad del año invita a replantear metas antes de las vacaciones",
    7: "inicio del segundo semestre académico",
    8: "inicio del segundo semestre académico",
    9: "regreso a la rutina después de las vacaciones",
    10: "la gente busca cerrar el año con metas cumplidas",
    11: "preparación para cerrar el año con metas cumplidas",
    12: "cierre de año: la gente quiere dejar listo un reto para empezar enero",
}
MOTIVO_GENERICO = "puede coincidir con una campaña, un evento o una temporada propia de la plataforma"


def cargar_datos(ruta):
    """Lee retos_limpio.csv, valida las columnas y convierte fechas y duración."""
    if not os.path.exists(ruta):
        sys.exit(f"Error: no se encontró el archivo '{ruta}'.")
    df = pd.read_csv(ruta)
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        sys.exit(f"Error: faltan las columnas {faltan} en '{ruta}'.")
    # El CSV guarda las fechas y los números como texto: se convierten.
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["duracion_dias"] = pd.to_numeric(df["duracion_dias"], errors="coerce")
    if df["fecha_inicio"].notna().sum() == 0 or df["duracion_dias"].notna().sum() == 0:
        sys.exit("Error: no hay fechas de inicio o duraciones válidas para graficar.")
    return df


def calcular_por_mes(df):
    """Cuenta los retos que empiezan cada mes, incluyendo los meses sin retos (con 0)."""
    meses = df["fecha_inicio"].dropna().dt.to_period("M")
    por_mes = meses.value_counts().sort_index()
    rango = pd.period_range(por_mes.index.min(), por_mes.index.max(), freq="M")
    return por_mes.reindex(rango, fill_value=0)


def grafica_1(df):
    """Gráfica 1 (barras): cantidad de retos por estado."""
    conteo = df["estado"].value_counts()
    plt.figure(figsize=(8, 5))
    ax = conteo.plot(kind="bar")
    ax.bar_label(ax.containers[0])  # Muestra el número encima de cada barra.
    plt.title("Cantidad de retos por estado")
    plt.xlabel("Estado")
    plt.ylabel("Cantidad de retos")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    ruta = os.path.join(CARPETA, "retos_grafica_1.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_2(por_mes):
    """Gráfica 2 (línea): retos que empiezan cada mes."""
    serie = por_mes.copy()
    serie.index = serie.index.astype(str)  # "2026-01" en vez de Period
    plt.figure(figsize=(9, 5))
    serie.plot(kind="line", marker="o")
    plt.title("Retos que empiezan cada mes")
    plt.xlabel("Mes de inicio")
    plt.ylabel("Cantidad de retos")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    ruta = os.path.join(CARPETA, "retos_grafica_2.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def grafica_3(df):
    """Gráfica 3 (histograma): cómo se reparte la duración de los retos."""
    plt.figure(figsize=(8, 5))
    df["duracion_dias"].plot(kind="hist", bins=20, edgecolor="white")
    plt.title("Distribución de la duración de los retos")
    plt.xlabel("Duración (días)")
    plt.ylabel("Cantidad de retos")
    plt.tight_layout()
    ruta = os.path.join(CARPETA, "retos_grafica_3.png")
    plt.savefig(ruta, dpi=120)
    plt.close()
    return ruta


def conclusion_mes(por_mes):
    """Imprime en qué mes se concentran los retos y por qué puede ser."""
    maximo = por_mes.max()
    total = int(por_mes.sum())
    promedio = total / len(por_mes)
    print("1) ¿En qué mes se concentran los retos y por qué puede ser?")
    for periodo in por_mes[por_mes == maximo].index:
        nombre = f"{MESES[periodo.month - 1]} de {periodo.year}"
        print(f"   - {nombre}: {int(maximo)} de {total} retos con fecha de inicio "
              f"({maximo / total:.0%}); el promedio es {promedio:.1f} retos por mes.")
        motivo = MOTIVOS.get(periodo.month, MOTIVO_GENERICO)
        print(f"     Posible razón (hipótesis, hay que confirmarla): {motivo}.")


def conclusion_duracion(df):
    """Imprime la duración promedio por estado (sin contar las fechas incoherentes)."""
    validos = df[df["duracion_dias"] >= 0]
    resumen = validos.groupby("estado")["duracion_dias"].agg(["count", "mean"])
    estados = sorted(df["estado"].dropna().unique())
    print("\n2) ¿Cuánto dura en promedio un reto según su estado?")
    print("   (no se cuentan los retos con fecha de fin antes que la de inicio)")
    for estado in estados:
        if estado in resumen.index:
            fila = resumen.loc[estado]
            print(f"   - {estado}: {fila['mean']:.1f} días en promedio ({int(fila['count'])} retos)")
        else:
            print(f"   - {estado}: sin duraciones válidas")


def conclusion_incoherentes(df):
    """Imprime cuántos retos tienen la fecha de fin antes que la de inicio."""
    incoherentes = int((df["duracion_dias"] < 0).sum())
    sin_duracion = int(df["duracion_dias"].isna().sum())
    print("\n3) ¿Cuántos retos tenían la fecha de fin antes que la de inicio?")
    print(f"   - {incoherentes} de {len(df)} retos. Dato para el back: revisar por qué "
          "se pudieron guardar y validar las fechas al crear el reto.")
    print(f"   - Además, {sin_duracion} retos no tienen duración porque les falta una fecha.")


def imprimir_conclusiones(df, por_mes):
    """Imprime las tres conclusiones del reporte."""
    print("\n" + "=" * 60)
    print("CONCLUSIONES")
    print("=" * 60)
    conclusion_mes(por_mes)
    conclusion_duracion(df)
    conclusion_incoherentes(df)


def main():
    """Lee el archivo, crea y guarda las tres gráficas e imprime las conclusiones."""
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_ENTRADA
    df = cargar_datos(ruta)
    os.makedirs(CARPETA, exist_ok=True)  # La carpeta se crea sola.

    por_mes = calcular_por_mes(df)

    print("Gráficas guardadas:")
    for ruta in (grafica_1(df), grafica_2(por_mes), grafica_3(df)):
        print(f"  {ruta}")

    imprimir_conclusiones(df, por_mes)


if __name__ == "__main__":
    main()
