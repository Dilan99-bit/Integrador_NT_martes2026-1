import random
import uuid

import numpy as np
import pandas as pd
from faker import Faker

# 1. Configurar Faker para Colombia
faker = Faker("es_CO")

# 2. Semillas fijas para que los datos sean reproducibles
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# 3. Datos a simular:
# id (UUID), titulo (texto), descripcion (texto), url_archivo (texto),
# fecha_entrega (fecha y hora), estado (texto), calificacion (decimal 0 a 5),
# id_registro (UUID)

# 4. Constantes
FILAS = 600
ESTADOS = ["enviada", "en revision", "aprobada"]
IDS_REGISTRO = [str(uuid.uuid4()) for _ in range(50)]


def generar_datos_limpios(numero_datos=FILAS):
    """Genera las filas limpias de evidencias y las devuelve como lista de diccionarios."""
    filas = []
    for _ in range(numero_datos):
        filas.append({
            "id": str(uuid.uuid4()),
            "titulo": faker.sentence(nb_words=5).rstrip("."),
            "descripcion": faker.sentence(nb_words=12),
            "url_archivo": faker.url() + faker.file_name(category="office"),
            "fecha_entrega": faker.date_time_between(start_date="-1y", end_date="now"),
            "estado": random.choice(ESTADOS),
            "calificacion": round(random.uniform(0, 5), 1),
            "id_registro": random.choice(IDS_REGISTRO),
        })
    return filas


def generar_muestra(datos, porcentaje):
    """Devuelve los índices de una muestra aleatoria con el porcentaje indicado (0 a 1)."""
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 999)).index


def ensuciar(datos_df):
    """Mete errores a los datos limpios: espacios, nulos, formatos mezclados, fuera de rango y duplicados."""
    df = datos_df.copy()
    df["calificacion"] = df["calificacion"].astype(object)

    # titulo: 10% con espacios sobrantes, 8% en mayúscula
    filas = generar_muestra(df, 0.10)
    df.loc[filas, "titulo"] = "  " + df.loc[filas, "titulo"] + "  "
    filas = generar_muestra(df, 0.08)
    df.loc[filas, "titulo"] = df.loc[filas, "titulo"].str.upper()

    # descripcion: 15% nulos
    filas = generar_muestra(df, 0.15)
    df.loc[filas, "descripcion"] = None

    # url_archivo: 8% sin http/https
    filas = generar_muestra(df, 0.08)
    df.loc[filas, "url_archivo"] = df.loc[filas, "url_archivo"].str.replace(
        r"^https?://", "", regex=True
    )

    # fecha_entrega: mezclar 2 formatos
    df["fecha_entrega"] = pd.to_datetime(df["fecha_entrega"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    filas = generar_muestra(df, 0.5)
    df.loc[filas, "fecha_entrega"] = pd.to_datetime(
        df.loc[filas, "fecha_entrega"]
    ).dt.strftime("%d/%m/%Y %H:%M")

    # estado: variantes mal escritas en todas las filas
    df["estado"] = [random.choice(["enviada", "EN REVISION", "Aprobada"]) for _ in range(len(df))]

    # calificacion: 6% nulos, 4% fuera de rango, 5% con coma como texto
    filas = generar_muestra(df, 0.06)
    df.loc[filas, "calificacion"] = None
    filas = generar_muestra(df, 0.04)
    df.loc[filas, "calificacion"] = [random.choice([-1, 8.0]) for _ in range(len(filas))]
    filas = [i for i in generar_muestra(df, 0.05) if pd.notna(df.loc[i, "calificacion"])]
    df.loc[filas, "calificacion"] = df.loc[filas, "calificacion"].astype(str).str.replace(".", ",")

    # id_registro + url_archivo repetidos: 10%
    filas = generar_muestra(df, 0.10)
    df.loc[filas, "id_registro"] = df.loc[df.index[0], "id_registro"]
    df.loc[filas, "url_archivo"] = df.loc[df.index[0], "url_archivo"]

    # Duplicados exactos: 5%
    duplicados = df.sample(frac=0.05, random_state=random.randint(0, 999))
    df = pd.concat([df, duplicados], ignore_index=True)

    return df


def generar_evidencias(n=FILAS):
    """Genera y ensucia las evidencias; devuelve el DataFrame para usarlo desde otros scripts."""
    df = ensuciar(pd.DataFrame(generar_datos_limpios(n)))
    return df


if __name__ == "__main__":
    df = generar_evidencias(n=600)
    print("Forma:", df.shape)
    print("\nPrimeras filas:")
    print(df.head())
    print("\nDatos vacíos por columna:")
    print(df.isna().sum())