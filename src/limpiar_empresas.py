"""Etapa 3 - Limpieza de datos de empresas (HU L01).

Lee el archivo sucio generado en la etapa anterior, aplica procesos de limpieza
con pandas (eliminación de duplicados, normalización de textos, corrección de NITs,
corrección de teléfonos, validación de correos y estandarización de booleanos)
y exporta los resultados limpios a la carpeta correspondiente.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# --- Configuración de rutas ---
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]  # raíz del proyecto
CARPETA_CRUDO = CARPETA_PROYECTO / "data" / "crudo"
CARPETA_LIMPIO = CARPETA_PROYECTO / "data" / "limpio"

NOMBRE_ARCHIVO_ENTRADA = "empresas_sucio"
NOMBRE_ARCHIVO_SALIDA = "empresas_limpio"


def cargar_datos(carpeta: Path, nombre: str) -> pd.DataFrame:
    """Carga el archivo CSV sucio desde la carpeta de crudos."""
    ruta = carpeta / f"{nombre}.csv"
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo en: {ruta}")
    df = pd.read_csv(ruta)
    print(f"Datos cargados correctamente desde {ruta} | Tamaño inicial: {df.shape}")
    return df


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el pipeline de limpieza sobre el DataFrame sucio."""
    df_limpio = df.copy()

    # 1. Eliminar duplicados exactos de filas completas
    filas_antes = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates()
    print(f"-> Duplicados exactos eliminados: {filas_antes - len(df_limpio)}")

    # 2. Limpiar 'nombre': quitar espacios sobrantes y estandarizar formato título
    df_limpio["nombre"] = df_limpio["nombre"].astype(str).str.strip().str.title()

    # 3. Limpiar 'nit': extraer solo dígitos y eliminar duplicados de NIT (manteniendo el primero)
    df_limpio["nit_limpio"] = df_limpio["nit"].astype(str).str.replace(r"\D", "", regex=True)
    filas_nit = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates(subset=["nit_limpio"])
    print(f"-> NITs duplicados eliminados: {filas_nit - len(df_limpio)}")
    
    # Estandarizar el formato del NIT limpio
    df_limpio["nit"] = df_limpio["nit_limpio"]
    df_limpio = df_limpio.drop(columns=["nit_limpio"])

    # 4. Limpiar 'sector': quitar espacios sobrantes y estandarizar a formato título
    df_limpio["sector"] = df_limpio["sector"].astype(str).str.strip().str.lower().str.title()

    # 5. Limpiar 'contacto': rellenar nulos con una etiqueta estándar
    df_limpio["contacto"] = df_limpio["contacto"].fillna("No registrado")

    # 6. Limpiar 'correo': verificar que contengan '@', de lo contrario asignar un valor por defecto
    mask_correo = df_limpio["correo"].astype(str).str.contains("@", na=False)
    df_limpio.loc[~mask_correo, "correo"] = "correo_no_disponible@empresa.com"

    # 7. Limpiar 'telefono': extraer los últimos 10 dígitos para mantener un estándar numérico
    tel_digitos = df_limpio["telefono"].astype(str).str.replace(r"\D", "", regex=True).str[-10:]
    df_limpio["telefono"] = tel_digitos

    # 8. Limpiar 'activa': estandarizar valores de texto ('SI', 'No', '1', '0', True, False) a booleanos
    def convertir_activo(val):
        if pd.isna(val):
            return False
        val_str = str(val).strip().upper()
        if val_str in ["SI", "1", "TRUE", "T"]:
            return True
        elif val_str in ["NO", "0", "FALSE", "F"]:
            return False
        return False

    df_limpio["activa"] = df_limpio["activa"].apply(convertir_activo).astype(bool)

    print(f"-> Tamaño final después de la limpieza: {df_limpio.shape}")
    return df_limpio


def exportar_limpios(df: pd.DataFrame, carpeta: Path, nombre: str):
    """Exporta el DataFrame limpio a formatos CSV, Excel y JSON."""
    os.makedirs(carpeta, exist_ok=True)
    
    ruta_csv = carpeta / f"{nombre}.csv"
    ruta_excel = carpeta / f"{nombre}.xlsx"
    ruta_json = carpeta / f"{nombre}.json"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_excel, index=False, sheet_name="empresas_limpias")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    print(f"Exportado exitosamente en:\n - {ruta_csv}\n - {ruta_excel}\n - {ruta_json}")


if __name__ == "__main__":
    try:
        # Cargar datos sucios desde crudo
        df_sucio = cargar_datos(CARPETA_CRUDO, NOMBRE_ARCHIVO_ENTRADA)
        
        # Ejecutar proceso de limpieza
        df_limpio = limpiar_datos(df_sucio)
        
        # Guardar y exportar datos limpios
        exportar_limpios(df_limpio, CARPETA_LIMPIO, NOMBRE_ARCHIVO_SALIDA)
        
    except Exception as e:
        print(f"Error durante el proceso de limpieza: {e}", file=sys.stderr)
        sys.exit(1)