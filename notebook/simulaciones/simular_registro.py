import random
import pandas as pd
import uuid

from faker import Faker

import pandas as pd

# Configuración de pandas para mostrar todas las columnas y ajustar el ancho de visualización
""" pd.set_option('display.max_columns', None)  # Muestra todas las columnas
pd.set_option('display.width', 1000)        # Ajusta el ancho para que no se corte """

#1. configurar el faker a la region que necesito
fake=Faker("es_CO")

#2. Sembrar semillas para tener coherencia en los datos
#simulados
Faker.seed(42)
random.seed(42)

#3. Identifico los datos que debo simular
#id (texto (UUID))
#fecha_registro (fecha y hora)
#observacion (texto)
#estado (texto)
#id_usuario (texto (UUID))
#id_reto (texto (UUID))


#4. Identifico los datos o el dato que sea un selector
ESTADOS=["inscrito","EN PROCESO","Finalizado"]
IDS_USUARIO=[str(uuid.uuid4()) for _ in range(10)]
IDS_RETO=[str(uuid.uuid4()) for _ in range(10)]

#5. Defino mi DATASET
FILAS=800

#6. Construyo una funcion para generar los N datos pedidos (LIMPIOS)
def generar_datos_limpios(numero_datos=FILAS):
    filas=[]
    for _ in range(numero_datos):
        
        filas.append({

            "id": str(uuid.uuid4()),
            "fecha_registro": fake.date_time_between(start_date='-1y', end_date='now'),
            "observacion": fake.sentence(nb_words=10),
            "estado":random.choice(ESTADOS),
            "id_usuario":random.choice(IDS_USUARIO),
            "id_reto":random.choice(IDS_RETO)

        })
    return filas   


señor_de_la_noche=pd.DataFrame(generar_datos_limpios())

#Ensusiar los datos

# 1) crear una funcion para sefinir porsentajes de error

def generar_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje,
                        random_state=random.randint(0,999)).index

# 2) crear una funcion para crear mal un texto

def escribir_mal(texto):
    variantes=[texto.lower(),f"{texto.title()} ",texto.capitalize()]
    return random.choice(variantes)

# 3)  crear una funcion para combertir booleanos en textos

def convertir_booleano_texto(valor):
    if valor:
        return random.choice(["si","1"])
    return random.choice(["No", "0"])

# 4) funcion para ensuciar los datos 

def ensuciar(datos_df):
    datos_df=datos_df.copy()
    filas_elegidas=generar_muestra(datos_df, 0.10)

    """ Se ensucia `fecha_registro`: dos formatos mezclados: "2026-03-15 14:30:00" y "15/03/2026 14:30" """
   #fechas dos formatos mesclados (2026-03-15 14:30:00) y (15/03/2026 14:30)

    iso=datos_df["fecha_registro"].dt.strftime("%Y-%m-%d %H:%M:%S")

    latino=datos_df["fecha_registro"].dt.strftime("%d/%m/%Y %H:%M")

    datos_df["fecha_registro"]=iso

    filas_elegidas=generar_muestra(datos_df,0.4)
    datos_df.loc[filas_elegidas,"fecha_registro"]=latino.loc[filas_elegidas] 

    """ Se ensucia `observacion`: 20% en None (nulos). """
    filas_elegidas=generar_muestra(datos_df , 0.2)
    datos_df.loc[filas_elegidas,"observacion"]=None

    """ Se ensucia `estado`: variantes: 'inscrito', 'EN PROCESO', ' Finalizado '. """
    filas_elegidas=generar_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "estado"] = (
        datos_df.loc[filas_elegidas, "estado"].map(escribir_mal)
    )

    """ Repite el par usuario-reto en el 10% de las filas seleccionadas. """
    filas_elegidas = generar_muestra(datos_df, 0.10)
    indices_origen = datos_df.index.difference(filas_elegidas)
    for indice in filas_elegidas:
        indice_origen = random.choice(indices_origen)
        datos_df.loc[indice, ["id_usuario", "id_reto"]] = datos_df.loc[
            indice_origen, ["id_usuario", "id_reto"]
        ]

    """ Agrega copias exactas del 5% de las filas originales. """
    filas_elegidas = generar_muestra(datos_df, 0.05)
    duplicados = datos_df.loc[filas_elegidas].copy()
    datos_df = pd.concat([datos_df, duplicados], ignore_index=True)

    return datos_df


registros_sucios = ensuciar(señor_de_la_noche)

print("Datos originales:")
print(señor_de_la_noche.head())
print("\nDatos sucios:")
print(registros_sucios.head())
