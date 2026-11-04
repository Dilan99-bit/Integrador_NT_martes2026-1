"""Etapa 5 - Generación de reportes y gráficas analíticas sobre empresas (HU R01).

Carga los datos limpios, genera visualizaciones gráficas analíticas (por sector y estado)
y exporta los gráficos generados a la carpeta de reportes del proyecto.
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuración de rutas ---
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]  # raíz del proyecto
CARPETA_LIMPIO = CARPETA_PROYECTO / "data" / "limpio"
CARPETA_REPORTES = CARPETA_PROYECTO / "data" / "reportes"
NOMBRE_ARCHIVO = "empresas_limpio"


def cargar_datos_limpios(carpeta: Path, nombre: str) -> pd.DataFrame:
    """Carga el archivo CSV limpio para la generación de reportes."""
    ruta = carpeta / f"{nombre}.csv"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo limpio en: {ruta}. "
            "Asegúrate de ejecutar primero el script de limpieza."
        )
    df = pd.read_csv(ruta)
    print(f"Datos cargados para reporte | Total de registros: {len(df)}")
    return df


def generar_grafica_sectores(df: pd.DataFrame, carpeta_salida: Path):
    """Genera y guarda un gráfico de barras con la distribución de empresas por sector."""
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_grafica = carpeta_salida / "empresas_por_sector.png"

    conteo = df["sector"].value_counts()

    plt.figure(figsize=(10, 6))
    conteo.plot(kind="bar", color="#2b5c8f", edgecolor="black")
    plt.title("Distribución de Empresas por Sector Económico", fontsize=14, fontweight="bold")
    plt.xlabel("Sector", fontsize=12)
    plt.ylabel("Cantidad de Empresas", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    plt.savefig(ruta_grafica)
    plt.close()
    print(f"Gráfica generada -> {ruta_grafica}")


def generar_grafica_estado(df: pd.DataFrame, carpeta_salida: Path):
    """Genera y guarda un gráfico circular (pastel) con el estado de actividad de las empresas."""
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_grafica = carpeta_salida / "empresas_por_estado.png"

    conteo = df["activa"].map({True: "Activas", False: "Inactivas"}).value_counts()

    plt.figure(figsize=(7, 7))
    conteo.plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90,
        colors=["#4CAF50", "#F44336"],
        wedgeprops={"edgecolor": "black"}
    )
    plt.title("Proporción de Empresas Activas e Inactivas", fontsize=14, fontweight="bold")
    plt.ylabel("")  # Ocultar etiqueta del eje y
    plt.tight_layout()

    plt.savefig(ruta_grafica)
    plt.close()
    print(f"Gráfica generada -> {ruta_grafica}")


if __name__ == "__main__":
    try:
        # Cargar datos limpios
        df_empresas = cargar_datos_limpios(CARPETA_LIMPIO, NOMBRE_ARCHIVO)
        
        # Generar reportes gráficos analíticos
        print("\n" + "=" * 50)
        print("GENERANDO REPORTES Y GRÁFICAS ANALÍTICAS")
        print("=" * 50)
        
        generar_grafica_sectores(df_empresas, CARPETA_REPORTES)
        generar_grafica_estado(df_empresas, CARPETA_REPORTES)
        
        print("\n¡Todos los reportes y gráficas se han generado y guardado con éxito!")
        
    except Exception as e:
        print(f"Error al generar los reportes: {e}", file=sys.stderr)
        sys.exit(1)