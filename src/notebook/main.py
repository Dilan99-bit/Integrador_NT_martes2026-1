"""
main.py - valida la simulación (HU F01), la exportación (HU X01), la limpieza (HU L01),
las consultas (HU Q01) y las gráficas (HU G01) de registros.

Estructura esperada del proyecto:
    proyecto/
    ├── data/
    │   ├── crudo/                  (se crea sola)
    │   ├── limpio/                 (se crea sola)
    │   │   └── consulta/
    │   │       ├── consulta_1/      (se crea sola)
    │   │       ├── consulta_2/
    │   │       ├── consulta_3/
    │   │       ├── consulta_4/
    │   │       └── consulta_5/
    │   └── reportes/               (se crea sola, con las 3 gráficas PNG)
    └── src/
        └── notebook/
            ├── main.py
            ├── simulacion/simular_registro.py
            ├── exportacion/exportar_registro.py
            ├── limpieza/limpieza_registros.py
            ├── consultas/consultas_registros.py
            └── reportes/reportes_registros.py

Uso (desde la raíz del proyecto):
    python src/notebook/main.py
"""
import sys
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROYECTO / "src"))

import pandas as pd

from notebook.simulacion.simular_registro import generar_registros
from notebook.exportacion.exportar_registro import (
    CARPETA_CRUDO,
    NOMBRE_ENTIDAD,
    exportar_csv,
    exportar_excel,
    exportar_json,
)
from notebook.limpieza.limpieza_registros import limpiar
from notebook.consultas.consultas_registros import ejecutar_consultas
from notebook.reportes.reportes_registros import generar_reportes, imprimir_conclusiones

COLUMNAS = ["id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto"]
ESTADOS_VALIDOS = ["en proceso", "finalizado", "inscrito"]
CARPETA_DATOS = RAIZ_PROYECTO / "data"
CARPETA_LIMPIO = CARPETA_DATOS / "limpio"
CARPETA_CONSULTAS = CARPETA_LIMPIO / "consulta"
CARPETA_REPORTES = CARPETA_DATOS / "reportes"
resultados = []


def revisar(nombre, condicion, detalle=""):
    estado = "PASA " if condicion else "FALLA"
    resultados.append(condicion)
    print(f"[{estado}] {nombre} {detalle}")


# ---------------------------------------------------------------- SIMULACIÓN
print("=" * 60)
print("HU F01 - SIMULACIÓN")
print("=" * 60)

df = generar_registros()

print("\nshape:", df.shape)
print("\nhead:")
print(df.head())
print("\nnulos por columna:")
print(df.isna().sum())
print()

revisar("generar_registros() devuelve un DataFrame", isinstance(df, pd.DataFrame))
revisar("Tiene las 6 columnas pedidas", list(df.columns) == COLUMNAS, f"-> {list(df.columns)}")
revisar("Tiene 840 filas (800 + 5% duplicadas)", len(df) == 840, f"-> {len(df)}")

n_nulos = int(df["observacion"].isna().sum())
revisar("observacion tiene ~20% de nulos", 150 <= n_nulos <= 180, f"-> {n_nulos}")

con_barra = int(df["fecha_registro"].astype(str).str.contains("/").sum())
con_guion = int(df["fecha_registro"].astype(str).str.contains("-").sum())
revisar("fecha_registro mezcla dos formatos", con_barra > 0 and con_guion > 0,
        f"-> {con_guion} ISO, {con_barra} dd/mm/aaaa")

variantes = sorted(df["estado"].dropna().unique().tolist())
sucios = [e for e in variantes if e != e.strip().lower()]
revisar("estado trae variantes mal escritas", len(sucios) > 0, f"-> {variantes}")

duplicados = int(df.duplicated().sum())
revisar("Hay duplicados exactos (~5%)", duplicados >= 40, f"-> {duplicados}")

pares_repetidos = int(df.duplicated(subset=["id_usuario", "id_reto"]).sum())
revisar("Hay pares id_usuario + id_reto repetidos", pares_repetidos > 0, f"-> {pares_repetidos}")

# ---------------------------------------------------------------- EXPORTACIÓN
print()
print("=" * 60)
print("HU X01 - EXPORTACIÓN")
print("=" * 60)

nombre = f"{NOMBRE_ENTIDAD}_sucio"
rutas = [
    exportar_csv(df, CARPETA_CRUDO, nombre),
    exportar_excel(df, CARPETA_CRUDO, nombre),
    exportar_json(df, CARPETA_CRUDO, nombre),
]

print()
for ruta in rutas:
    print(f"{ruta} -> {df.shape}")
print()

for ruta in rutas:
    revisar(f"Existe {ruta.name}", ruta.exists() and ruta.stat().st_size > 0)

revisar("Están en data/crudo", all(r.parent.name == "crudo" and r.parent.parent.name == "data" for r in rutas))

# Se leen de vuelta para comprobar que el contenido quedó bien
csv_df = pd.read_csv(rutas[0], encoding="utf-8")
json_df = pd.read_json(rutas[2], orient="records")

revisar("CSV se lee con las mismas filas y columnas", csv_df.shape == df.shape, f"-> {csv_df.shape}")
with pd.ExcelFile(rutas[1]) as xlsx:
    revisar(
        "Excel tiene la hoja 'registros'",
        "registros" in xlsx.sheet_names,
        f"-> {xlsx.sheet_names}",
    )
revisar("JSON se lee con las mismas filas y columnas", json_df.shape == df.shape, f"-> {json_df.shape}")

# ------------------------------------------------------------------ LIMPIEZA
print()
print("=" * 60)
print("HU L01 - LIMPIEZA")
print("=" * 60)

