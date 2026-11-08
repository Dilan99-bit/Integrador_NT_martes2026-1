"""Limpieza de la tabla registros del proyecto integrador (HU L01 de Kaizen).

Uso:
    python scripts/limpiar_registros.py registros_sucio.csv

Lee el CSV sucio, imprime el diagnóstico, corrige los errores, imprime el
diagnóstico otra vez y guarda registros_limpio.csv junto al archivo de entrada.
"""

import os
import re
import sys

import pandas as pd

# Textos que en realidad significan "dato ausente".
VALORES_NULOS = {"", "n/a", "na", "nan", "null", "none", "-", "--", "?", "sin dato", "s/d"}

# Rangos válidos para detectar valores imposibles.
EDAD_MIN, EDAD_MAX = 0, 120

# Texto con el que se rellenan los nulos de las columnas de texto.
TEXTO_SIN_DATO = "Sin dato"


def leer_datos(ruta):
    """Lee el CSV sucio con pandas y devuelve un DataFrame."""
    return pd.read_csv(ruta, encoding="utf-8")


def diagnostico(df, titulo):
    """Imprime el diagnóstico del DataFrame: shape, info, nulos y duplicados."""
    print("=" * 60)
    print(f"DIAGNÓSTICO {titulo}")
    print("=" * 60)
    print(f"Shape: {df.shape}")
    print("\nInfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print(f"\nFilas duplicadas: {df.duplicated().sum()}")
    print()


def normalizar_columnas(df):
    """Deja los nombres de columnas en minúsculas, sin espacios extremos y con guion bajo."""
    df = df.copy()
    df.columns = [re.sub(r"\s+", "_", str(c).strip().lower()) for c in df.columns]
    return df


def limpiar_texto(df):
    """Quita espacios sobrantes en las columnas de texto y convierte los marcadores de ausencia en nulos."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
        serie = df[col].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        serie = serie.mask(serie.str.lower().isin(VALORES_NULOS), pd.NA)
        df[col] = serie
    return df


def estandarizar_categorias(df):
    """Unifica mayúsculas/minúsculas: nombre y ciudad en Título, email y estado en minúscula."""
    df = df.copy()
    for col in ("nombre", "ciudad"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.title()
    for col in ("email", "estado"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.lower()
    return df


def convertir_numero(valor):
    """Convierte un texto como '$1.200,50' o '1,200.50' en float; devuelve NaN si no se puede."""
    if pd.isna(valor):
        return float("nan")
    texto = re.sub(r"[^\d,.\-]", "", str(valor))
    if not texto:
        return float("nan")
    if "," in texto and "." in texto:
        # El último separador es el decimal.
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        if len(partes) == 2 and len(partes[1]) <= 2:
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif texto.count(".") > 1 or (texto.count(".") == 1 and len(texto.split(".")[1]) == 3):
        # Un punto seguido de exactamente 3 dígitos se toma como separador de miles.
        texto = texto.replace(".", "")
    try:
        return float(texto)
    except ValueError:
        return float("nan")


def convertir_tipos(df):
    """Convierte monto y edad a numérico y fecha_registro a fecha (formato AAAA-MM-DD)."""
    df = df.copy()
    if "monto" in df.columns:
        df["monto"] = df["monto"].map(convertir_numero)
    if "edad" in df.columns:
        df["edad"] = df["edad"].map(convertir_numero)
    if "fecha_registro" in df.columns:
        df["fecha_registro"] = convertir_fechas(df["fecha_registro"])
    return df


def convertir_fechas(serie):
    """Convierte fechas mixtas con formatos explícitos: AAAA-MM-DD HH:MM:SS y DD/MM/AAAA HH:MM."""
    texto = serie.astype("string").str.strip()
    iso = pd.to_datetime(texto, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    dmy = pd.to_datetime(texto.where(iso.isna()), format="%d/%m/%Y %H:%M", errors="coerce")
    return iso.fillna(dmy)


def corregir_valores_imposibles(df):
    """Convierte en nulo lo que no tiene sentido: edades fuera de rango, montos negativos y fechas futuras."""
    df = df.copy()
    if "edad" in df.columns:
        df.loc[(df["edad"] < EDAD_MIN) | (df["edad"] > EDAD_MAX), "edad"] = float("nan")
    if "monto" in df.columns:
        df.loc[df["monto"] < 0, "monto"] = float("nan")
    if "fecha_registro" in df.columns:
        df.loc[df["fecha_registro"] > pd.Timestamp.today(), "fecha_registro"] = pd.NaT
    return df


def tratar_nulos(df):
    """Rellena nulos: mediana en numéricos y 'Sin dato' en texto; las fechas nulas se dejan vacías."""
    df = df.copy()
    for col in df.columns:
        if col == "id":
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            df[col] = df[col].fillna(TEXTO_SIN_DATO)
    return df


def eliminar_duplicados(df):
    """Elimina filas sin id, filas duplicadas exactas y registros repetidos por id (se conserva el primero)."""
    df = df.copy()
    if "id" in df.columns:
        df = df.dropna(subset=["id"])
    df = df.drop_duplicates()
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"], keep="first")
    return df.reset_index(drop=True)


def formatear_salida(df):
    """Prepara tipos finales: id y edad enteros, y fechas como texto AAAA-MM-DD."""
    df = df.copy()
    # Los id de esta tabla son UUID (texto): no se convierten a número.
    if "edad" in df.columns:
        df["edad"] = df["edad"].round().astype("Int64")
    if "fecha_registro" in df.columns:
        df["fecha_registro"] = df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def limpiar(df):
    """Aplica todos los pasos de limpieza en orden y devuelve el DataFrame limpio."""
    df = normalizar_columnas(df)
    df = limpiar_texto(df)
    df = estandarizar_categorias(df)
    df = convertir_tipos(df)
    df = corregir_valores_imposibles(df)
    df = eliminar_duplicados(df)
    df = tratar_nulos(df)
    return formatear_salida(df)


def main():
    """Punto de entrada: lee, diagnostica, limpia, diagnostica otra vez y guarda registros_limpio.csv."""
    if len(sys.argv) != 2:
        print("Uso: python scripts/limpiar_registros.py registros_sucio.csv")
        sys.exit(1)

    ruta_entrada = sys.argv[1]
    if not os.path.exists(ruta_entrada):
        print(f"No existe el archivo: {ruta_entrada}")
        sys.exit(1)

    df_sucio = leer_datos(ruta_entrada)
    diagnostico(df_sucio, "ANTES DE LIMPIAR")

    df_limpio = limpiar(df_sucio)
    diagnostico(df_limpio, "DESPUÉS DE LIMPIAR")

    eliminadas = len(df_sucio) - len(df_limpio)
    print(f"Filas antes: {len(df_sucio)} | después: {len(df_limpio)} | eliminadas: {eliminadas}")

    carpeta = os.path.dirname(os.path.abspath(ruta_entrada))
    ruta_salida = os.path.join(carpeta, "registros_limpio.csv")
    df_limpio.to_csv(ruta_salida, index=False, encoding="utf-8")
    print(f"Archivo limpio guardado en: {ruta_salida}")


if __name__ == "__main__":
    main()