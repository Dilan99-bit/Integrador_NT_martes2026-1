# HU X01 - Exportar la tabla `retos` sucia a CSV, Excel y JSON.
# Importa la funcion de simular_retos.py: NO se vuelve a copiar el codigo de generacion.

import os
from pathlib import Path

from src.notebook.simulacion.simular_retos import generar_retos

# 1. Configuracion
NOMBRE_ARCHIVO = "retos_sucio"
CARPETA_PROYECTO = Path(__file__).resolve().parents[3]   # src/ -> raiz del proyecto
CARPETA_CRUDO = CARPETA_PROYECTO / "data" / "crudo"


# 2. Funciones para cada formato
def exportar_csv(df, carpeta, nombre_archivo):
    ruta = carpeta / f"{nombre_archivo}.csv"
    df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def exportar_excel(df, carpeta, nombre_archivo):
    ruta = carpeta / f"{nombre_archivo}.xlsx"
    df.to_excel(ruta, index=False, sheet_name="retos")
    return ruta


def exportar_json(df, carpeta, nombre_archivo):
    ruta = carpeta / f"{nombre_archivo}.json"
    df.to_json(ruta, orient="records", force_ascii=False, indent=2)
    return ruta


# 3. Generar los tres archivos
def exportar_retos_crudos(df):
    os.makedirs(CARPETA_CRUDO, exist_ok=True)
    return [
        exportar_csv(df, CARPETA_CRUDO, NOMBRE_ARCHIVO),
        exportar_excel(df, CARPETA_CRUDO, NOMBRE_ARCHIVO),
        exportar_json(df, CARPETA_CRUDO, NOMBRE_ARCHIVO),
    ]


if __name__ == "__main__":
    df = generar_retos()
    for ruta in exportar_retos_crudos(df):
        print(f"{ruta} -> {df.shape}")