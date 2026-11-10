# main.py - Valida las HU F01 (simulacion), X01 (exportacion), L01 (limpieza), Q01 (consultas)
# y G01 (graficas) de la tabla `retos`.
# Ejecutar SIEMPRE desde la raiz del proyecto:  python main.py

import contextlib
import inspect
import io
import json
import re
from pathlib import Path

import pandas as pd

from src.notebook.simulacion.simular_retos import generar_retos
from src.notebook.exportacion.exportar_retos import exportar_retos_crudos, CARPETA_CRUDO
from src.notebook.limpieza import limpiar_retos as limpieza
from src.notebook.consulta import consultas_retos as consultas
from src.notebook.graficas import reporte_retos as reporte

COLUMNAS = ["id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
            "estado", "id_empresa", "id_categoria", "id_prioridad"]

resultados = []


def verificar(nombre, condicion, detalle=""):
    resultados.append(bool(condicion))
    print(f"[{'PASA' if condicion else 'FALLA'}] {nombre} {detalle}")


# ---------- HU F01: simulacion ----------
print("=== HU F01: simulacion ===")
df = generar_retos()
print(df.shape)
print(df.head())
print(df.isna().sum())
print()

verificar("500 filas", len(df) == 500, f"({len(df)})")
verificar("9 columnas en orden", list(df.columns) == COLUMNAS)
verificar("duplicados exactos ~5%", 20 <= df.duplicated().sum() <= 30, f"({df.duplicated().sum()})")
verificar("descripcion ~12% nulos", 9 <= df["descripcion"].isna().mean() * 100 <= 15)
verificar("fecha_fin ~8% nulos", 5 <= df["fecha_fin"].isna().mean() * 100 <= 11)
verificar("nombre con espacios ~10%", 7 <= (df["nombre"] != df["nombre"].str.strip()).mean() * 100 <= 13)
verificar("fecha_inicio con 2 formatos", df["fecha_inicio"].str.contains("/").any() and df["fecha_inicio"].str.contains("-").any())
inicio = pd.to_datetime(df["fecha_inicio"], format="mixed", dayfirst=False, errors="coerce")
verificar("hay fecha_fin anterior a fecha_inicio", (pd.to_datetime(df["fecha_fin"]) < inicio).any())
verificar("estado con variantes sucias", df["estado"].isin(["en_curso", "EN CURSO", " Cerrado "]).sum() == 3)
verificar("es reproducible (misma semilla)", generar_retos().equals(df))

# ---------- HU X01: exportacion ----------
print("\n=== HU X01: exportacion ===")
for ruta in exportar_retos_crudos(df):
    print(f"{ruta} -> {df.shape}")
print()

csv = CARPETA_CRUDO / "retos_sucio.csv"
xlsx = CARPETA_CRUDO / "retos_sucio.xlsx"
js = CARPETA_CRUDO / "retos_sucio.json"
verificar("existen los 3 archivos en data/crudo", csv.exists() and xlsx.exists() and js.exists())
verificar("CSV: 500 filas y 9 columnas", pd.read_csv(csv, encoding="utf-8").shape == (500, 9))
verificar("XLSX: hoja 'retos' con 500 filas", pd.read_excel(xlsx, sheet_name="retos").shape == (500, 9))
datos_json = json.loads(js.read_text(encoding="utf-8"))
verificar("JSON: lista de 500 objetos", isinstance(datos_json, list) and len(datos_json) == 500)

# ---------- HU L01: limpieza ----------
# Corre el script de limpieza: lee data/crudo/retos_sucio.csv y guarda en data/limpio/
print("\n=== HU L01: limpieza ===")
limpieza.main()
print()

crudo = pd.read_csv(csv)
limpio_csv = limpieza.RUTA_SALIDA
limpio = pd.read_csv(limpio_csv, encoding="utf-8")
verificar("existen los 3 archivos en data/limpio",
          all((limpieza.CARPETA_LIMPIO / f"retos_limpio.{e}").exists() for e in ("csv", "xlsx", "json")))
verificar("sin duplicados exactos", limpio.duplicated().sum() == 0)
verificar("solo se eliminaron los duplicados",
          len(limpio) == len(crudo) - crudo.duplicated().sum(),
          f"({len(crudo)} -> {len(limpio)})")
verificar("sin nulos en columnas obligatorias", limpio[limpieza.COLUMNAS_OBLIGATORIAS].isna().sum().sum() == 0)
verificar("descripcion sin nulos", limpio["descripcion"].isna().sum() == 0)
verificar("descripciones vacias rellenas",
          (limpio["descripcion"] == "Sin descripcion").sum() >= crudo.drop_duplicates()["descripcion"].isna().sum())
verificar("fechas con un solo formato (AAAA-MM-DD)",
          limpio["fecha_inicio"].str.match(r"^\d{4}-\d{2}-\d{2}$").all()
          and limpio["fecha_fin"].dropna().str.match(r"^\d{4}-\d{2}-\d{2}$").all())
verificar("estado unificado (MAYUSCULAS, sin espacios)",
          limpio["estado"].map(lambda e: bool(re.fullmatch(r"[A-Z_]+", e))).all(),
          f"({sorted(limpio['estado'].unique())})")
