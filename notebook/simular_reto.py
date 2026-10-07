# El elemento central: la necesidad que publica la empresa. Crea el script `src/simular_retos.py`. Con la libreria **Faker** genera 500 filas falsas de la tabla `retos`, con las MISMAS columnas que usa Backend II. Despues **ensucia los datos a proposito**: nulos, duplicados, espacios sobrantes, mayusculas mezcladas y formatos distintos. Esos errores son los que vas a arreglar en la etapa de limpieza, asi que tienen que quedar bien puestos.

# Usa `Faker("es_CO")` y fija la semilla con `Faker.seed(42)` y `random.seed(42)` para que el resultado sea SIEMPRE el mismo y tu compañero pueda reproducirlo.

import random
from datetime import timedelta
import pandas as pd
from faker import Faker

#2. Sembrar semillar para tener coherencia en los datos simulados

Faker.seed(42)
random.seed(42)

#1. configurar el faker a la region que necesito
fake=Faker("es_CO")

#3. Identifico los datos que debo simular
#id (texto (UUID))
#nombre (texto)
#descripcion (texto)
#fecha_inicio (fecha)
#fecha_fin (fecha)
#estado (texto)
#id_empresa (texto (UUID))
#id_categoria (texto (UUID))
#id_prioridad (texto (UUID))

#4. Identifico los datos o el dato que sea un selector
ESTADO =["ACTIVO","INACTIVO","RECHAZADO","ACEPTADO", "EN ESPERA"]

IDS_EMPRESA = [fake.uuid4() for _ in range(10)]
IDS_CATEGORIA = [fake.uuid4() for _ in range(5)]
IDS_PRIORIDAD = [fake.uuid4() for _ in range(3)]

#5. Defino mi DATASET
FILAS=500

#6. Construyo una funcion para generar los N datos pedidos (LIMPIOS)
def generar_datos_limpios(numero_datos=FILAS):
    filas=[]
    for _ in range (numero_datos):
        fecha_inicio=fake.date_between(start_date="-1y", end_date="+3m")
        filas.append({
            "id":fake.uuid4(),
            "nombre":fake.sentence(nb_words=6).rstrip("."),
            "descripcion":fake.sentence(nb_words=12),
            "fecha_inicio":fecha_inicio,
            "fecha_fin":fecha_inicio + timedelta(days=random.randint(15, 180)),
            "estado": random.choice(ESTADO),
            "id_empresa":random.choice(IDS_EMPRESA),
            "id_categoria":random.choice(IDS_CATEGORIA),
            "id_prioridad":random.choice(IDS_PRIORIDAD), 
        })
    return filas

variable_noche=pd.DataFrame(generar_datos_limpios())

#Ensuciar los datos

#1. Crear una funcion para definir porcentajes de error
def generar_muestra(datos,porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0,999)).index

#2. Crear una funcion para escribir mal un texto
def escribir_mal(texto):
    variantes=[texto.lower(),f" {texto.title()} ", texto.capitalize()]
    return random.choice(variantes)

#3. Convertir booleanos en textos
def converti_booleano_texto(valor):
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["NO","0"])

#4. Funcion para ensuciar los datos
def ensuciar(datos_df):
    datos_df=datos_df.copy()
    datos_df["fecha_inicio"]=pd.to_datetime(datos_df["fecha_inicio"])
    datos_df["fecha_fin"]=pd.to_datetime(datos_df["fecha_fin"])

    #nombre:10% con espacios sobrantes
    filas_elegidas=generar_muestra(datos_df,0.10)
    datos_df.loc[filas_elegidas, "nombre"]=" "+datos_df.loc[filas_elegidas,"nombre"]+" "

    #descripcion: 12% en None (nulos)
    filas_elegidas=generar_muestra(datos_df,0.12)
    datos_df.loc[filas_elegidas,"descripcion"]=None

    #fecha_fin: 8% en None y 5% anterior a fecha_inicio
    filas_nulas=generar_muestra(datos_df,0.08)
    datos_disponibles=datos_df.drop(index=filas_nulas)
    filas_anteriores=generar_muestra(datos_disponibles,0.05/0.92)
    datos_df.loc[filas_anteriores,"fecha_fin"]=[
        fecha_inicio-timedelta(days=random.randint(1,180))
        for fecha_inicio in datos_df.loc[filas_anteriores,"fecha_inicio"]
    ]

    #fecha_inicio: dos formatos mezclados: "2026-03-02" y "02/03/2026"
    iso=datos_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino=datos_df["fecha_inicio"].dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"]=iso
    filas_elegidas=generar_muestra(datos_df,0.4)
    datos_df.loc[filas_elegidas,"fecha_inicio"]=latino.loc[filas_elegidas]

    datos_df["fecha_fin"]=datos_df["fecha_fin"].dt.strftime("%Y-%m-%d")
    datos_df.loc[filas_nulas,"fecha_fin"]=None

    #estado: variantes con diferencias de formato
    filas_estado=datos_df.sample(n=3, random_state=random.randint(0,999)).index
    datos_df.loc[filas_estado,"estado"]=["en_curso","EN CURSO"," Cerrado "]

    return datos_df

variable_noche=ensuciar(variable_noche)

def agregar_duplicados(datos_df, porcentaje=0.05):
    cantidad_duplicados=int(len(datos_df)*porcentaje)
    filas_duplicadas=datos_df.sample(
        n=cantidad_duplicados,
        random_state=random.randint(0,999),
    )
    return pd.concat([datos_df,filas_duplicadas],ignore_index=True)


#5% de las filas originales repetidas tal cual (duplicados exactos).
variable_noche=agregar_duplicados(variable_noche)

if __name__ == "__main__":
    print(f"Filas generadas: {len(variable_noche)}")
    print(f"Duplicados exactos: {variable_noche.duplicated().sum()}")
    print("\nDatos generados:")
    with pd.option_context(
        "display.max_rows", None,
        "display.max_columns", None,
        "display.width", 120,
        "display.expand_frame_repr", True,
    ):
        print(variable_noche.to_string(index=False, line_width=120))