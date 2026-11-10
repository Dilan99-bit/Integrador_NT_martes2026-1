"""Limpieza de la tabla retos del proyecto integrador (HU L01 de Kaizen).

Uso (desde cualquier carpeta):
    python src/notebook/limpieza/limpiar_retos.py

Lee data/crudo/retos_sucio.csv, imprime el diagnostico, corrige los errores,
imprime el diagnostico otra vez y guarda data/limpio/retos_limpio.csv
(ademas del .xlsx y el .json con el mismo contenido).
"""

import sys
from pathlib import Path

import pandas as pd

# src/notebook/limpieza/limpiar_retos.py -> parents[3] es la raiz del proyecto
CARPETA_PROYECTO = Path(__file__).resolve().parents[3]
RUTA_ENTRADA = CARPETA_PROYECTO / "data" / "crudo" / "retos_sucio.csv"
CARPETA_LIMPIO = CARPETA_PROYECTO / "data" / "limpio"
RUTA_SALIDA = CARPETA_LIMPIO / "retos_limpio.csv"

# Columnas que deben existir en el archivo de entrada (las de la tabla retos).
COLUMNAS_ESPERADAS = [
    "id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
    "estado", "id_empresa", "id_categoria", "id_prioridad",
]

# Obligatorias: no pueden quedar con nulos. (La descripcion se rellena y las
# fechas incoherentes o faltantes se marcan en fecha_valida, no se borran.)
COLUMNAS_OBLIGATORIAS = [
    "id", "nombre", "fecha_inicio", "estado",
    "id_empresa", "id_categoria", "id_prioridad",
]


