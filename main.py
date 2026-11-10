# Ejecutar desde la raiz del proyecto: python main.py [empresas|registros|retos] [etapas]
"""Punto de entrada unico del proyecto integrador (empresas, registros y retos).

Las tres entidades corren las mismas cinco etapas, en orden:

    1. simular    (HU F01)  genera los datos sucios en memoria
    2. exportar   (HU X01)  guarda data/crudo/<entidad>_sucio.csv, .xlsx y .json
    3. limpiar    (HU L01)  limpia el csv crudo y guarda data/limpio/<entidad>_limpio.*
    4. consultar  (HU Q01)  resuelve las cinco consultas sobre el csv limpio
    5. reportar   (HU G01)  crea las tres graficas en data/reportes/

Uso (desde la raiz del proyecto o desde cualquier otra carpeta):

    python main.py                            # empresas, registros y retos
    python main.py empresas                   # las cinco etapas de empresas
    python main.py registros                  # las cinco etapas de registros
    python main.py retos                      # las cinco etapas de retos
    python main.py retos exportar             # simula y guarda csv, xlsx y json
    python main.py retos limpiar consultar    # varias etapas en orden
"""
import contextlib
import inspect
import io
import json
import re
import sys
from importlib import import_module
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"
NOTEBOOK = SRC / "notebook"

# El paquete "notebook" (usado por registros) se importa desde src/
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
# El paquete "src" (usado por retos) se importa desde la raiz
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

ENTIDADES = ("empresas", "registros", "retos")
ETAPAS = ("simular", "exportar", "limpiar", "consultar", "reportar")


def encabezado(titulo):
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


# =====================================================================
#  EMPRESAS
# =====================================================================
ENTRADA_LIMPIEZA = RAIZ / "data" / "crudo" / "empresas_sucio.csv"
SALIDA_LIMPIEZA = RAIZ / "data" / "limpio"
ENTRADA_CONSULTAS = RAIZ / "data" / "limpio" / "empresas_limpio.csv"
SALIDA_CONSULTAS = RAIZ / "data" / "limpio" / "consulta"
ENTRADA_REPORTES = RAIZ / "data" / "limpio" / "empresas_limpio.csv"
SALIDA_REPORTES = RAIZ / "data" / "reportes"


def cargar(carpeta, modulo):
    """Importa un script de src/notebook/<carpeta>/ por su nombre.
    Todos se cargan con el mismo nombre de modulo, asi cada script se
    importa una sola vez aunque otro (exportar) tambien lo use."""
    ruta = str(NOTEBOOK / carpeta)
    if ruta not in sys.path:
        sys.path.insert(0, ruta)
    return import_module(modulo)


def emp_simular():
    """HU F01: genera las empresas sucias en memoria y las muestra."""
    encabezado("EMPRESAS - ETAPA 1 - SIMULAR (HU F01)")
    simular = cargar("simulacion", "simular_empresas")
    df = simular.generar_empresas()
    print("df.shape:", df.shape)
    print(df.head())
    print(df.isna().sum())
    return df


def emp_exportar(df=None):
    """HU X01: guarda el DataFrame sucio en data/crudo (csv, xlsx y json)."""
    encabezado("EMPRESAS - ETAPA 2 - EXPORTAR (HU X01)")
    exportar = cargar("exportacion", "exportar_empresas")
    if df is None:
        simular = cargar("simulacion", "simular_empresas")
        df = simular.generar_empresas()
    exportar.exportar_datos(df)
    return df


def emp_limpiar():
    """HU L01: limpia data/crudo/empresas_sucio.csv y guarda los tres
    archivos limpios en data/limpio."""
    encabezado("EMPRESAS - ETAPA 3 - LIMPIAR (HU L01)")
    if not ENTRADA_LIMPIEZA.exists():
        raise SystemExit(
            f"No existe {ENTRADA_LIMPIEZA.relative_to(RAIZ)}. "
            "Ejecuta antes: python main.py empresas exportar"
        )
    limpiar = cargar("limpieza", "limpiar_empresas")
    return limpiar.ejecutar(ENTRADA_LIMPIEZA, SALIDA_LIMPIEZA)


