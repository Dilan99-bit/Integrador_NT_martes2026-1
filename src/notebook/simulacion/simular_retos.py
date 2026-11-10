# HU F01 - Simulacion de la tabla `retos` (la necesidad que publica la empresa).
# Genera 500 filas falsas con las MISMAS columnas que usa Backend II y despues
# las ENSUCIA a proposito para practicar la limpieza.

import random
import uuid
from datetime import timedelta

import pandas as pd
from faker import Faker

# 1. Constantes al inicio
SEMILLA = 42
FILAS = 500
PORCENTAJE_DUPLICADOS = 0.05

ESTADOS = ["ACTIVO", "INACTIVO", "RECHAZADO", "ACEPTADO", "EN ESPERA"]

# 2. Semilla fija y Faker en espanol de Colombia
Faker.seed(SEMILLA)
random.seed(SEMILLA)
fake = Faker("es_CO")

# 3. Listas fijas para las llaves foraneas (asi varios retos comparten empresa, etc.)
IDS_EMPRESA = [fake.uuid4() for _ in range(10)]
IDS_CATEGORIA = [fake.uuid4() for _ in range(5)]
IDS_PRIORIDAD = [fake.uuid4() for _ in range(3)]


def nuevo_uuid():
    """UUID v4 como texto. Usa random (con semilla) para que el resultado sea reproducible."""
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


# 4. Datos LIMPIOS
def generar_datos_limpios(numero_datos):
    filas = []
    for _ in range(numero_datos):
        fecha_inicio = fake.date_between(start_date="-1y", end_date="+3m")
        filas.append({
            "id": nuevo_uuid(),
            "nombre": fake.sentence(nb_words=6).rstrip("."),
            "descripcion": fake.sentence(nb_words=12),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })
    return pd.DataFrame(filas)


# 5. Ensuciar los datos
def generar_muestra(datos, porcentaje):
    """Devuelve el indice de un porcentaje de filas elegidas al azar (reproducible)."""
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 999)).index


def ensuciar(datos_df):
    datos_df = datos_df.copy()
    datos_df["fecha_inicio"] = pd.to_datetime(datos_df["fecha_inicio"])
    datos_df["fecha_fin"] = pd.to_datetime(datos_df["fecha_fin"])

    # nombre: 10% con espacios sobrantes
    filas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas, "nombre"] = " " + datos_df.loc[filas, "nombre"] + " "

    # descripcion: 12% en None (nulos)
    filas = generar_muestra(datos_df, 0.12)
    datos_df.loc[filas, "descripcion"] = None

    # fecha_fin: 8% en None y 5% ANTERIOR a fecha_inicio
    filas_nulas = generar_muestra(datos_df, 0.08)
    disponibles = datos_df.drop(index=filas_nulas)
    filas_anteriores = generar_muestra(disponibles, 0.05 / 0.92)
    datos_df.loc[filas_anteriores, "fecha_fin"] = [
        inicio - timedelta(days=random.randint(1, 180))
        for inicio in datos_df.loc[filas_anteriores, "fecha_inicio"]
    ]

    # fecha_inicio: dos formatos mezclados ("2026-03-02" y "02/03/2026")
    iso = datos_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino = datos_df["fecha_inicio"].dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = iso
    filas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas, "fecha_inicio"] = latino.loc[filas]

    datos_df["fecha_fin"] = datos_df["fecha_fin"].dt.strftime("%Y-%m-%d")
    datos_df.loc[filas_nulas, "fecha_fin"] = None

    # estado: variantes con diferencias de formato
    filas = datos_df.sample(n=3, random_state=random.randint(0, 999)).index
    datos_df.loc[filas, "estado"] = ["en_curso", "EN CURSO", " Cerrado "]

    return datos_df


def agregar_duplicados(datos_df, cantidad):
    """Repite `cantidad` filas tal cual (duplicados exactos)."""
    repetidas = datos_df.sample(n=cantidad, random_state=random.randint(0, 999))
    return pd.concat([datos_df, repetidas], ignore_index=True)


# 6. Funcion principal: devuelve el DataFrame para poder importarla desde exportar_retos.py
def generar_retos(n=FILAS):
    Faker.seed(SEMILLA)
    random.seed(SEMILLA)
    duplicados = int(n * PORCENTAJE_DUPLICADOS)          # 5% de las filas repetidas
    df = generar_datos_limpios(n - duplicados)           # filas unicas
    df = ensuciar(df)
    df = agregar_duplicados(df, duplicados)              # total = n filas
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())