def leer_csv(ruta):
    """Lee el CSV sucio con pd.read_csv() y verifica que tenga las columnas esperadas."""
    try:
        df = pd.read_csv(ruta)
    except FileNotFoundError:
        sys.exit(f"Error: no se encontro el archivo '{ruta}'.")
    faltantes = [c for c in COLUMNAS_ESPERADAS if c not in df.columns]
    if faltantes:
        sys.exit(f"Error: faltan las columnas {faltantes} en '{ruta}'.")
    return df


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnostico: shape, info, nulos por columna y duplicados exactos."""
    print("=" * 60)
    print(f"DIAGNOSTICO {titulo}")
    print("=" * 60)
    print(f"shape: {df.shape}")
    print("\ninfo:")
    df.info()
    print("\nNulos por columna:")
    print(df.isna().sum())
    print(f"\nDuplicados exactos: {df.duplicated().sum()}\n")


def quitar_duplicados(df):
    """Elimina las filas duplicadas exactas con df.drop_duplicates()."""
    return df.drop_duplicates()


def convertir_fechas(df):
    """Convierte fecha_inicio y fecha_fin a datetime aunque vengan en dos formatos.

    Con dayfirst=True, pandas puede leer mal las fechas ISO (2026-03-02). Por eso
    primero se leen las ISO (AAAA-MM-DD) con su formato exacto y solo las que quedan
    (DD/MM/AAAA) se leen con format="mixed", dayfirst=True. Lo ilegible queda NaT.
    """
    for col in ["fecha_inicio", "fecha_fin"]:
        iso = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
        resto = pd.to_datetime(df[col], format="mixed", dayfirst=True, errors="coerce")
        df[col] = iso.fillna(resto)
    return df


def unificar_estado(df):
    """Unifica el estado: sin espacios en los bordes, MAYUSCULAS y guion bajo."""
    df["estado"] = df["estado"].str.strip().str.upper().str.replace(" ", "_")
    return df


def rellenar_descripciones(df):
    """Rellena las descripciones vacias (nulas o solo espacios) con 'Sin descripcion'."""
    vacias = df["descripcion"].isna() | (df["descripcion"].astype("string").str.strip() == "")
    df.loc[vacias, "descripcion"] = pd.NA
    df["descripcion"] = df["descripcion"].fillna("Sin descripcion")
    return df


def crear_duracion(df):
    """Crea duracion_dias = fecha_fin - fecha_inicio, en dias."""
    df["duracion_dias"] = (df["fecha_fin"] - df["fecha_inicio"]).dt.days.astype("Int64")
    return df


def marcar_fechas_incoherentes(df):
    """Crea fecha_valida (False si el fin es anterior al inicio o falta una fecha).

    Devuelve el DataFrame, las filas con fin ANTES que inicio y las que no tienen fecha_fin.
    """
    df["fecha_valida"] = (df["duracion_dias"] >= 0).fillna(False).astype(bool)
    fin_antes = int((df["duracion_dias"] < 0).sum())
    sin_fecha = int(df["duracion_dias"].isna().sum())
    return df, fin_antes, sin_fecha


def quitar_filas_sin_obligatorios(df):
    """Elimina las filas con nulos en las columnas obligatorias (no se pueden recuperar)."""
    return df.dropna(subset=COLUMNAS_OBLIGATORIAS)


def verificar_resultado(df):
    """Comprueba que no queden nulos obligatorios ni duplicados exactos."""
    nulos = int(df[COLUMNAS_OBLIGATORIAS].isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    assert nulos == 0, f"Quedan {nulos} nulos en columnas obligatorias"
    assert duplicados == 0, f"Quedan {duplicados} duplicados exactos"
    print("Verificacion OK: sin nulos obligatorios y sin duplicados exactos.")


def guardar_limpio(df):
    """Guarda retos_limpio.csv (UTF-8, sin indice) y, ademas, .xlsx y .json."""
    CARPETA_LIMPIO.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_SALIDA, index=False, encoding="utf-8")
    df.to_excel(CARPETA_LIMPIO / "retos_limpio.xlsx", index=False, sheet_name="retos")
    para_json = df.copy()
    for col in ["fecha_inicio", "fecha_fin"]:
        para_json[col] = para_json[col].dt.strftime("%Y-%m-%d")
    para_json.to_json(CARPETA_LIMPIO / "retos_limpio.json",
                      orient="records", force_ascii=False, indent=2)


def main():
    """Ejecuta todo el flujo: leer, diagnosticar, limpiar, diagnosticar y guardar."""
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA_ENTRADA
    df = leer_csv(ruta)
    filas_inicio = len(df)
    nulos_antes = df.isna().sum()

    imprimir_diagnostico(df, "ANTES DE LIMPIAR")

    # Limpieza, en el orden de los criterios.
    df = quitar_duplicados(df)
    df = convertir_fechas(df)
    df = unificar_estado(df)
    df = rellenar_descripciones(df)
    df = crear_duracion(df)
    df, fin_antes, sin_fecha = marcar_fechas_incoherentes(df)
    df = quitar_filas_sin_obligatorios(df)
    # Tras unificar el estado pueden aparecer duplicados nuevos: se quitan otra vez.
    df = quitar_duplicados(df)

    imprimir_diagnostico(df, "DESPUES DE LIMPIAR")

    nulos_despues = df.isna().sum()
    print("Nulos corregidos por columna (antes -> despues):")
    for col in COLUMNAS_ESPERADAS:
        print(f"  {col}: {nulos_antes[col]} -> {nulos_despues[col]}")
    print(f"\nFilas con fecha_fin ANTERIOR a fecha_inicio: {fin_antes}")
    print(f"Filas sin fecha_fin (no se puede calcular la duracion): {sin_fecha}")
    print(f"Filas con fecha_valida = False (total): {int((~df['fecha_valida']).sum())}")
    print(f"Filas eliminadas: {filas_inicio - len(df)} (de {filas_inicio} a {len(df)})")

    verificar_resultado(df)
    guardar_limpio(df)
    print(f"Archivos limpios guardados en: {CARPETA_LIMPIO}")


if __name__ == "__main__":
    main()