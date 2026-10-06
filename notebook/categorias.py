# Paso 1: Importar las herramientas para generar datos aleatorios y ficticios.
import random
import uuid
import pandas as pd

from faker import Faker

# Paso 2: Configurar los generadores de datos en español de Colombia.
fake=Faker("es_CO")
Faker.seed(42)
random.seed(42)

# Paso 3: Definir las categorías y las áreas que se asignarán a cada registro.
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
    "Administración"
]

AREAS = [
    "Operaciones",
    "Dirección General",
     "Sistemas", 
    "Gestión Humana",
    "Comercial",
     "Suministros"
]

# Paso 4: Indicar cuántos registros base se crearán.
FILAS = 250

# Paso 5: Crear la función que genera los registros y agrega variaciones.
def generar_categorias():
    # Paso 5.1: Preparar la lista donde se almacenarán los registros.
    filas=[]

    # Paso 5.2: Crear los registros base con identificador y datos aleatorios.
    for i in range(FILAS):

        nombre_categoria = random.choice(CATEGORIAS)
        variante_nombre=[
            nombre_categoria,
            nombre_categoria.upper(),
            nombre_categoria.lower()

        ]

        # Cada registro incluye nombre, descripción y área responsable.
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": random.choice(variante_nombre),
            "descripcion": fake.sentence(nb_words=8),
            "area_responsable": random.choice(AREAS)
        })

    # Paso 5.3: Dejar algunas descripciones vacías para simular datos faltantes.
    for _ in range(int(FILAS * 0.15)):
        pos = random.randint(0, FILAS - 1)
        filas[pos]["descripcion"] = None
    
    # Paso 5.4: Dejar algunas áreas responsables sin asignar.
    for _ in range(int(FILAS * 0.10)):
        pos = random.randint(0, FILAS - 1)
        filas[pos]["area_responsable"] = None

    # Paso 5.5: Agregar copias de algunos registros para simular duplicados.
    for _ in range(int(FILAS * 0.08)):
        pos = random.randint(0, FILAS - 1)
        filas.append(filas[pos].copy())

    # Paso 5.6: Devolver la lista completa con los datos generados.
    return filas

# Paso 6: Ejecutar la función y guardar los registros generados.
datos= generar_categorias()

# Paso 7: Organizar los registros en una tabla de pandas.
tabla = pd.DataFrame(datos)

# Paso 8: Mostrar el total de registros y la tabla completa sin índice.
print("Todos los datos son", len(datos))
print(tabla.to_string(index=False))