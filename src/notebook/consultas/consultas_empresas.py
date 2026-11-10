"""Consultas sobre la tabla empresas del proyecto integrador (HU Q01 de Kaizen).

Uso:
    python consultas_empresas.py empresas_limpio.csv

Opcional: un segundo argumento con la carpeta base de salida
(por defecto data/limpio/consulta). Cada consulta se guarda en su propia
subcarpeta y en tres formatos:

    <carpeta>/consulta_N/empresas_consulta_N.csv
    <carpeta>/consulta_N/empresas_consulta_N.json
    <carpeta>/consulta_N/empresas_consulta_N.xlsx
"""
import os
import sys

import pandas as pd

# Carpeta base donde se guardan los resultados si no se indica otra.
CARPETA_SALIDA = os.path.join("data", "limpio", "consulta")

# Sector que se consulta en la consulta 2.
SECTOR_CONSULTA = "Logistica"

# Valores de texto que se convierten a booleano si "activa" llega como texto.
MAPA_ACTIVA = {
    "TRUE": True, "SI": True, "1": True,
    "FALSE": False, "NO": False, "0": False,
}


def leer_datos(ruta):
    """Lee empresas_limpio.csv con pandas. Todo entra como texto (dtype=str)
    para no perder ceros del nit ni del telefono, y luego 'activa' se
    convierte a booleano de verdad."""
    df = pd.read_csv(ruta, dtype=str)
    df["activa"] = (
        df["activa"].astype(str).str.strip().str.upper().map(MAPA_ACTIVA)
    )
    return df


def guardar(resultado, numero, carpeta, con_indice):
    """Guarda el resultado en <carpeta>/consulta_N/ en tres formatos:
    csv, json y xlsx. Si el resultado tiene indice con significado (sector),
    se pasa a columna para que quede igual en los tres formatos."""
    carpeta_consulta = os.path.join(carpeta, f"consulta_{numero}")
    os.makedirs(carpeta_consulta, exist_ok=True)

    tabla = resultado.reset_index() if con_indice else resultado.copy()
    tabla.columns = [str(c) for c in tabla.columns]
    tabla.columns.name = None

    base = os.path.join(carpeta_consulta, f"empresas_consulta_{numero}")
    tabla.to_csv(base + ".csv", index=False, encoding="utf-8")
    tabla.to_json(base + ".json", orient="records", force_ascii=False, indent=2)
    tabla.to_excel(base + ".xlsx", index=False)
    print(f"(guardado en {carpeta_consulta}: csv, json y xlsx)")


def consulta_1_activas(df, carpeta):
    """Consulta 1: que empresas estan activas. Filtra activa == True."""
    print("\n=== CONSULTA 1: ¿Cuáles son las empresas activas? ===")
    activas = df[df["activa"] == True]  # noqa: E712
    print(activas.to_string(index=False))
    print(f"Total: {len(activas)}")
    guardar(activas, 1, carpeta, con_indice=False)
    return activas


def consulta_2_sector(df, carpeta, sector=SECTOR_CONSULTA):
    """Consulta 2: que empresas son de un sector, ordenadas por nombre."""
    print(f"\n=== CONSULTA 2: ¿Cuáles son las empresas del sector "
          f"{sector}, ordenadas por nombre? ===")
    resultado = df[df["sector"] == sector].sort_values("nombre")
    print(resultado.to_string(index=False))
    print(f"Total: {len(resultado)}")
    guardar(resultado, 2, carpeta, con_indice=False)
    return resultado


def consulta_3_conteo(df, carpeta):
    """Consulta 3: cuantas empresas hay por sector (conteo rapido con
    value_counts)."""
    print("\n=== CONSULTA 3: ¿Cuántas empresas hay por sector "
          "(conteo rápido)? ===")
    conteo = df["sector"].value_counts().rename("cantidad")
    conteo.index.name = "sector"
    print(conteo.to_string())
    guardar(conteo, 3, carpeta, con_indice=True)
    return conteo


def consulta_4_groupby(df, carpeta):
    """Consulta 4 (GROUPBY): empresas por sector, de mayor a menor."""
    print("\n=== CONSULTA 4 (groupby): ¿Cuántas empresas hay por sector, "
          "de mayor a menor? ===")
    por_sector = (
        df.groupby("sector")["id"].count()
        .sort_values(ascending=False)
        .rename("cantidad")
    )
    print(por_sector.to_string())
    guardar(por_sector, 4, carpeta, con_indice=True)
    return por_sector


def consulta_5_groupby_doble(df, carpeta):
    """Consulta 5 (GROUPBY doble): empresas activas e inactivas por sector.
    En la tabla, False = inactivas y True = activas."""
    print("\n=== CONSULTA 5 (groupby doble): ¿Cuántas empresas activas e "
          "inactivas hay por sector? ===")
    tabla = df.groupby(["sector", "activa"])["id"].count().unstack(fill_value=0)
    print(tabla.to_string())
    guardar(tabla, 5, carpeta, con_indice=True)
    return tabla


def main():
    """Lee el CSV limpio y ejecuta las cinco consultas en orden."""
    if len(sys.argv) < 2:
        raise SystemExit(
            "Uso: python consultas_empresas.py empresas_limpio.csv"
        )
    ruta_entrada = sys.argv[1]
    carpeta = sys.argv[2] if len(sys.argv) > 2 else CARPETA_SALIDA

    df = leer_datos(ruta_entrada)
    print(f"Archivo leído: {ruta_entrada} ({df.shape[0]} filas)")

    consulta_1_activas(df, carpeta)
    consulta_2_sector(df, carpeta)
    consulta_3_conteo(df, carpeta)
    consulta_4_groupby(df, carpeta)
    consulta_5_groupby_doble(df, carpeta)


if __name__ == "__main__":
    main()