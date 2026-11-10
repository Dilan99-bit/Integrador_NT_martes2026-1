# Ejecutar desde la raiz del proyecto: python main.py [empresas|registros] [etapas]
"""Punto de entrada unico del proyecto integrador (empresas y registros).

Las dos entidades corren las mismas cinco etapas, en orden:

    1. simular    (HU F01)  genera los datos sucios en memoria
    2. exportar   (HU X01)  guarda data/crudo/<entidad>_sucio.csv, .xlsx y .json
    3. limpiar    (HU L01)  limpia el csv crudo y guarda data/limpio/<entidad>_limpio.*
    4. consultar  (HU Q01)  resuelve las cinco consultas sobre el csv limpio
    5. reportar   (HU G01)  crea las tres graficas en data/reportes/

Uso (desde la raiz del proyecto o desde cualquier otra carpeta):

    python main.py                            # empresas y registros
    python main.py empresas                   # las cinco etapas de empresas
    python main.py registros                  # las cinco etapas de registros
    python main.py registros exportar         # simula y guarda csv, xlsx y json
    python main.py registros limpiar consultar  # varias etapas en orden
"""
import sys
from importlib import import_module
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"
NOTEBOOK = SRC / "notebook"

# El paquete "notebook" (usado por registros) se importa desde src/
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ENTIDADES = ("empresas", "registros")
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
#  ENTRADA
# =====================================================================
def main(argumentos):
    args = [a.lower() for a in argumentos]

    if args and args[0] in ENTIDADES:
        entidades, pedidas = [args[0]], args[1:]
    else:
        entidades, pedidas = list(ENTIDADES), args  # sin entidad: corre ambas

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

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1:])