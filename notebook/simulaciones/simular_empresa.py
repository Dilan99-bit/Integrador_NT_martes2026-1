"""Etapa 1 - Simulación de la tabla Empresa con Faker.

Genera datos realistas y los ENSUCIA a propósito, para que la etapa 3
(limpieza con pandas) tenga trabajo de verdad.
"""

import random
import uuid
from pathlib import Path

import pandas as pd
import numpy as np
from faker import Faker

# --- Reproducibilidad: SIEMPRE arriba y antes de crear el objeto fake ---
SEMILLA = 42
Faker.seed(SEMILLA)
random.seed(SEMILLA)

fake = Faker("es_CO")

FILAS = 300
SECTORES = ["Manufactura", "Servicios", "Comercio", "Tecnología",
            "Agroindustria", "Construcción", "Salud", "Educación"]

def generar_empresas(n: int = FILAS) -> pd.DataFrame: 
    """Devuelve un DataFrame de n empresas simuladas."""
    filas = []
    for i in range(1, n + 1):
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.unique.numerify("9########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.unique.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        })
    return pd.DataFrame(filas)


def ensuciar(df: pd.DataFrame) -> pd.DataFrame:
    """Introduce defectos controlados. Devuelve una copia sucia."""
    sucio = df.copy()
    n = len(sucio)

    # 1) 10% Espacios sobrantes al inicio y final, 15% en MAYUSCULAS en 'nombre'
    idx = sucio.sample(frac=0.10, random_state=SEMILLA + 2).index
    sucio.loc[idx, "nombre"] = "  " + sucio.loc[idx, "nombre"].astype(str) + " "
           idx = sucio.sample(frac=0.15, random_state=SEMILLA + 3).index
    sucio.loc[idx, "nombre"] = sucio.loc[idx, "nombre"].astype(str).str.upper()

    # 2) Ensuciar 'nit': mitad con formato (900.123.456-7) y mitad sin formato (9001234567)
    nit_limpio = sucio["nit"].astype(str).str.replace(r'\D', '', regex=True)
    idx_1 = sucio.sample(frac=0.5, random_state=SEMILLA + 4).index
    sucio.loc[idx_1, "nit"] = (
        nit_limpio.loc[idx_1].str[:3] + "." + 
        nit_limpio.loc[idx_1].str[3:6] + "." + 
        nit_limpio.loc[idx_1].str[6:9] + "-" + 
        nit_limpio.loc[idx_1].str[9:]
    )
    idx_2 = sucio.index.difference(idx_1)
    sucio.loc[idx_2, "nit"] = nit_limpio.loc[idx_2]

    # 3) Ensuciar 'sector': variantes con espacios sobrantes y en MAYUSCULAS
    idx = sucio.sample(frac=0.10, random_state=SEMILLA + 5).index
    sucio.loc[idx, "sector"] = "  " + sucio.loc[idx, "sector"].astype(str).str.lower() + "  "
    idx = sucio.sample(frac=0.15, random_state=SEMILLA + 6).index
    sucio.loc[idx, "sector"] = sucio.loc[idx, "sector"].astype(str).str.upper()

    # 4) Nulos: 8% de contacto
    idx = sucio.sample(frac=0.08, random_state=SEMILLA).index
    sucio.loc[idx, "contacto"] = np.nan

    # 5) Ensuciar 'correo': 6% sin la arroba (correo inválido)
    idx = sucio.sample(frac=0.06, random_state=SEMILLA + 7).index
    sucio.loc[idx, "correo"] = sucio.loc[idx, "correo"].astype(str).str.replace("@", "")

    # 6) Ensuciar 'telefono': tres formatos mezclados
    tel_limpio = sucio["telefono"].astype(str).str.replace(r'\D', '', regex=True).str[-10:]
    sucio["telefono"] = tel_limpio
    idx = sucio.sample(frac=0.33, random_state=SEMILLA + 8).index
    sucio.loc[idx, "telefono"] = (
        tel_limpio.loc[idx].str[:3] + " " + 
        tel_limpio.loc[idx].str[3:6] + " " + 
        tel_limpio.loc[idx].str[6:]
    )
    idx = sucio.sample(frac=0.33, random_state=SEMILLA + 9).index
    sucio.loc[idx, "telefono"] = (
        "+57 " + 
        tel_limpio.loc[idx].str[:3] + "-" + 
        tel_limpio.loc[idx].str[3:6] + "-" + 
        tel_limpio.loc[idx].str[6:]
    )

    # 7) Ensuciar 'activa': a veces como texto ('SI', 'No', '1', '0')
    sucio["activa"] = sucio["activa"].astype(object)
    idx = sucio.sample(frac=0.05, random_state=SEMILLA + 10).index
    sucio.loc[idx, "activa"] = "SI"
    idx = sucio.sample(frac=0.05, random_state=SEMILLA + 11).index
    sucio.loc[idx, "activa"] = "No"
    idx = sucio.sample(frac=0.05, random_state=SEMILLA + 12).index
    sucio.loc[idx, "activa"] = "1"
    idx = sucio.sample(frac=0.05, random_state=SEMILLA + 13).index
    sucio.loc[idx, "activa"] = "0"

    # 8) 5% de las filas repetidas tal cual (duplicados exactos)
    idx = sucio.sample(frac=0.05, random_state=SEMILLA + 14).index
    sucio = pd.concat([sucio, sucio.loc[idx]], ignore_index=True)

    # 9) 3% de los `nit` repetidos entre empresas distintas
    idx_destino = sucio.sample(frac=0.03, random_state=SEMILLA + 15).index
    idx_origen = sucio.sample(frac=0.03, random_state=SEMILLA + 16).index
    sucio.loc[idx_destino, "nit"] = sucio.loc[idx_origen, "nit"].values

    return sucio


if __name__ == "__main__":
    df_limpio = generar_empresas()
    df_sucio = ensuciar(df_limpio)

    print("Filas y columnas:", df_sucio.shape)
    print(df_sucio.head())

    salida = Path("data/crudo")
    salida.mkdir(parents=True, exist_ok=True)
    
    df_sucio.to_csv(salida / "empresa.csv", index=False, encoding="utf-8-sig")
    print("Archivo escrito en data/crudo/empresa.csv")