duracion = (pd.to_datetime(limpio["fecha_fin"]) - pd.to_datetime(limpio["fecha_inicio"])).dt.days
verificar("duracion_dias = fin - inicio", duracion.fillna(-999).equals(limpio["duracion_dias"].fillna(-999).astype(float)))
verificar("fecha_valida marca las incoherentes",
          limpio["fecha_valida"].equals(limpio["duracion_dias"].ge(0)) and (~limpio["fecha_valida"]).sum() > 0,
          f"({(~limpio['fecha_valida']).sum()} con fecha_valida=False)")

# ---------- HU Q01: consultas ----------
# Corre el script de consultas: lee data/limpio/retos_limpio.csv y guarda retos_consulta_N.csv
print("\n=== HU Q01: consultas ===")
consultas.main()
print()

carpeta = limpieza.CARPETA_LIMPIO
verificar("existen los 5 archivos retos_consulta_N.csv",
          all((carpeta / f"retos_consulta_{n}.csv").exists() for n in range(1, 6)))

c1 = pd.read_csv(carpeta / "retos_consulta_1.csv")
verificar("consulta 1: solo retos EN_CURSO y estan todos",
          (c1["estado"] == "EN_CURSO").all() and len(c1) == (limpio["estado"] == "EN_CURSO").sum(),
          f"({len(c1)} retos)")

c2 = pd.read_csv(carpeta / "retos_consulta_2.csv", index_col=0)
verificar("consulta 2: 10 retos, de mayor a menor duracion",
          len(c2) == 10 and list(c2.columns) == ["nombre", "duracion_dias", "estado"]
          and c2["duracion_dias"].is_monotonic_decreasing)

c3 = pd.read_csv(carpeta / "retos_consulta_3.csv", index_col=0)
verificar("consulta 3: los conteos por estado suman todas las filas",
          c3.iloc[:, 0].sum() == len(limpio), f"({c3.iloc[:, 0].sum()} de {len(limpio)})")

c4 = pd.read_csv(carpeta / "retos_consulta_4.csv", index_col=0)
verificar("consulta 4: count, mean, min y max por estado",
          list(c4.columns) == ["count", "mean", "min", "max"]
          and c4["count"].sum() == limpio["duracion_dias"].notna().sum())

c5 = pd.read_csv(carpeta / "retos_consulta_5.csv", index_col=0)
verificar("consulta 5: los retos por mes suman todas las filas",
          c5.iloc[:, 0].sum() == len(limpio), f"({c5.iloc[:, 0].sum()} de {len(limpio)})")

funciones = [getattr(consultas, f"consulta_{n}", None) for n in range(1, 6)]
verificar("cada consulta esta en su propia funcion", all(callable(f) for f in funciones))
con_groupby = sum("groupby" in inspect.getsource(f) for f in funciones if callable(f))
verificar("al menos 2 consultas usan groupby", con_groupby >= 2, f"({con_groupby})")

# ---------- HU G01: graficas ----------
# Corre el script de graficas: lee data/limpio/retos_limpio.csv y guarda reportes/retos_grafica_N.png
print("\n=== HU G01: graficas ===")
salida = io.StringIO()
with contextlib.redirect_stdout(salida):   # se captura lo que imprime para poder revisarlo
    reporte.main()
texto = salida.getvalue()
print(texto)

rutas = [Path(reporte.CARPETA) / f"retos_grafica_{n}.png" for n in range(1, 4)]
verificar("existen las 3 imagenes en reportes/", all(r.exists() for r in rutas))
verificar("las 3 imagenes son PNG validos y no estan vacias",
          all(r.exists() and r.stat().st_size > 1000 and r.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" for r in rutas))

fuentes = [inspect.getsource(getattr(reporte, f"grafica_{n}")) for n in (1, 2, 3)]
verificar("grafica 1 es de barras", 'kind="bar"' in fuentes[0])
verificar("grafica 2 es de linea con marker='o'", 'kind="line"' in fuentes[1] and 'marker="o"' in fuentes[1])
verificar("grafica 3 es un histograma con 20 bins", 'kind="hist"' in fuentes[2] and "bins=20" in fuentes[2])
verificar("cada grafica tiene titulo, nombre en los 2 ejes y tight_layout",
          all(all(x in f for x in ("plt.title", "plt.xlabel", "plt.ylabel", "plt.tight_layout")) for f in fuentes))
verificar("se guarda con dpi=120 y plt.close() (sin plt.show())",
          all("dpi=120" in f and "plt.close()" in f and "plt.show()" not in f for f in fuentes))

incoherentes = int((limpio["duracion_dias"] < 0).sum())
verificar("conclusion 1: mes en que se concentran los retos", "¿En qué mes se concentran los retos" in texto)
verificar("conclusion 2: duracion promedio por estado", "¿Cuánto dura en promedio un reto según su estado?" in texto)
verificar("conclusion 3: retos con fecha de fin antes que la de inicio",
          f"{incoherentes} de {len(limpio)} retos" in texto, f"({incoherentes} de {len(limpio)})")

print(f"\nResultado: {sum(resultados)}/{len(resultados)} comprobaciones PASAN")