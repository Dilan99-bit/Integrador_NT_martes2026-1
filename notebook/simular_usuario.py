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
#nombre (texto) 
#correo (texto) 
#contrasena_hash (texto) 
#rol (texto) 
#activo (booleano),
#fecha_registro (fecha y hora)

#4. Identifico los datos o el dato que sea un selector
ROLES=["ADMIN","EMPRESA","PARTICIPANTE"]

#5. Defino mi DATASET
FILAS=800

#6. Construyo una funcion para generar los N datos pedidos (LIMPIOS)
def generar_datos_limpios(numero_datos=FILAS):
    filas=[]
    for _ in range(numero_datos):
        
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.name(),
            "correo": fake.email(),
            "contrasena_hash": fake.sha256(),
            "rol": random.choice(ROLES),
            "activo": random.choice([True, False]),
            "fecha_registro": fake.date_time_between(start_date='-2y', end_date='now')

        })
    return filas 

señor_de_la_noche=pd.DataFrame(generar_datos_limpios())

print(señor_de_la_noche)