def emp_consultar():
    """HU Q01: lee data/limpio/empresas_limpio.csv y resuelve las cinco consultas."""
    encabezado("EMPRESAS - ETAPA 4 - CONSULTAR (HU Q01)")
    if not ENTRADA_CONSULTAS.exists():
        raise SystemExit(
            f"No existe {ENTRADA_CONSULTAS.relative_to(RAIZ)}. "
            "Ejecuta antes: python main.py empresas limpiar"
        )
    consultas = cargar("consultas", "consultas_empresas")
    df = consultas.leer_datos(ENTRADA_CONSULTAS)
    print(f"Archivo leído: {ENTRADA_CONSULTAS.relative_to(RAIZ)} ({df.shape[0]} filas)")
    consultas.consulta_1_activas(df, SALIDA_CONSULTAS)
    consultas.consulta_2_sector(df, SALIDA_CONSULTAS)
    consultas.consulta_3_conteo(df, SALIDA_CONSULTAS)
    consultas.consulta_4_groupby(df, SALIDA_CONSULTAS)
    consultas.consulta_5_groupby_doble(df, SALIDA_CONSULTAS)


def emp_reportar():
    """HU G01: crea las tres graficas en data/reportes/ e imprime las conclusiones."""
    encabezado("EMPRESAS - ETAPA 5 - REPORTAR (HU G01)")
    if not ENTRADA_REPORTES.exists():
        raise SystemExit(
            f"No existe {ENTRADA_REPORTES.relative_to(RAIZ)}. "
            "Ejecuta antes: python main.py empresas limpiar"
        )
    reporte = cargar("reportes", "reporte_empresas")
    reporte.CARPETA_REPORTES = str(SALIDA_REPORTES)
    SALIDA_REPORTES.mkdir(parents=True, exist_ok=True)

    df = reporte.cargar_datos(ENTRADA_REPORTES)
    print(f"Archivo leído: {ENTRADA_REPORTES.relative_to(RAIZ)} ({df.shape[0]} filas)")
    reporte.grafica_1_por_sector(df)
    reporte.grafica_2_activas_inactivas(df)
    reporte.grafica_3_apiladas(df)
    reporte.imprimir_conclusiones(df)


def correr_empresas(pedidas):
    df = None
    for etapa in ETAPAS:  # siempre en orden, sin importar como se escribieron
        if etapa not in pedidas:
            continue
        if etapa == "simular":
            df = emp_simular()
        elif etapa == "exportar":
            df = emp_exportar(df)
        elif etapa == "limpiar":
            emp_limpiar()
        elif etapa == "consultar":
            emp_consultar()
        else:
            emp_reportar()
    print("\nEmpresas listo: etapas ejecutadas ->",
          ", ".join(e for e in ETAPAS if e in pedidas))
    return True


# =====================================================================
#  REGISTROS (mismas etapas; cada una revisa sus criterios)
# =====================================================================
COLUMNAS_REGISTROS = ["id", "fecha_registro", "observacion", "estado", "id_usuario", "id_reto"]
ESTADOS_VALIDOS = ["en proceso", "finalizado", "inscrito"]
CARPETA_DATOS = RAIZ / "data"
CARPETA_LIMPIO = CARPETA_DATOS / "limpio"
CARPETA_CONSULTAS = CARPETA_LIMPIO / "consulta"
CARPETA_REPORTES = CARPETA_DATOS / "reportes"

resultados = []


def revisar(nombre, condicion, detalle=""):
    estado = "PASA " if condicion else "FALLA"
    resultados.append(bool(condicion))
    print(f"[{estado}] {nombre} {detalle}")


def _exportar_tres(df, carpeta, nombre):
    """Guarda el DataFrame en csv, xlsx y json (igual que empresas)."""
    from notebook.exportacion.exportar_registro import (
        exportar_csv, exportar_excel, exportar_json,
    )
    return [
        exportar_csv(df, carpeta, nombre),
        exportar_excel(df, carpeta, nombre),
        exportar_json(df, carpeta, nombre),
    ]


