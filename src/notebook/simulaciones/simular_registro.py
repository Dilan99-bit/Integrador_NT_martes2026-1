import random
import uuid

import pandas as pd
from faker import Faker

# 1. Faker configurado para Colombia
fake = Faker("es_CO")

# 2. Semillas fijas para que el archivo sea reproducible
Faker.seed(42)
random.seed(42)

# 3. Constantes
ESTADOS = ["inscrito", "en proceso", "finalizado"]
IDS_USUARIO = [str(uuid.uuid4()) for _ in range(10)]
IDS_RETO = [str(uuid.uuid4()) for _ in range(10)]


# 4. Datos limpios
def generar_datos_limpios(n):
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "fecha_registro": fake.date_time_between(start_date="-1y", end_date="now"),
            "observacion": fake.sentence(nb_words=10),
            "estado": random.choice(ESTADOS),
            "id_usuario": random.choice(IDS_USUARIO),
            "id_reto": random.choice(IDS_RETO),
        })
    return pd.DataFrame(filas)


# 5. Funciones auxiliares para ensuciar
def generar_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 999)).index


def escribir_mal(texto):
    variantes = [texto.upper(), f" {texto.capitalize()} ", texto.title()]
    return random.choice(variantes)


def ensuciar(df):
    df = df.copy()

    # fecha_registro: dos formatos mezclados
    iso = df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")
    latino = df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")
    df["fecha_registro"] = iso
    filas = generar_muestra(df, 0.4)
    df.loc[filas, "fecha_registro"] = latino.loc[filas]

    # observacion: 20% nulos
    filas = generar_muestra(df, 0.2)
    df.loc[filas, "observacion"] = None

    # estado: variantes mal escritas
    filas = generar_muestra(df, 0.08)
    df.loc[filas, "estado"] = df.loc[filas, "estado"].map(escribir_mal)

    # 10% con el par id_usuario + id_reto repetido
    filas = generar_muestra(df, 0.10)
    origenes = list(df.index.difference(filas))
    for indice in filas:
        origen = random.choice(origenes)
        df.loc[indice, ["id_usuario", "id_reto"]] = df.loc[
            origen, ["id_usuario", "id_reto"]
        ]

    # 5% de filas duplicadas exactas
    filas = generar_muestra(df, 0.05)
    df = pd.concat([df, df.loc[filas].copy()], ignore_index=True)

    return df


# 6. Función principal, la que importa el script de exportación
def generar_registros(n=800):
    df = generar_datos_limpios(n)
    df = ensuciar(df)
    return df


if __name__ == "__main__":
    df = generar_registros()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())