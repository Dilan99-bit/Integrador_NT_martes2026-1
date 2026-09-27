import random
import pandas as pd
import uuid

from faker import Faker

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
ESTADOS=["PENDIENTE", "EN_PROCESO", "COMPLETADO", "CANCELADO"]
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

print(señor_de_la_noche)
