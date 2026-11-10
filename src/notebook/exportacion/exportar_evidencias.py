"""Exporta los datos sucios a CSV, Excel y JSON (HU X01)."""
import os
import sys
from importlib import import_module

# Carpeta de este script y raíz del proyecto, para encontrar el módulo de simulación
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
for carpeta in (AQUI, os.path.join(RAIZ, "src")):
    if carpeta not in sys.path:
        sys.path.insert(0, carpeta)

# Se importa la función del script de simulación; NO se copia el código de generación.
simulacion = import_module("simular_evidencias")
generar_evidencias = simulacion.generar_evidencias

CARPETA = os.path.join(RAIZ, "data", "crudo")


def exportar(df):
    """Guarda el DataFrame en CSV, XLSX y JSON dentro de data/crudo y devuelve las rutas."""
    os.makedirs(CARPETA, exist_ok=True)

    ruta_csv = os.path.join(CARPETA, "evidencias_sucio.csv")
    ruta_xlsx = os.path.join(CARPETA, "evidencias_sucio.xlsx")
    ruta_json = os.path.join(CARPETA, "evidencias_sucio.json")

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_excel(ruta_xlsx, index=False, sheet_name="evidencias")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    return [ruta_csv, ruta_xlsx, ruta_json]


if __name__ == "__main__":
    df = generar_evidencias(n=600)
    for ruta in exportar(df):
        print(f"{ruta} -> {df.shape}")