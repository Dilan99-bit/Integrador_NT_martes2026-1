"""Etapa 1 - Simulación de la tabla empresas con Faker (HU F01).

Genera datos realistas y los ENSUCIA a propósito, para que la etapa 3
(limpieza con pandas) tenga trabajo de verdad.
"""

import random
import uuid

import numpy as np
import pandas as pd
from faker import Faker

# --- Constantes ---
SEMILLA = 42
SECTORES = ["Manufactura", "Servicios", "Comercio", "Tecnología",
            "Agroindustria", "Construcción", "Salud", "Educación"]

# --- Reproducibilidad: SIEMPRE antes de crear el objeto fake ---
Faker.seed(SEMILLA)
random.seed(SEMILLA)

fake = Faker("es_CO")


def ensuciar(df: pd.DataFrame) -> pd.DataFrame:
    """Introduce defectos controlados. Devuelve una copia sucia."""
    sucio = df.copy()

    # 1) 'nombre': 10% con espacios sobrantes, 15% en MAYUSCULAS
    idx = sucio.sample(frac=0.10, random_state=SEMILLA + 2).index
    sucio.loc[idx, "nombre"] = "  " + sucio.loc[idx, "nombre"].astype(str) + " "
    idx = sucio.sample(frac=0.15, random_state=SEMILLA + 3).index
    sucio.loc[idx, "nombre"] = sucio.loc[idx, "nombre"].astype(str).str.upper()

    # 2) 'nit': mitad con formato (900.123.456-7) y mitad sin formato (9001234567)
    nit_limpio = sucio["nit"].astype(str).str.replace(r"\D", "", regex=True)
    idx_1 = sucio.sample(frac=0.5, random_state=SEMILLA + 4).index
    sucio.loc[idx_1, "nit"] = (
        nit_limpio.loc[idx_1].str[:3] + "."
        + nit_limpio.loc[idx_1].str[3:6] + "."
        + nit_limpio.loc[idx_1].str[6:9] + "-"
        + nit_limpio.loc[idx_1].str[9:]
    )
    idx_2 = sucio.index.difference(idx_1)
    sucio.loc[idx_2, "nit"] = nit_limpio.loc[idx_2]

    # 3) 'sector': variantes con espacios sobrantes y en MAYUSCULAS
    idx = sucio.sample(frac=0.10, random_state=SEMILLA + 5).index
    sucio.loc[idx, "sector"] = "  " + sucio.loc[idx, "sector"].astype(str).str.lower() + "  "
    idx = sucio.sample(frac=0.15, random_state=SEMILLA + 6).index
    sucio.loc[idx, "sector"] = sucio.loc[idx, "sector"].astype(str).str.upper()

    # 4) 'contacto': 8% nulos
    idx = sucio.sample(frac=0.08, random_state=SEMILLA).index
    sucio.loc[idx, "contacto"] = np.nan

    # 5) 'correo': 6% sin la arroba (correo inválido)
    idx = sucio.sample(frac=0.06, random_state=SEMILLA + 7).index
    sucio.loc[idx, "correo"] = sucio.loc[idx, "correo"].astype(str).str.replace("@", "")

    # 6) 'telefono': tres formatos mezclados
    tel_limpio = sucio["telefono"].astype(str).str.replace(r"\D", "", regex=True).str[-10:]
    sucio["telefono"] = tel_limpio
    idx = sucio.sample(frac=0.33, random_state=SEMILLA + 8).index
    sucio.loc[idx, "telefono"] = (
        tel_limpio.loc[idx].str[:3] + " "
        + tel_limpio.loc[idx].str[3:6] + " "
        + tel_limpio.loc[idx].str[6:]
    )
    idx = sucio.sample(frac=0.33, random_state=SEMILLA + 9).index
    sucio.loc[idx, "telefono"] = (
        "+57 "
        + tel_limpio.loc[idx].str[:3] + "-"
        + tel_limpio.loc[idx].str[3:6] + "-"
        + tel_limpio.loc[idx].str[6:]
    )

    # 7) 'activa': a veces como texto ('SI', 'No', '1', '0')
    sucio["activa"] = sucio["activa"].astype(object)
    for texto, desplazamiento in (("SI", 10), ("No", 11), ("1", 12), ("0", 13)):
        idx = sucio.sample(frac=0.05, random_state=SEMILLA + desplazamiento).index
        sucio.loc[idx, "activa"] = texto

    # 8) 3% de los 'nit' repetidos entre empresas distintas
    idx_destino = sucio.sample(frac=0.03, random_state=SEMILLA + 15).index
    idx_origen = sucio.sample(frac=0.03, random_state=SEMILLA + 16).index
    sucio.loc[idx_destino, "nit"] = sucio.loc[idx_origen, "nit"].values

    # 9) 5% de las filas repetidas tal cual (duplicados exactos; va al final para que las copias queden idénticas)
    idx = sucio.sample(frac=0.05, random_state=SEMILLA + 14).index
    sucio = pd.concat([sucio, sucio.loc[idx]], ignore_index=True)

    return sucio


def generar_empresas(n: int = 300) -> pd.DataFrame:
    """Devuelve un DataFrame SUCIO con n empresas simuladas (más sus repetidas)."""
    filas = []
    for _ in range(n):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        })
    df = ensuciar(pd.DataFrame(filas))
    return df


if __name__ == "__main__":
    df = generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())