# Se limpia el CSV crudo que acaba de exportarse, como haría el flujo real.
sucio = pd.read_csv(rutas[0], encoding="utf-8")
limpio = limpiar(sucio)

print("\nshape antes:", sucio.shape, "| después:", limpio.shape)
print("\nhead:")
print(limpio.head())
print("\nnulos por columna:")
print(limpio.isna().sum())
print()

revisar("limpiar() devuelve un DataFrame", isinstance(limpio, pd.DataFrame))
revisar("Conserva las 6 columnas", list(limpio.columns) == COLUMNAS, f"-> {list(limpio.columns)}")
revisar("No quedan filas duplicadas", int(limpio.duplicated().sum()) == 0)
revisar("id es único", limpio["id"].is_unique, f"-> {limpio['id'].nunique()} de {len(limpio)}")
revisar("Se eliminaron las 40 duplicadas (840 -> 800)", len(limpio) == 800, f"-> {len(limpio)}")
revisar("No quedan nulos en ninguna columna", int(limpio.isna().sum().sum()) == 0)

estados_limpios = sorted(limpio["estado"].unique().tolist())
revisar("estado quedó con 3 valores en minúscula y sin espacios",
        estados_limpios == ESTADOS_VALIDOS, f"-> {estados_limpios}")

fechas = limpio["fecha_registro"].astype(str)
revisar("fecha_registro tiene un solo formato AAAA-MM-DD HH:MM:SS",
        bool(fechas.str.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$").all()))
revisar("No hay fechas futuras", bool((pd.to_datetime(fechas) <= pd.Timestamp.today()).all()))

CARPETA_LIMPIO.mkdir(parents=True, exist_ok=True)
ruta_limpio = CARPETA_LIMPIO / f"{NOMBRE_ENTIDAD}_limpio.csv"
limpio.to_csv(ruta_limpio, index=False, encoding="utf-8")
print(f"\n{ruta_limpio} -> {limpio.shape}")
revisar(f"Existe {ruta_limpio.name}", ruta_limpio.exists() and ruta_limpio.stat().st_size > 0)

# ----------------------------------------------------------------- CONSULTAS
print()
print("=" * 60)
print("HU Q01 - CONSULTAS")
print("=" * 60)

# Las consultas leen el archivo LIMPIO que acaba de guardarse, no el sucio.
limpio_csv = pd.read_csv(ruta_limpio, encoding="utf-8")
(finalizados, repetidos, conteo, top_retos, por_mes), rutas_consultas = ejecutar_consultas(
    limpio_csv, CARPETA_CONSULTAS
)
print()

revisar("Son 5 consultas con su CSV cada una", len(rutas_consultas) == 5)
for n, ruta in enumerate(rutas_consultas, start=1):
    revisar(f"Existe {ruta.name}", ruta.exists() and ruta.stat().st_size > 0)
revisar(
    "Están en data/limpio/consulta/consulta_N",
    all(
        ruta.parent.name == f"consulta_{n}" and ruta.parent.parent == CARPETA_CONSULTAS
        for n, ruta in enumerate(rutas_consultas, start=1)
    ),
)

n_finalizados = int((limpio_csv["estado"] == "finalizado").sum())
revisar("Consulta 1: solo trae estado finalizado y no queda vacía",
        len(finalizados) == n_finalizados and n_finalizados > 0 and (finalizados["estado"] == "finalizado").all(),
        f"-> {len(finalizados)}")
revisar("Consulta 2: todas las filas repiten usuario + reto",
        bool(repetidos.duplicated(subset=["id_usuario", "id_reto"], keep=False).all()) if len(repetidos) else True,
        f"-> {len(repetidos)}")
revisar("Consulta 3: los conteos por estado suman todas las filas",
        int(conteo["cantidad"].sum()) == len(limpio_csv), f"-> {int(conteo['cantidad'].sum())}")
revisar("Consulta 4: máximo 10 retos, ordenados de mayor a menor",
        len(top_retos) <= 10 and top_retos["participaciones"].is_monotonic_decreasing, f"-> {len(top_retos)} retos")
revisar("Consulta 5: las participaciones por mes suman todas las filas",
        int(por_mes["participaciones"].sum()) == len(limpio_csv), f"-> {len(por_mes)} meses")

# ------------------------------------------------------------------ GRÁFICAS
print()
print("=" * 60)
print("HU G01 - GRÁFICAS")
print("=" * 60)

# Las gráficas también leen el archivo LIMPIO guardado en la limpieza.
rutas_graficas, conclusiones = generar_reportes(limpio_csv, CARPETA_REPORTES)
print()
for ruta in rutas_graficas:
    print(ruta)
imprimir_conclusiones(conclusiones)
print()

revisar("Son 3 gráficas PNG", len(rutas_graficas) == 3)
for ruta in rutas_graficas:
    revisar(f"Existe {ruta.name}", ruta.exists() and ruta.stat().st_size > 0)
revisar("Están en data/reportes/", all(r.parent == CARPETA_REPORTES for r in rutas_graficas))
revisar("Los nombres son registros_grafica_1, _2 y _3",
        [r.name for r in rutas_graficas] ==
        ["registros_grafica_1.png", "registros_grafica_2.png", "registros_grafica_3.png"])
revisar("Las conclusiones responden las 3 preguntas (reto, mes, duplicadas con 409)",
        len(conclusiones) >= 3 and "409" in conclusiones[2])

# ------------------------------------------------------------------- RESUMEN
print()
print("=" * 60)
print(f"RESULTADO: {sum(resultados)} de {len(resultados)} pruebas pasan")
print("=" * 60)
sys.exit(0 if all(resultados) else 1)