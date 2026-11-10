"""Consultas de la HU Q01 sobre la tabla registros (proyecto integrador).

Cada consulta está en su propia función, imprime qué pregunta responde y
devuelve un DataFrame. `ejecutar_consultas` corre las cinco en orden y guarda
cada resultado como registros_consulta_N.csv en la carpeta indicada.
"""
from pathlib import Path

import pandas as pd


def preparar(df):
    """Devuelve una copia con la columna 'mes' (AAAA-MM) calculada desde fecha_registro."""
    df = df.copy()
    if "mes" not in df.columns:
        fechas = pd.to_datetime(df["fecha_registro"], errors="coerce")
        df["mes"] = fechas.dt.to_period("M").astype(str)
    return df


def consulta_1(df):
    """Consulta 1: participaciones ya finalizadas."""
    print("\n=== Consulta 1: ¿Qué participaciones ya están finalizadas? ===")
    finalizados = df[df["estado"].str.upper() == "FINALIZADO"]
    print(finalizados.to_string(index=False))
    return finalizados


def consulta_2(df):
    """Consulta 2: participaciones repetidas (mismo usuario en el mismo reto)."""
    print("\n=== Consulta 2: ¿Qué participaciones están repetidas (mismo usuario y mismo reto)? ===")
    repetidos = df[df.duplicated(subset=["id_usuario", "id_reto"], keep=False)]
    repetidos = repetidos.sort_values(["id_usuario", "id_reto"])
    print(repetidos.to_string(index=False))
    return repetidos


def consulta_3(df):
    """Consulta 3: cuántas participaciones hay por estado."""
    print("\n=== Consulta 3: ¿Cuántas participaciones hay por estado? ===")
    conteo = df["estado"].value_counts().rename_axis("estado").reset_index(name="cantidad")
    print(conteo.to_string(index=False))
    return conteo


def consulta_4(df):
    """Consulta 4 (GROUPBY): los 10 retos con más participantes."""
    print("\n=== Consulta 4: ¿Cuáles son los 10 retos con más participantes? ===")
    top_retos = df.groupby("id_reto")["id"].count().nlargest(10)
    top_retos = top_retos.rename("participaciones").reset_index()
    print(top_retos.to_string(index=False))
    return top_retos


def consulta_5(df):
    """Consulta 5 (GROUPBY): cuántas participaciones hubo cada mes."""
    print("\n=== Consulta 5: ¿Cuántas participaciones hubo cada mes? ===")
    por_mes = df.groupby("mes")["id"].count().rename("participaciones").reset_index()
    print(por_mes.to_string(index=False))
    return por_mes


CONSULTAS = [consulta_1, consulta_2, consulta_3, consulta_4, consulta_5]


def ejecutar_consultas(df, carpeta_salida):
    """Corre las cinco consultas en orden; devuelve (resultados, rutas_csv)."""
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    df = preparar(df)

    resultados, rutas = [], []
    for n, consulta in enumerate(CONSULTAS, start=1):
        resultado = consulta(df)
        carpeta_consulta = carpeta_salida / f"consulta_{n}"
        carpeta_consulta.mkdir(parents=True, exist_ok=True)
        ruta = carpeta_consulta / f"registros_consulta_{n}.csv"
        resultado.to_csv(ruta, index=False, encoding="utf-8")
        print(f"-> guardado: {ruta}")
        resultados.append(resultado)
        rutas.append(ruta)
    return resultados, rutas