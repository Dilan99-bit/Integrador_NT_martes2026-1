from email.mime import text
from importlib.resources import files
import random
import uuid
from faker import Faker

#1 configurar  el fake a  la region que necesito
faker=Faker("es_CO")

#2 simurar semillas para tener coherencia en los datos
Faker.seed(42)
random.seed(42)

#3 indentifico los datos que debo simular
#id (texto (UUID)),
#titulo (texto),
#descripcion (texto), 
#url_archivo (texto),
#fecha_entrega (fecha y hora), 
#estado (texto), 
#calificacion (decimal (0 a 5)), 
#id_registro (texto (UUID)).

#4 indetifico los datos


#5 defini mi DATASET
FILAS=600

#6 CONTRUYO UNA FUNCION PARA GENERAR LOS pedidos (limpios)
def generar_datos_limpios(numero_datos=FILAS):
    for _ in range(numero_datos):
        files.append({
         "id": str(uuid.uuid4()),
         "titulo": faker.sentence(nb_words=5).rstrip("."), 
         "id_registro":random.choice(IDS_REGISTRO),
         "descripcion": faker.sentence(nb_words=12),
         "url_archivo" : faker.url() + faker.file_name(category="office"),
         "calificacion": random.choice(ESTADOS),
         "fecha_entrega": faker.date_time_between(start_date="-1y", end_date="now"),
         "estado": random.choice(ESTADOS),
        })
    return files
variable_noche=pd.DataFrame(generar_datos_limpios())

#Ensucial los datos

#1. Crear yna funcion para definir procentaje de error
def generar_muestra(datos,porcentaje):
    return datos.simple(fraccion=porcentaje,
    random_state=random.randint(0,999)).index

#2. Crear una funcion para escribir mal un text
def escribir_mal(text):
    vatiantes=[texto.Iower(),f"{texto.title()}", texto.capitalize()]
    return random.choice(variantes)

#3 comvertir boolenos en textos
def convertir_booleano_tect(valor):
    if valor:
       return randm.choice(["SI", "1"])
    return randm.choice(["NO", "0"]) 

def ensuciar(datos_df):
    datos_df=datos_df.copy()

    #nombre:10% con espacios sobrantes, 8% Mayuscula
    filas_elegidas=generar_muestra(datos_df,0.10)
     #  descripcion: 15% nulos
    filas = generar_muestra(datos_df, 0.15)
    datos_df.loc[filas, 'descripcion'] = None
    
    #  url_archivo: 8% sin http/https
    filas = generar_muestra(datos_df, 0.08)
    datos_df.loc[filas, 'url_archivo'] = datos_df.loc[filas, 'url_archivo'].str.replace(r'^https?://', '', regex=True)
    
    #  fecha_entrega: mezclar 2 formatos
    mitad = len(datos_df) // 2
    datos_df['fecha_entrega'] = pd.to_datetime(datos_df['fecha_entrega']).dt.strftime('%Y-%m-%d %H:%M:%S')
    filas = generar_muestra(datos_df, 0.5)
    datos_df.loc[filas, 'fecha_entrega'] = pd.to_datetime(datos_df.loc[filas, 'fecha_entrega']).dt.strftime('%d/%m/%Y %H:%M')
    
    #  estado: variantes
    filas = generar_muestra(datos_df, 1.0)
    datos_df.loc[filas, 'estado'] = np.random.choice(['enviada', 'EN REVISION', 'Aprobada'], size=len(filas))
    
    #  calificacion
    # 6% nulos
    filas = generar_muestra(datos_df, 0.06)
    datos_df.loc[filas, 'calificacion'] = None
    # 4% fuera de rango
    filas = generar_muestra(datos_df, 0.04)
    datos_df.loc[filas, 'calificacion'] = np.random.choice([-1, 8.0], size=len(filas))
    # Algunos con coma como texto
    filas = generar_muestra(datos_df, 0.05)
    datos_df.loc[filas, 'calificacion'] = datos_df.loc[filas, 'calificacion'].astype(str).str.replace('.', ',')
    
    # 6 Duplicados: 5%
    duplicados = datos_df.sample(frac=0.05, replace=True)
    datos_df = pd.concat([datos_df, duplicados], ignore_index=True)
    
    #  id_registro + url_archivo repetidos: 10%
    filas = generar_muestra(datos_df, 0.10)
    datos_def.loc[filas, 'url_archivo']=datos_df_loc[filas, 'url_archivo'].iloc[0]
    
    return datos_df
    #imprimir
    if _ _name_ _ == " _ _main_ _":
    df = generar_evidencias(n=600)
    print("Forma:", df.shape)
    print("\nPrimeras filas:")
    print(df.head())
    print("\nDatos vacíos por columna:")
    print(df.isna().sum())