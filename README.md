# integrador_nt_martes20262

Proyecto integrador de nuevas tecnologías. Trabaja con la tabla **empresas**: simula datos sucios con Faker, los exporta a CSV, XLSX y JSON, y los limpia con pandas.

## Requisitos

- Python 3.10 o superior
- Las librerías de `requirements.txt`:

```
pandas>=2.0,<3.0
faker
openpyxl
matplotlib
```

## Instalación

Desde la raíz del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En macOS o Linux, el segundo comando es `source .venv/bin/activate`.

## Cómo ejecutar

Todo se corre desde `main.py`, en la raíz del proyecto:

```
python main.py                    # corre las tres etapas, en orden
python main.py simular            # solo simula y muestra los datos (no guarda archivos)
python main.py exportar           # simula y guarda data/crudo/empresas_sucio.*
python main.py limpiar            # limpia data/crudo y guarda data/limpio/
python main.py simular exportar   # varias etapas; siempre se ejecutan en orden
```

La etapa `limpiar` necesita que `data/crudo/empresas_sucio.csv` exista; si no, ejecuta antes `python main.py exportar`.

Cada script también se puede correr por separado, por ejemplo:

```
python src/notebook/simulacion/simular_empresas.py
python src/notebook/exportacion/exportar_empresas.py
python src/notebook/limpieza/limpiar_empresas.py
```

## Estructura del proyecto

```
integrador_nt_martes20262/
├── data/
│   ├── crudo/        empresas_sucio.csv, .json, .xlsx
│   ├── limpio/       empresas_limpio.csv, .json, .xlsx
│   └── reportes/     empresas_por_estado.png, empresas_por_sector.png
├── src/
│   └── notebook/
│       ├── simulacion/   simular_empresas.py
│       ├── exportacion/  exportar_empresas.py
│       ├── limpieza/     limpiar_empresas.py
│       ├── consultas/    consultas_empresas.py
│       └── reportes/     reporte_empresas.py
├── main.py
├── requirements.txt
└── README.md
```

## Etapas

| Etapa | Historia de usuario | Script | Resultado |
|---|---|---|---|
| Simulación | F01 | `src/notebook/simulacion/simular_empresas.py` | DataFrame sucio con 300 empresas + 5 % de filas repetidas (315 filas) |
| Exportación | X01 | `src/notebook/exportacion/exportar_empresas.py` | `data/crudo/empresas_sucio.csv`, `.xlsx` y `.json` |
| Limpieza | L01 | `src/notebook/limpieza/limpiar_empresas.py` | `data/limpio/empresas_limpio.csv`, `.xlsx` y `.json` (300 filas) |

`exportar_empresas.py` importa la función `generar_empresas()` de `simular_empresas.py`; no copia su código. Los scripts de `consultas` y `reportes` todavía no están integrados en `main.py`.

## Datos

**Columnas:** `id`, `nombre`, `nit`, `sector`, `contacto`, `correo`, `telefono`, `activa`. La limpieza agrega `correo_valido`.

**Defectos que introduce la simulación:**

- `nombre`: 10 % con espacios sobrantes y 15 % en mayúsculas.
- `nit`: la mitad con puntos y guion (`900.123.456-7`) y la otra mitad sin formato; 3 % repetidos entre empresas distintas.
- `sector`: variantes del mismo sector (`Salud`, `SALUD`, `  salud  `).
- `contacto`: 8 % nulos.
- `correo`: 6 % sin la arroba.
- `telefono`: tres formatos mezclados (`3001234567`, `300 123 4567`, `+57 300-123-4567`).
- `activa`: a veces como texto (`SI`, `No`, `1`, `0`).
- 5 % de las filas repetidas tal cual.

**Correcciones de la limpieza:**

- Elimina los duplicados exactos (315 → 300 filas).
- Quita espacios sobrantes en `nombre` y unifica `sector` con formato título.
- Deja `nit` sin puntos ni guiones y `telefono` solo con dígitos (queda como texto, para no perder ceros a la izquierda).
- Convierte `activa` a booleano.
- Rellena los `contacto` vacíos con `Sin contacto`.
- Crea `correo_valido` (`True` si el correo tiene `@`).
- Verifica que no quede ningún nulo ni duplicado exacto antes de guardar.

## Reproducibilidad y versionado

- La semilla está fija (`Faker.seed(42)` y `random.seed(42)`), así que cada corrida genera los mismos datos, con una excepción: el `id` es un UUID nuevo en cada ejecución (`uuid.uuid4()`).
- Los tres archivos de `data/crudo/` se versionan en Git. Si se pierden o se quieren regenerar: `python main.py exportar`.
