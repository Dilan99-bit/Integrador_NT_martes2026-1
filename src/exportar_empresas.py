"""Etapa 2 - Exportación de empresas_sucio a CSV, XLSX y JSON (HU X01)."""

import os
import sys
from importlib import import_module
from pathlib import Path

# src/ está en la carpeta del script; así 'simular_empresas' se importa sin importar desde dónde se ejecute
sys.path.insert(0, str(Path(__file__).resolve().parent))

# --- Configuración ---
NOMBRE_ARCHIVO = "empresas_sucio"
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]   # src/ -> raíz del proyecto
CARPETA_CRUDO = CARPETA_PROYECTO / "data" / "crudo"


def exportar_csv(df, carpeta, nombre):
    ruta = carpeta / f"{nombre}.csv"
    df.to_csv(ruta, index=False, encoding="utf-8")
    print(f"Generado CSV   -> Ruta: {ruta} | Tamaño: {df.shape}")
    return ruta


def exportar_excel(df, carpeta, nombre):
    ruta = carpeta / f"{nombre}.xlsx"
    df.to_excel(ruta, index=False, sheet_name="empresas")
    print(f"Generado Excel -> Ruta: {ruta} | Tamaño: {df.shape}")
    return ruta


def exportar_json(df, carpeta, nombre):
    ruta = carpeta / f"{nombre}.json"
    df.to_json(ruta, orient="records", force_ascii=False, indent=2)
    print(f"Generado JSON  -> Ruta: {ruta} | Tamaño: {df.shape}")
    return ruta


def exportar_datos(df):
    os.makedirs(CARPETA_CRUDO, exist_ok=True)
    return [
        exportar_csv(df, CARPETA_CRUDO, NOMBRE_ARCHIVO),
        exportar_excel(df, CARPETA_CRUDO, NOMBRE_ARCHIVO),
        exportar_json(df, CARPETA_CRUDO, NOMBRE_ARCHIVO),
    ]


if __name__ == "__main__":
    simulacion = import_module("simular_empresas")
    df_sucio = simulacion.generar_empresas()
    exportar_datos(df_sucio)