"""Genera datos sucios de prueba para la tabla categorias."""

import random
import uuid
import unicodedata

import pandas as pd
from faker import Faker


CATEGORIAS = [
    "Logística",
    "Finanzas",
    "Recursos Humanos",
    "Tecnología",
    "Marketing",
    "Ventas",
    "Compras",
    "Producción",
    "Calidad",
    "Administración",
]

AREAS = [
    "Operaciones",
    "Dirección General",
    "Sistemas",
    "Gestión Humana",
    "Comercial",
    "Suministros",
]


def generar_categorias(n: int = 250) -> pd.DataFrame:
    """Devuelve n filas con nombres, nulos y duplicados intencionalmente sucios."""
    if n < 1:
        raise ValueError("n debe ser mayor que cero")

    Faker.seed(42)
    random.seed(42)
    fake = Faker("es_CO")

    cantidad_duplicados = int(n * 0.08)
    cantidad_base = n - cantidad_duplicados
    registros = []

    for _ in range(cantidad_base):
        categoria = random.choice(CATEGORIAS)
        sin_tildes = "".join(
            caracter
            for caracter in unicodedata.normalize("NFKD", categoria)
            if not unicodedata.combining(caracter)
        )
        nombre = random.choice(
            [
                categoria,
                categoria.upper(),
                categoria.lower(),
                f" {categoria.lower()} ",
                sin_tildes,
            ]
        )
        registros.append(
            {
                "id": str(uuid.uuid4()),
                "nombre": nombre,
                "descripcion": fake.sentence(nb_words=8),
                "area_responsable": random.choice(AREAS),
            }
        )

    indices_duplicados = random.sample(range(cantidad_base), cantidad_duplicados)
    registros.extend(registros[indice].copy() for indice in indices_duplicados)

    indices_duplicados_set = set(indices_duplicados)
    indices_disponibles = [
        indice
        for indice in range(cantidad_base)
        if indice not in indices_duplicados_set
    ]
    cantidad_nulos_descripcion = int(n * 0.15)
    cantidad_nulos_area = int(n * 0.10)
    indices_descripcion = random.sample(
        indices_disponibles, cantidad_nulos_descripcion
    )
    indices_area = random.sample(indices_disponibles, cantidad_nulos_area)
    for indice in indices_descripcion:
        registros[indice]["descripcion"] = None
    for indice in indices_area:
        registros[indice]["area_responsable"] = None

    return pd.DataFrame(registros)


if __name__ == "__main__":
    df = generar_categorias()
    print("df.shape:", df.shape)
    print("\ndf.head():")
    print(df.head())
    print("\ndf.isna().sum():")
    print(df.isna().sum())
