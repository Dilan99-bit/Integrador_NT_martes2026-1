import os
from pathlib import Path

from ..simulacion.simular_registro import generar_registros

# Configuración
NOMBRE_ENTIDAD = "registros"
CARPETA_PROYECTO = Path(__file__).resolve().parents[3]
CARPETA_CRUDO = CARPETA_PROYECTO / "data" / "crudo"


def preparar_carpeta(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def exportar_csv(df, carpeta, nombre):
    ruta = preparar_carpeta(carpeta) / f"{nombre}.csv"
    df.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def exportar_excel(df, carpeta, nombre):
    ruta = preparar_carpeta(carpeta) / f"{nombre}.xlsx"
    df.to_excel(ruta, index=False, sheet_name="registros")
    return ruta


def exportar_json(df, carpeta, nombre):
    ruta = preparar_carpeta(carpeta) / f"{nombre}.json"
    df.to_json(ruta, orient="records", force_ascii=False, indent=2)
    return ruta


if __name__ == "__main__":
    df = generar_registros()
    nombre = f"{NOMBRE_ENTIDAD}_sucio"

    rutas = [
        exportar_csv(df, CARPETA_CRUDO, nombre),
        exportar_excel(df, CARPETA_CRUDO, nombre),
        exportar_json(df, CARPETA_CRUDO, nombre),
    ]

    for ruta in rutas:
        print(f"{ruta} -> {df.shape}")