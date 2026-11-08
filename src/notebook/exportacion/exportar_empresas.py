"""Etapa 2 - Exportación de empresas_sucio a CSV, XLSX y JSON (HU X01).

Ubicación: src/notebook/exportacion/exportar_empresas.py
Uso:       python src/notebook/exportacion/exportar_empresas.py
"""

import os
import sys
from importlib import import_module
from pathlib import Path

# 'simular_empresas' está en la carpeta hermana src/notebook/simulacion; así se importa sin importar desde dónde se ejecute
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulacion"))

# --- Configuración ---
NOMBRE_ARCHIVO = "empresas_sucio"
CARPETA_PROYECTO = Path(__file__).resolve().parents[3]   # exportacion -> notebook -> src -> raíz del proyecto
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