"""Limpia la tabla empresas del proyecto integrador (HU L01 de Kaizen).

Estructura esperada del proyecto:

    proyecto/
    |-- data/
    |   |-- crudo/    empresas_sucio.csv (.json, .xlsx)
    |   `-- limpio/   aqui se guardan los tres archivos limpios
    `-- src/
        `-- notebook/
            `-- limpieza/
                `-- limpiar_empresas.py

Normalmente se corre desde main.py en la raiz del proyecto (python main.py limpiar).
Uso directo (desde la raiz del proyecto o desde cualquier otra carpeta):
    python src/notebook/limpieza/limpiar_empresas.py
    python src/notebook/limpieza/limpiar_empresas.py data/crudo/empresas_sucio.json
    python src/notebook/limpieza/limpiar_empresas.py ruta/entrada.xlsx ruta/carpeta_salida

Sin argumentos lee data/crudo/empresas_sucio.csv y guarda en data/limpio:
empresas_limpio.csv, empresas_limpio.json y empresas_limpio.xlsx.
"""
import sys
from pathlib import Path

import pandas as pd

def encontrar_raiz():
    """Sube desde la carpeta del script hasta encontrar la carpeta que
    contiene data/ (la raiz del proyecto). Asi funciona sin importar a
    cuantos niveles dentro de src/ este el script."""
    for carpeta in Path(__file__).resolve().parents:
        if (carpeta / "data").is_dir():
            return carpeta
    return Path.cwd()


RAIZ = encontrar_raiz()
ENTRADA_POR_DEFECTO = RAIZ / "data" / "crudo" / "empresas_sucio.csv"
SALIDA_POR_DEFECTO = RAIZ / "data" / "limpio"
NOMBRE_BASE = "empresas_limpio"

# Valores de texto que se convierten a booleano en la columna "activa".
MAPA_ACTIVA = {
    "TRUE": True, "SI": True, "1": True,
    "FALSE": False, "NO": False, "0": False,
}


def leer_datos(ruta):
    """Lee el archivo sucio (csv, json o xlsx) con pandas. Todo entra como
    texto para no perder ceros a la izquierda en el nit ni en el telefono."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise SystemExit(f"ERROR: no existe el archivo {ruta}")
    ext = ruta.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(ruta, dtype=str)
    if ext == ".json":
        return pd.read_json(ruta, dtype=False, convert_dates=False)
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(ruta, dtype=str)
    raise SystemExit(f"ERROR: formato no soportado: {ext} (usa csv, json o xlsx)")


def imprimir_diagnostico(df, titulo):
    """Imprime el diagnostico: shape, info, nulos por columna y duplicados."""
    print(f"\n===== {titulo} =====")
    print("df.shape:", df.shape)
    print("\ndf.info():")
    df.info()
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print("\ndf.duplicated().sum():", df.duplicated().sum())


def limpiar(df):
    """Aplica las correcciones de los criterios, en el orden de Kaizen."""
    df = df.copy()
    df = df.drop_duplicates().reset_index(drop=True)

    df["nombre"] = df["nombre"].str.strip()
    df["sector"] = df["sector"].str.strip().str.title()
    df["nit"] = df["nit"].str.replace(r"[.\-]", "", regex=True)
    df["telefono"] = df["telefono"].str.replace(r"\D", "", regex=True)
    df["activa"] = (
        df["activa"].astype(str).str.strip().str.upper().map(MAPA_ACTIVA)
    )
    df["contacto"] = df["contacto"].fillna("Sin contacto")
    df["correo_valido"] = df["correo"].str.contains("@", na=False)

    # La limpieza puede volver iguales filas que antes diferian solo por
    # espacios o formato: se quitan los duplicados otra vez.
    return df.drop_duplicates().reset_index(drop=True)


def verificar(df):
    """Detiene el programa si queda algun nulo o duplicado exacto."""
    nulos = int(df.isna().sum().sum())
    duplicados = int(df.duplicated().sum())
    if nulos or duplicados:
        raise SystemExit(
            f"ERROR: quedaron {nulos} nulos y {duplicados} duplicados."
        )
    print("\nVerificacion OK: 0 nulos y 0 duplicados exactos.")


def guardar(df, carpeta):
    """Guarda empresas_limpio en csv, json y xlsx. Devuelve las rutas."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_csv = carpeta / f"{NOMBRE_BASE}.csv"
    ruta_json = carpeta / f"{NOMBRE_BASE}.json"
    ruta_xlsx = carpeta / f"{NOMBRE_BASE}.xlsx"

    df.to_csv(ruta_csv, index=False, encoding="utf-8")
    df.to_json(ruta_json, orient="records", force_ascii=False, indent=2)
    df.to_excel(ruta_xlsx, index=False, sheet_name="empresas")
    return [ruta_csv, ruta_json, ruta_xlsx]


def ejecutar(ruta_entrada=ENTRADA_POR_DEFECTO, carpeta_salida=SALIDA_POR_DEFECTO):
    """Lee, diagnostica, limpia, vuelve a diagnosticar y guarda los tres
    archivos limpios. Se puede llamar desde main.py. Devuelve el DataFrame."""
    df = leer_datos(ruta_entrada)
    filas_antes = df.shape[0]
    imprimir_diagnostico(df, "DIAGNOSTICO ANTES DE LIMPIAR")

    df = limpiar(df)

    print("\n===== DIAGNOSTICO DESPUES DE LIMPIAR =====")
    print("df.shape:", df.shape)
    print("\ndf.isna().sum():")
    print(df.isna().sum())
    print(f"\nFilas eliminadas: {filas_antes - df.shape[0]} "
          f"({filas_antes} -> {df.shape[0]})")
    print("Correos invalidos marcados:", int((~df["correo_valido"]).sum()))

    verificar(df)
    for ruta in guardar(df, carpeta_salida):
        print("Archivo guardado en:", ruta)
    return df


def main():
    """Uso por consola: python src/notebook/limpieza/limpiar_empresas.py
    [entrada] [carpeta_salida]"""
    ruta_entrada = Path(sys.argv[1]) if len(sys.argv) > 1 else ENTRADA_POR_DEFECTO
    carpeta = Path(sys.argv[2]) if len(sys.argv) > 2 else SALIDA_POR_DEFECTO
    ejecutar(ruta_entrada, carpeta)


if __name__ == "__main__":
    main()