def _revisar_archivos(rutas, df, carpeta_nombre):
    import pandas as pd

    print()
    for ruta in rutas:
        print(f"{ruta} -> {df.shape}")
    print()
    for ruta in rutas:
        revisar(f"Existe {ruta.name}", ruta.exists() and ruta.stat().st_size > 0)
    revisar(f"Están en data/{carpeta_nombre}",
            all(r.parent.name == carpeta_nombre and r.parent.parent.name == "data" for r in rutas))

    # Se leen de vuelta para comprobar que el contenido quedó bien
    csv_df = pd.read_csv(rutas[0], encoding="utf-8")
    json_df = pd.read_json(rutas[2], orient="records")
    revisar("CSV se lee con las mismas filas y columnas", csv_df.shape == df.shape,
            f"-> {csv_df.shape}")
    with pd.ExcelFile(rutas[1]) as xlsx:
        revisar("Excel tiene la hoja 'registros'", "registros" in xlsx.sheet_names,
                f"-> {xlsx.sheet_names}")
    revisar("JSON se lee con las mismas filas y columnas", json_df.shape == df.shape,
            f"-> {json_df.shape}")


def reg_simular():
    """HU F01: genera los registros sucios en memoria y revisa los criterios."""
    import pandas as pd
    from notebook.simulacion.simular_registro import generar_registros

    encabezado("REGISTROS - ETAPA 1 - SIMULAR (HU F01)")
    df = generar_registros()

    print("\nshape:", df.shape)
    print("\nhead:")
    print(df.head())
    print("\nnulos por columna:")
    print(df.isna().sum())
    print()

    revisar("generar_registros() devuelve un DataFrame", isinstance(df, pd.DataFrame))
    revisar("Tiene las 6 columnas pedidas", list(df.columns) == COLUMNAS_REGISTROS,
            f"-> {list(df.columns)}")
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

    revisar("Hay duplicados exactos (~5%)", int(df.duplicated().sum()) >= 40,
            f"-> {int(df.duplicated().sum())}")
    pares = int(df.duplicated(subset=["id_usuario", "id_reto"]).sum())
    revisar("Hay pares id_usuario + id_reto repetidos", pares > 0, f"-> {pares}")
    return df


def reg_exportar(df=None):
    """HU X01: guarda el DataFrame sucio en data/crudo (csv, xlsx y json)."""
    from notebook.simulacion.simular_registro import generar_registros
    from notebook.exportacion.exportar_registro import CARPETA_CRUDO, NOMBRE_ENTIDAD

    encabezado("REGISTROS - ETAPA 2 - EXPORTAR (HU X01)")
    if df is None:
        df = generar_registros()
    rutas = _exportar_tres(df, CARPETA_CRUDO, f"{NOMBRE_ENTIDAD}_sucio")
    _revisar_archivos(rutas, df, "crudo")
    return df


