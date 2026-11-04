"""Etapa 4 - Consultas y reportes analíticos sobre empresas limpias (HU C01).

Carga el archivo limpio de empresas y realiza consultas analíticas clave
(distribución por sector, estado de actividad, conteos y filtros específicos).
"""

import sys
from pathlib import Path
import pandas as pd

# --- Configuración de rutas ---
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]  # raíz del proyecto
CARPETA_LIMPIO = CARPETA_PROYECTO / "data" / "limpio"
NOMBRE_ARCHIVO = "empresas_limpio"


def cargar_datos_limpios(carpeta: Path, nombre: str) -> pd.DataFrame:
    """Carga el archivo CSV limpio desde la carpeta correspondiente."""
    ruta = carpeta / f"{nombre}.csv"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo limpio en: {ruta}. "
            "Asegúrate de ejecutar primero el script de limpieza."
        )
    df = pd.read_csv(ruta)
    print(f"Datos limpios cargados correctamente | Total de registros: {len(df)}")
    return df


def consultar_total_empresas(df: pd.DataFrame):
    """Muestra el total de empresas registradas en el sistema."""
    print("\n" + "=" * 50)
    print("1. TOTAL DE EMPRESAS REGISTRADAS")
    print("=" * 50)
    print(f"Cantidad total de empresas activas e inactivas: {len(df)}")


def consultar_por_sector(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa y cuenta las empresas por sector económico."""
    print("\n" + "=" * 50)
    print("2. DISTRIBUCIÓN DE EMPRESAS POR SECTOR ECONÓMICO")
    print("=" * 50)
    conteo_sector = df["sector"].value_counts().reset_index()
    conteo_sector.columns = ["Sector", "Cantidad"]
    print(conteo_sector.to_string(index=False))
    return conteo_sector


def consultar_por_estado(df: pd.DataFrame) -> pd.DataFrame:
    """Muestra el desglose de empresas activas e inactivas."""
    print("\n" + "=" * 50)
    print("3. ESTADO DE ACTIVIDAD DE LAS EMPRESAS")
    print("=" * 50)
    conteo_estado = df["activa"].value_counts().reset_index()
    conteo_estado.columns = ["Activa", "Cantidad"]
    # Mapear valores booleanos a texto legible
    conteo_estado["Activa"] = conteo_estado["Activa"].map({True: "Sí", False: "No"})
    print(conteo_estado.to_string(index=False))
    return conteo_estado


def filtrar_empresas_por_sector(df: pd.DataFrame, sector_buscado: str) -> pd.DataFrame:
    """Filtra y lista las empresas que pertenecen a un sector específico."""
    print("\n" + "=" * 50)
    print(f"4. FILTRAR EMPRESAS POR SECTOR: '{sector_buscado}'")
    print("=" * 50)
    filtradas = df[df["sector"].str.lower() == sector_buscado.lower()]
    
    if filtradas.empty:
        print(f"No se encontraron empresas registradas en el sector '{sector_buscado}'.")
    else:
        print(f"Se encontraron {len(filtradas)} empresas en el sector '{sector_buscado}':")
        print(filtradas[["nombre", "nit", "contacto", "correo", "activa"]].to_string(index=False))
    
    return filtradas


if __name__ == "__main__":
    try:
        # Cargar los datos limpios
        df_empresas = cargar_datos_limpios(CARPETA_LIMPIO, NOMBRE_ARCHIVO)
        
        # Ejecutar las consultas y reportes analíticos
        consultar_total_empresas(df_empresas)
        consultar_por_sector(df_empresas)
        consultar_por_estado(df_empresas)
        
        # Ejemplo de filtro específico (puedes cambiar el sector de prueba según tus datos)
        filtrar_empresas_por_sector(df_empresas, "Tecnología")
        
    except Exception as e:
        print(f"Error al ejecutar las consultas: {e}", file=sys.stderr)
        sys.exit(1)