"""Limpieza de la tabla evidencias (HU L01).

Uso:
    python scripts/limpiar_evidencias.py evidencias_sucio.csv [salida.csv]

Si no se indica salida, guarda en data/limpio/evidencias_limpio.csv.
"""
import os
import sys

import pandas as pd

# Columnas que no pueden quedar con nulos despues de limpiar
COLUMNAS_OBLIGATORIAS = ["id_registro", "titulo", "url_archivo", "fecha_entrega", "estado", "calificacion"]
RUTA_SALIDA_DEFECTO = os.path.join("data", "limpio", "evidencias_limpio.csv")


def leer_datos(ruta):
    """Lee el CSV sucio con pandas y devuelve el DataFrame."""
    return pd.read_csv(ruta, dtype=str, keep_default_na=True)


def imprimir_diagnostico(df, titulo):
    """Imprime shape, info, nulos por columna y cantidad de duplicados exactos."""
    print(f"\n===== {titulo} =====")
    print("shape:", df.shape)
    print("\ninfo:")
    df.info()
    print("\nnulos por columna:")
    print(df.isna().sum())
    print("\nduplicados exactos:", df.duplicated().sum())


def quitar_duplicados_exactos(df):
    """Elimina las filas completamente iguales."""
    return df.drop_duplicates()


def limpiar_titulo(df):
    """Quita los espacios sobrantes al inicio y al final del titulo."""
    df["titulo"] = df["titulo"].str.strip()
    return df


def rellenar_descripcion(df):
    """Rellena las descripciones vacias con 'Sin descripcion'."""
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    return df


def marcar_url_valida(df):
    """Crea la columna url_valida: True si la URL empieza por 'http'."""
    df["url_valida"] = df["url_archivo"].str.startswith("http", na=False)
    return df


def convertir_fecha(df):
    """Convierte fecha_entrega a datetime aceptando varios formatos (dia primero)."""
    df["fecha_entrega"] = pd.to_datetime(
        df["fecha_entrega"], format="mixed", dayfirst=True, errors="coerce"
    )
    return df


def unificar_estado(df):
    """Unifica el estado: sin espacios sobrantes, mayusculas y guion bajo."""
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    return df


def limpiar_calificacion(df):
    """Convierte calificacion a numero (coma decimal), anula lo que queda
    fuera del rango 0-5 y rellena los nulos con la mediana."""
    df["calificacion"] = pd.to_numeric(
        df["calificacion"].astype(str).str.replace(",", "."), errors="coerce"
    )
    df.loc[(df["calificacion"] < 0) | (df["calificacion"] > 5), "calificacion"] = None
    df["calificacion"] = df["calificacion"].fillna(df["calificacion"].median())
    return df


def quitar_entregas_repetidas(df):
    """Detecta las entregas repetidas (mismo id_registro y url_archivo) y deja la primera."""
    repetidas = df[df.duplicated(subset=["id_registro", "url_archivo"], keep=False)]
    print("\nfilas en entregas repetidas:", len(repetidas))
    return df.drop_duplicates(subset=["id_registro", "url_archivo"], keep="first")


def crear_mes(df):
    """Crea la columna mes (periodo mensual) para agrupar despues."""
    df["mes"] = df["fecha_entrega"].dt.to_period("M")
    return df


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/limpiar_evidencias.py evidencias_sucio.csv [salida.csv]")
        sys.exit(1)
    ruta_entrada = sys.argv[1]
    ruta_salida = sys.argv[2] if len(sys.argv) > 2 else RUTA_SALIDA_DEFECTO

    df = leer_datos(ruta_entrada)
    filas_antes = len(df)
    imprimir_diagnostico(df, "ANTES DE LIMPIAR")

    df = quitar_duplicados_exactos(df)
    df = limpiar_titulo(df)
    df = rellenar_descripcion(df)
    df = marcar_url_valida(df)
    df = convertir_fecha(df)
    df = unificar_estado(df)
    df = limpiar_calificacion(df)
    df = quitar_entregas_repetidas(df)
    df = crear_mes(df)

    imprimir_diagnostico(df, "DESPUES DE LIMPIAR")
    print("\nfilas eliminadas:", filas_antes - len(df))

    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    df.to_csv(ruta_salida, index=False, encoding="utf-8")
    print("archivo guardado en:", ruta_salida)

    nulos = df[COLUMNAS_OBLIGATORIAS].isna().sum().sum()
    print("nulos en columnas obligatorias:", nulos, "| duplicados exactos:", df.duplicated().sum())


if __name__ == "__main__":
    main()