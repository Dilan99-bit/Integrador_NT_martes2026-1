import random
import uuid
from faker import Faker
import pandas as pd
import faker

#1. configurar el faker a la region que necesito
fake=Faker("es_CO")

#2. Sembrare semillas para tener coherencia en los datos
#simulados
Faker.seed(42)
random.seed(42)

#3. Identifico los datos que debo simular
 #id (texto (UUID)),
 #nombre (texto), 
 # nivel (entero), 
 #dias_max_respuesta (entero).

 #4. iDENTIFICO los datos o dato que sea un selector
NIVELES=["ALTA", "MEDIA", "BAJA"]
DIAS=[5, 10, 15]

 #5. Defino mi DATASET
FILAS=200

 #6. Construyo una funcion para generar los N datos pedidos
def generar_datos_limpios(nivel, numero_datos=FILAS):
    filas=[]
    for _ in range(numero_datos):
      nombre=random.choice(list(NIVELES.keys()))


      filas.append({
        "id":str(uuid.uuid4()),
        "nombre":random.choice(list(NIVELES.keys())),
        "nivel":NIVELES[nombre.keys()],
        "dias_max_respuesta":DIAS[nivel]
        
      })

      #Ensuciar los datos

      #1. Crear una funcion para definir porcentajes de error

      def generar_muestra(datos,porcentaje):
         return datos.sample(fraccion=porcentaje, random_state=random.randint(0,999)).index

      #2. Crear una funcion para escribir mal un dato
      def escribir_mal(texto):
         variantes=[texto.lower(),f" {texto.title()} ", texto.capitalize()]
         return random.choice(variantes)

      #3. Convertir booleanos en texto
      def convertir_booleano_texto(valor):
         if valor:
            return random.choice(["si", "1"])
         return random.choice(["no", "0"])

      #4. Funcion para ensuciar los datos
      def ensuciar(datos_df):
         datos_df=datos_df.copy()

         #nombre: 10% con espacios sobrantes, 8% Mayusculas
         filas_elegidas=generar_muestra(datos_df, 0.1)
         datos_df.loc[filas_elegidas, "nombre"]=" "+datos_df.loc[filas_elegidas, "nombre"] 

         #ensuciar variantes (Alta, ALTA, alta)
         filas_elegidas=generar_muestra(datos_df, 0.08)
         datos_df.loc[filas_elegidas, "nombre"]=escribir_mal(datos_df.loc[filas_elegidas, "nombre"])

         #ensuciar nivel: como texto, a veces la palabra 
         filas_elegidas=generar_muestra(datos_df, 0.05)
         datos_df.loc[filas_elegidas, "nivel"].str.replace({"1":"ALTA", "2":"MEDIA", "3":"BAJA"})

         #7% None
         filas_elegidas=generar_muestra(datos_df, 0.07)
         datos_df.loc[filas_elegidas, "nivel"]=None

         #dias_max_respuesta: 5% None, 3% como valor absurdo (999)
         filas_elegidas=generar_muestra(datos_df, 0.05)
         datos_df.loc[filas_elegidas, "dias_max_respuesta"]=None 

         filas_elegidas=generar_muestra(datos_df, 0.03)
         datos_df.loc[filas_elegidas, "dias_max_respuesta"]=999

         #8% filas repetidas
         filas_elegidas=generar_muestra(datos_df, 0.08)
         datos_df=datos_df.append(datos_df.loc[filas_elegidas], ignore_index=True)
      