def reg_limpiar():
    """HU L01: limpia data/crudo/registros_sucio.csv y guarda csv, xlsx y json
    limpios en data/limpio."""
    import pandas as pd
    from notebook.exportacion.exportar_registro import CARPETA_CRUDO, NOMBRE_ENTIDAD
    from notebook.limpieza.limpieza_registros import limpiar

    encabezado("REGISTROS - ETAPA 3 - LIMPIAR (HU L01)")
    entrada = Path(CARPETA_CRUDO) / f"{NOMBRE_ENTIDAD}_sucio.csv"
    if not entrada.exists():
        raise SystemExit(
            f"No existe {entrada}. Ejecuta antes: python main.py registros exportar"
        )

    sucio = pd.read_csv(entrada, encoding="utf-8")
    limpio = limpiar(sucio)

    print("\nshape antes:", sucio.shape, "| después:", limpio.shape)
    print("\nhead:")
    print(limpio.head())
    print("\nnulos por columna:")
    print(limpio.isna().sum())
    print()

    revisar("limpiar() devuelve un DataFrame", isinstance(limpio, pd.DataFrame))
    revisar("Conserva las 6 columnas", list(limpio.columns) == COLUMNAS_REGISTROS,
            f"-> {list(limpio.columns)}")
    revisar("No quedan filas duplicadas", int(limpio.duplicated().sum()) == 0)
    revisar("id es único", limpio["id"].is_unique,
            f"-> {limpio['id'].nunique()} de {len(limpio)}")
    revisar("Se eliminaron las 40 duplicadas (840 -> 800)", len(limpio) == 800,
            f"-> {len(limpio)}")
    revisar("No quedan nulos en ninguna columna", int(limpio.isna().sum().sum()) == 0)

    estados_limpios = sorted(limpio["estado"].unique().tolist())
    revisar("estado quedó con 3 valores en minúscula y sin espacios",
            estados_limpios == ESTADOS_VALIDOS, f"-> {estados_limpios}")

    fechas = limpio["fecha_registro"].astype(str)
    revisar("fecha_registro tiene un solo formato AAAA-MM-DD HH:MM:SS",
            bool(fechas.str.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$").all()))
    revisar("No hay fechas futuras",
            bool((pd.to_datetime(fechas) <= pd.Timestamp.today()).all()))

    CARPETA_LIMPIO.mkdir(parents=True, exist_ok=True)
    rutas = _exportar_tres(limpio, CARPETA_LIMPIO, f"{NOMBRE_ENTIDAD}_limpio")
    _revisar_archivos(rutas, limpio, "limpio")
    return limpio


def _leer_limpio():
    import pandas as pd
    from notebook.exportacion.exportar_registro import NOMBRE_ENTIDAD

    ruta = CARPETA_LIMPIO / f"{NOMBRE_ENTIDAD}_limpio.csv"
    if not ruta.exists():
        raise SystemExit(
            f"No existe {ruta.relative_to(RAIZ)}. Ejecuta antes: python main.py registros limpiar"
        )
    df = pd.read_csv(ruta, encoding="utf-8")
    print(f"Archivo leído: {ruta.relative_to(RAIZ)} ({df.shape[0]} filas)")
    return df


def reg_consultar():
    """HU Q01: lee data/limpio/registros_limpio.csv y resuelve las cinco consultas."""
    from notebook.consultas.consultas_registros import ejecutar_consultas

    encabezado("REGISTROS - ETAPA 4 - CONSULTAR (HU Q01)")
    limpio_csv = _leer_limpio()
    (finalizados, repetidos, conteo, top_retos, por_mes), rutas = ejecutar_consultas(
        limpio_csv, CARPETA_CONSULTAS
    )
    print()

    revisar("Son 5 consultas con su CSV cada una", len(rutas) == 5)
    for ruta in rutas:
        revisar(f"Existe {ruta.name}", ruta.exists() and ruta.stat().st_size > 0)
    revisar(
        "Están en data/limpio/consulta/consulta_N",
        all(r.parent.name == f"consulta_{n}" and r.parent.parent == CARPETA_CONSULTAS
            for n, r in enumerate(rutas, start=1)),
    )

    n_fin = int((limpio_csv["estado"] == "finalizado").sum())
    revisar("Consulta 1: solo trae estado finalizado y no queda vacía",
            len(finalizados) == n_fin and n_fin > 0 and (finalizados["estado"] == "finalizado").all(),
            f"-> {len(finalizados)}")
    revisar("Consulta 2: todas las filas repiten usuario + reto",
            bool(repetidos.duplicated(subset=["id_usuario", "id_reto"], keep=False).all())
            if len(repetidos) else True,
            f"-> {len(repetidos)}")
    revisar("Consulta 3: los conteos por estado suman todas las filas",
            int(conteo["cantidad"].sum()) == len(limpio_csv),
            f"-> {int(conteo['cantidad'].sum())}")
    revisar("Consulta 4: máximo 10 retos, ordenados de mayor a menor",
            len(top_retos) <= 10 and top_retos["participaciones"].is_monotonic_decreasing,
            f"-> {len(top_retos)} retos")
    revisar("Consulta 5: las participaciones por mes suman todas las filas",
            int(por_mes["participaciones"].sum()) == len(limpio_csv),
            f"-> {len(por_mes)} meses")


def reg_reportar():
    """HU G01: crea las tres graficas en data/reportes/ e imprime las conclusiones."""
    from notebook.reportes.reportes_registros import generar_reportes, imprimir_conclusiones

    encabezado("REGISTROS - ETAPA 5 - REPORTAR (HU G01)")
    limpio_csv = _leer_limpio()
    rutas, conclusiones = generar_reportes(limpio_csv, CARPETA_REPORTES)
    print()
    for ruta in rutas:
        print(ruta)
    imprimir_conclusiones(conclusiones)
    print()

    revisar("Son 3 gráficas PNG", len(rutas) == 3)
    for ruta in rutas:
        revisar(f"Existe {ruta.name}", ruta.exists() and ruta.stat().st_size > 0)
    revisar("Están en data/reportes/", all(r.parent == CARPETA_REPORTES for r in rutas))
    revisar("Los nombres son registros_grafica_1, _2 y _3",
            [r.name for r in rutas] ==
            ["registros_grafica_1.png", "registros_grafica_2.png", "registros_grafica_3.png"])
    revisar("Las conclusiones responden las 3 preguntas (reto, mes, duplicadas con 409)",
            len(conclusiones) >= 3 and "409" in conclusiones[2])


def correr_registros(pedidas):
    resultados.clear()
    df = None
    for etapa in ETAPAS:
        if etapa not in pedidas:
            continue
        if etapa == "simular":
            df = reg_simular()
        elif etapa == "exportar":
            df = reg_exportar(df)
        elif etapa == "limpiar":
            reg_limpiar()
        elif etapa == "consultar":
            reg_consultar()
        else:
            reg_reportar()

    print()
    print("=" * 60)
    print(f"REGISTROS - RESULTADO: {sum(resultados)} de {len(resultados)} pruebas pasan")
    print("=" * 60)
    print("Registros listo: etapas ejecutadas ->",
          ", ".join(e for e in ETAPAS if e in pedidas))
    return all(resultados)


# =====================================================================
#  RETOS (mismas etapas; csv, xlsx y json en data/crudo y data/limpio)
# =====================================================================
COLUMNAS_RETOS = ["id", "nombre", "descripcion", "fecha_inicio", "fecha_fin",
                  "estado", "id_empresa", "id_categoria", "id_prioridad"]
CARPETA_CONSULTAS_RETOS = RAIZ / "data" / "consulta"


def _modulos_retos():
    """Carga los módulos de retos desde los paquetes existentes."""
    from src.notebook.simulacion import simular_retos
    from src.notebook.exportacion import exportar_retos
    from src.notebook.limpieza import limpiar_retos
    from src.notebook.consultas import consultas_retos
    from src.notebook.reportes import reporte_retos
    return simular_retos, exportar_retos, limpiar_retos, consultas_retos, reporte_retos


def ret_simular():
    """HU F01: genera los retos sucios en memoria y revisa los criterios."""
    import pandas as pd

    encabezado("RETOS - ETAPA 1 - SIMULAR (HU F01)")
    simular = _modulos_retos()[0]
    df = simular.generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
    print()

    revisar("500 filas", len(df) == 500, f"({len(df)})")
    revisar("9 columnas en orden", list(df.columns) == COLUMNAS_RETOS)
    revisar("duplicados exactos ~5%", 20 <= df.duplicated().sum() <= 30, f"({df.duplicated().sum()})")
    revisar("descripcion ~12% nulos", 9 <= df["descripcion"].isna().mean() * 100 <= 15)
    revisar("fecha_fin ~8% nulos", 5 <= df["fecha_fin"].isna().mean() * 100 <= 11)
    revisar("nombre con espacios ~10%",
            7 <= (df["nombre"] != df["nombre"].str.strip()).mean() * 100 <= 13)
    revisar("fecha_inicio con 2 formatos",
            df["fecha_inicio"].str.contains("/").any() and df["fecha_inicio"].str.contains("-").any())
    fechas = _modulos_retos()[2].convertir_fechas(
        df[["fecha_inicio", "fecha_fin"]].copy()
    )
    revisar(
        "hay fecha_fin anterior a fecha_inicio",
        (fechas["fecha_fin"] < fechas["fecha_inicio"]).any(),
    )
    revisar("estado con variantes sucias",
            df["estado"].isin(["en_curso", "EN CURSO", " Cerrado "]).sum() == 3)
    revisar("es reproducible (misma semilla)", simular.generar_retos().equals(df))
    return df


def ret_exportar(df=None):
    """HU X01: guarda el DataFrame sucio en data/crudo (csv, xlsx y json)."""
    import pandas as pd

    encabezado("RETOS - ETAPA 2 - EXPORTAR (HU X01)")
    simular, exportar = _modulos_retos()[:2]
    if df is None:
        df = simular.generar_retos()

    for ruta in exportar.exportar_retos_crudos(df):
        print(f"{ruta} -> {df.shape}")
    print()

    crudo = exportar.CARPETA_CRUDO
    csv = crudo / "retos_sucio.csv"
    xlsx = crudo / "retos_sucio.xlsx"
    js = crudo / "retos_sucio.json"
    revisar("existen los 3 archivos en data/crudo", csv.exists() and xlsx.exists() and js.exists())
    revisar("CSV: 500 filas y 9 columnas", pd.read_csv(csv, encoding="utf-8").shape == (500, 9))
    revisar("XLSX: hoja 'retos' con 500 filas",
            pd.read_excel(xlsx, sheet_name="retos").shape == (500, 9))
    datos_json = json.loads(js.read_text(encoding="utf-8"))
    revisar("JSON: lista de 500 objetos", isinstance(datos_json, list) and len(datos_json) == 500)
    return df


def ret_limpiar():
    """HU L01: limpia data/crudo/retos_sucio.csv y guarda csv, xlsx y json
    limpios en data/limpio."""
    import pandas as pd

    encabezado("RETOS - ETAPA 3 - LIMPIAR (HU L01)")
    exportar, limpieza = _modulos_retos()[1:3]
    csv = exportar.CARPETA_CRUDO / "retos_sucio.csv"
    if not csv.exists():
        raise SystemExit(f"No existe {csv}. Ejecuta antes: python main.py retos exportar")

    sucio = limpieza.leer_csv(csv)
    filas_inicio = len(sucio)
    nulos_antes = sucio.isna().sum()
    limpieza.imprimir_diagnostico(sucio, "ANTES DE LIMPIAR")

    limpio = limpieza.quitar_duplicados(sucio)
    limpio = limpieza.convertir_fechas(limpio)
    limpio = limpieza.unificar_estado(limpio)
    limpio = limpieza.rellenar_descripciones(limpio)
    limpio = limpieza.crear_duracion(limpio)
    limpio, fin_antes, sin_fecha = limpieza.marcar_fechas_incoherentes(limpio)
    limpio = limpieza.quitar_filas_sin_obligatorios(limpio)
    limpio = limpieza.quitar_duplicados(limpio)

    limpieza.imprimir_diagnostico(limpio, "DESPUES DE LIMPIAR")
    nulos_despues = limpio.isna().sum()
    print("Nulos corregidos por columna (antes -> despues):")
    for columna in limpieza.COLUMNAS_ESPERADAS:
        print(f"  {columna}: {nulos_antes[columna]} -> {nulos_despues[columna]}")
    print(f"\nFilas con fecha_fin ANTERIOR a fecha_inicio: {fin_antes}")
    print(f"Filas sin fecha_fin (no se puede calcular la duracion): {sin_fecha}")
    print(f"Filas con fecha_valida = False (total): {int((~limpio['fecha_valida']).sum())}")
    print(f"Filas eliminadas: {filas_inicio - len(limpio)} (de {filas_inicio} a {len(limpio)})")
    limpieza.verificar_resultado(limpio)
    limpieza.guardar_limpio(limpio)
    print(f"Archivos limpios guardados en: {limpieza.CARPETA_LIMPIO}")
    print()

    crudo = pd.read_csv(csv)
    limpio = pd.read_csv(limpieza.RUTA_SALIDA, encoding="utf-8")
    revisar("existen los 3 archivos en data/limpio",
            all((limpieza.CARPETA_LIMPIO / f"retos_limpio.{e}").exists()
                for e in ("csv", "xlsx", "json")))
    revisar("sin duplicados exactos", limpio.duplicated().sum() == 0)
    revisar("solo se eliminaron los duplicados",
            len(limpio) == len(crudo) - crudo.duplicated().sum(),
            f"({len(crudo)} -> {len(limpio)})")
    revisar("sin nulos en columnas obligatorias",
            limpio[limpieza.COLUMNAS_OBLIGATORIAS].isna().sum().sum() == 0)
    revisar("descripcion sin nulos", limpio["descripcion"].isna().sum() == 0)
    revisar("descripciones vacias rellenas",
            (limpio["descripcion"] == "Sin descripcion").sum()
            >= crudo.drop_duplicates()["descripcion"].isna().sum())
    revisar("fechas con un solo formato (AAAA-MM-DD)",
            limpio["fecha_inicio"].str.match(r"^\d{4}-\d{2}-\d{2}$").all()
            and limpio["fecha_fin"].dropna().str.match(r"^\d{4}-\d{2}-\d{2}$").all())
    revisar("estado unificado (MAYUSCULAS, sin espacios)",
            limpio["estado"].map(lambda e: bool(re.fullmatch(r"[A-Z_]+", e))).all(),
            f"({sorted(limpio['estado'].unique())})")
    duracion = (pd.to_datetime(limpio["fecha_fin"]) - pd.to_datetime(limpio["fecha_inicio"])).dt.days
    revisar("duracion_dias = fin - inicio",
            duracion.fillna(-999).equals(limpio["duracion_dias"].fillna(-999).astype(float)))
    revisar("fecha_valida marca las incoherentes",
            limpio["fecha_valida"].equals(limpio["duracion_dias"].ge(0))
            and (~limpio["fecha_valida"]).sum() > 0,
            f"({(~limpio['fecha_valida']).sum()} con fecha_valida=False)")
    return limpio


def _leer_retos_limpio():
    import pandas as pd

    limpieza = _modulos_retos()[2]
    ruta = Path(limpieza.RUTA_SALIDA)
    if not ruta.exists():
        raise SystemExit(f"No existe {ruta}. Ejecuta antes: python main.py retos limpiar")
    return pd.read_csv(ruta, encoding="utf-8")


def ret_consultar():
    """HU Q01: guarda cada consulta de retos en data/consulta/consulta_N/."""
    import pandas as pd

    encabezado("RETOS - ETAPA 4 - CONSULTAR (HU Q01)")
    limpieza, consultas = _modulos_retos()[2:4]
    limpio = consultas.cargar_datos(limpieza.RUTA_SALIDA)

    CARPETA_CONSULTAS_RETOS.mkdir(parents=True, exist_ok=True)
    rutas_consultas = []
    for numero, consulta in enumerate(
        (consultas.consulta_1, consultas.consulta_2, consultas.consulta_3,
         consultas.consulta_4, consultas.consulta_5),
        start=1,
    ):
        resultado = consulta(limpio)
        carpeta_consulta = CARPETA_CONSULTAS_RETOS / f"consulta_{numero}"
        carpeta_consulta.mkdir(parents=True, exist_ok=True)
        destino = Path(consultas.guardar(resultado, carpeta_consulta, numero))
        rutas_consultas.append(destino)
        print(f"-> Guardado en {destino}")
    print()

    revisar("existen los 5 archivos retos_consulta_N.csv",
            len(rutas_consultas) == 5 and all(ruta.exists() for ruta in rutas_consultas))

    c1 = pd.read_csv(rutas_consultas[0])
    revisar("consulta 1: solo retos EN_CURSO y estan todos",
            (c1["estado"] == "EN_CURSO").all() and len(c1) == (limpio["estado"] == "EN_CURSO").sum(),
            f"({len(c1)} retos)")

    c2 = pd.read_csv(rutas_consultas[1], index_col=0)
    revisar("consulta 2: 10 retos, de mayor a menor duracion",
            len(c2) == 10 and list(c2.columns) == ["nombre", "duracion_dias", "estado"]
            and c2["duracion_dias"].is_monotonic_decreasing)

    c3 = pd.read_csv(rutas_consultas[2], index_col=0)
    revisar("consulta 3: los conteos por estado suman todas las filas",
            c3.iloc[:, 0].sum() == len(limpio), f"({c3.iloc[:, 0].sum()} de {len(limpio)})")

    c4 = pd.read_csv(rutas_consultas[3], index_col=0)
    revisar("consulta 4: count, mean, min y max por estado",
            list(c4.columns) == ["count", "mean", "min", "max"]
            and c4["count"].sum() == limpio["duracion_dias"].notna().sum())

    c5 = pd.read_csv(rutas_consultas[4], index_col=0)
    revisar("consulta 5: los retos por mes suman todas las filas",
            c5.iloc[:, 0].sum() == len(limpio), f"({c5.iloc[:, 0].sum()} de {len(limpio)})")

    funciones = [getattr(consultas, f"consulta_{n}", None) for n in range(1, 6)]
    revisar("cada consulta esta en su propia funcion", all(callable(f) for f in funciones))
    con_groupby = sum("groupby" in inspect.getsource(f) for f in funciones if callable(f))
    revisar("al menos 2 consultas usan groupby", con_groupby >= 2, f"({con_groupby})")


def ret_reportar():
    """HU G01: crea retos_grafica_1..3.png e imprime las conclusiones."""
    encabezado("RETOS - ETAPA 5 - REPORTAR (HU G01)")
    reporte = _modulos_retos()[4]
    limpieza = _modulos_retos()[2]
    reporte.CARPETA = str(CARPETA_REPORTES)
    CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)
    limpio = reporte.cargar_datos(limpieza.RUTA_SALIDA)

    salida = io.StringIO()
    por_mes = reporte.calcular_por_mes(limpio)
    rutas = [
        Path(reporte.grafica_1(limpio)),
        Path(reporte.grafica_2(por_mes)),
        Path(reporte.grafica_3(limpio)),
    ]
    with contextlib.redirect_stdout(salida):
        reporte.imprimir_conclusiones(limpio, por_mes)
    texto = salida.getvalue()
    print(texto)

    revisar("existen las 3 imagenes en data/reportes/", all(r.exists() for r in rutas))
    revisar("las 3 imagenes son PNG validos y no estan vacias",
            all(r.exists() and r.stat().st_size > 1000
                and r.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" for r in rutas))

    fuentes = [inspect.getsource(getattr(reporte, f"grafica_{n}")) for n in (1, 2, 3)]
    revisar("grafica 1 es de barras", 'kind="bar"' in fuentes[0])
    revisar("grafica 2 es de linea con marker='o'",
            'kind="line"' in fuentes[1] and 'marker="o"' in fuentes[1])
    revisar("grafica 3 es un histograma con 20 bins",
            'kind="hist"' in fuentes[2] and "bins=20" in fuentes[2])
    revisar("cada grafica tiene titulo, nombre en los 2 ejes y tight_layout",
            all(all(x in f for x in ("plt.title", "plt.xlabel", "plt.ylabel", "plt.tight_layout"))
                for f in fuentes))
    revisar("se guarda con dpi=120 y plt.close() (sin plt.show())",
            all("dpi=120" in f and "plt.close()" in f and "plt.show()" not in f for f in fuentes))

    incoherentes = int((limpio["duracion_dias"] < 0).sum())
    revisar("conclusion 1: mes en que se concentran los retos",
            "¿En qué mes se concentran los retos" in texto)
    revisar("conclusion 2: duracion promedio por estado",
            "¿Cuánto dura en promedio un reto según su estado?" in texto)
    revisar("conclusion 3: retos con fecha de fin antes que la de inicio",
            f"{incoherentes} de {len(limpio)} retos" in texto, f"({incoherentes} de {len(limpio)})")


def correr_retos(pedidas):
    resultados.clear()
    df = None
    for etapa in ETAPAS:
        if etapa not in pedidas:
            continue
        if etapa == "simular":
            df = ret_simular()
        elif etapa == "exportar":
            df = ret_exportar(df)
        elif etapa == "limpiar":
            ret_limpiar()
        elif etapa == "consultar":
            ret_consultar()
        else:
            ret_reportar()

    print()
    print("=" * 60)
    print(f"RETOS - RESULTADO: {sum(resultados)} de {len(resultados)} pruebas pasan")
    print("=" * 60)
    print("Retos listo: etapas ejecutadas ->",
          ", ".join(e for e in ETAPAS if e in pedidas))
    return all(resultados)


# =====================================================================
#  ENTRADA
# =====================================================================
def main(argumentos):
    args = [a.lower() for a in argumentos]

    if args and args[0] in ENTIDADES:
        entidades, pedidas = [args[0]], args[1:]
    else:
        entidades, pedidas = list(ENTIDADES), args  # sin entidad: corre todas

    desconocidas = [a for a in pedidas if a not in ETAPAS]
    if desconocidas:
        raise SystemExit(
            f"Etapa desconocida: {', '.join(desconocidas)}. "
            f"Usa: {', '.join(ETAPAS)} (o nada para correr todas)."
        )
    pedidas = pedidas or list(ETAPAS)

    ok = True
    if "empresas" in entidades:
        ok = correr_empresas(pedidas) and ok
    if "registros" in entidades:
        ok = correr_registros(pedidas) and ok
    if "retos" in entidades:
        ok = correr_retos(pedidas) and ok

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1:])