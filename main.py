"""Punto de entrada del proyecto integrador (tabla empresas).

Corre las etapas del proyecto en orden:

    1. simular    -> src/notebook/simulacion/simular_empresas.py    (HU F01)
    2. exportar   -> src/notebook/exportacion/exportar_empresas.py  (HU X01)
    3. limpiar    -> src/notebook/limpieza/limpiar_empresas.py      (HU L01)
    4. consultar  -> src/notebook/consultas/consultas_empresas.py   (HU Q01)
    5. reportar   -> src/notebook/reportes/reporte_empresas.py      (HU G01)

Uso (desde la raiz del proyecto o desde cualquier otra carpeta):

    python main.py                    # corre las cinco etapas en orden
    python main.py simular            # solo la simulacion (no guarda archivos)
    python main.py exportar           # simula y guarda data/crudo/empresas_sucio.*
    python main.py limpiar            # limpia data/crudo y guarda data/limpio/
    python main.py consultar          # consulta data/limpio/empresas_limpio.csv
    python main.py reportar           # grafica data/limpio/empresas_limpio.csv
    python main.py simular exportar   # varias etapas, siempre en este orden
"""
import sys
from importlib import import_module
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
NOTEBOOK = RAIZ / "src" / "notebook"
ENTRADA_LIMPIEZA = RAIZ / "data" / "crudo" / "empresas_sucio.csv"
SALIDA_LIMPIEZA = RAIZ / "data" / "limpio"
ENTRADA_CONSULTAS = RAIZ / "data" / "limpio" / "empresas_limpio.csv"
SALIDA_CONSULTAS = RAIZ / "data" / "limpio" / "consultas"
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


def encabezado(titulo):
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


def etapa_simular():
    """HU F01: genera las empresas sucias en memoria y las muestra."""
    encabezado("ETAPA 1 - SIMULAR (HU F01)")
    simular = cargar("simulacion", "simular_empresas")
    df = simular.generar_empresas()
    print("df.shape:", df.shape)
    print(df.head())
    print(df.isna().sum())
    return df


def etapa_exportar(df=None):
    """HU X01: guarda el DataFrame sucio en data/crudo (csv, xlsx y json).
    Si viene de la etapa anterior, exporta ese mismo DataFrame."""
    encabezado("ETAPA 2 - EXPORTAR (HU X01)")
    exportar = cargar("exportacion", "exportar_empresas")
    if df is None:
        simular = cargar("simulacion", "simular_empresas")
        df = simular.generar_empresas()
    exportar.exportar_datos(df)
    return df


def etapa_limpiar():
    """HU L01: limpia data/crudo/empresas_sucio.csv y guarda los tres
    archivos limpios en data/limpio."""
    encabezado("ETAPA 3 - LIMPIAR (HU L01)")
    if not ENTRADA_LIMPIEZA.exists():
        raise SystemExit(
            f"No existe {ENTRADA_LIMPIEZA.relative_to(RAIZ)}. "
            "Ejecuta antes: python main.py exportar"
        )
    limpiar = cargar("limpieza", "limpiar_empresas")
    return limpiar.ejecutar(ENTRADA_LIMPIEZA, SALIDA_LIMPIEZA)


def etapa_consultar():
    """HU Q01: lee data/limpio/empresas_limpio.csv, resuelve las cinco
    consultas y guarda data/limpio/empresas_consulta_N.csv."""
    encabezado("ETAPA 4 - CONSULTAR (HU Q01)")
    if not ENTRADA_CONSULTAS.exists():
        raise SystemExit(
            f"No existe {ENTRADA_CONSULTAS.relative_to(RAIZ)}. "
            "Ejecuta antes: python main.py limpiar"
        )
    consultas = cargar("consultas", "consultas_empresas")
    df = consultas.leer_datos(ENTRADA_CONSULTAS)
    print(f"Archivo leído: {ENTRADA_CONSULTAS.relative_to(RAIZ)} ({df.shape[0]} filas)")
    consultas.consulta_1_activas(df, SALIDA_CONSULTAS)
    consultas.consulta_2_sector(df, SALIDA_CONSULTAS)
    consultas.consulta_3_conteo(df, SALIDA_CONSULTAS)
    consultas.consulta_4_groupby(df, SALIDA_CONSULTAS)
    consultas.consulta_5_groupby_doble(df, SALIDA_CONSULTAS)


def etapa_reportar():
    """HU G01: lee data/limpio/empresas_limpio.csv, crea las tres graficas
    en data/reportes/ e imprime las conclusiones."""
    encabezado("ETAPA 5 - REPORTAR (HU G01)")
    if not ENTRADA_REPORTES.exists():
        raise SystemExit(
            f"No existe {ENTRADA_REPORTES.relative_to(RAIZ)}. "
            "Ejecuta antes: python main.py limpiar"
        )
    reporte = cargar("reportes", "reporte_empresas")
    # El script guarda en la carpeta que diga CARPETA_REPORTES: se apunta
    # a data/reportes/ para que no dependa de desde donde se ejecute.
    reporte.CARPETA_REPORTES = str(SALIDA_REPORTES)
    SALIDA_REPORTES.mkdir(parents=True, exist_ok=True)

    df = reporte.cargar_datos(ENTRADA_REPORTES)
    print(f"Archivo leído: {ENTRADA_REPORTES.relative_to(RAIZ)} ({df.shape[0]} filas)")
    reporte.grafica_1_por_sector(df)
    reporte.grafica_2_activas_inactivas(df)
    reporte.grafica_3_apiladas(df)
    reporte.imprimir_conclusiones(df)


ETAPAS = ("simular", "exportar", "limpiar", "consultar", "reportar")


def main(argumentos):
    pedidas = [a.lower() for a in argumentos] or list(ETAPAS)
    desconocidas = [a for a in pedidas if a not in ETAPAS]
    if desconocidas:
        raise SystemExit(
            f"Etapa desconocida: {', '.join(desconocidas)}. "
            f"Usa: {', '.join(ETAPAS)} (o nada para correr todas)."
        )

    df = None
    for etapa in ETAPAS:  # siempre en orden, sin importar como se escribieron
        if etapa not in pedidas:
            continue
        if etapa == "simular":
            df = etapa_simular()
        elif etapa == "exportar":
            df = etapa_exportar(df)
        elif etapa == "limpiar":
            etapa_limpiar()
        elif etapa == "consultar":
            etapa_consultar()
        else:
            etapa_reportar()

    print("\nListo: etapas ejecutadas ->", ", ".join(e for e in ETAPAS if e in pedidas))


if __name__ == "__main__":
    main(sys.argv[1:])
