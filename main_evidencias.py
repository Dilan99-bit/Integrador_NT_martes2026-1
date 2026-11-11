"""Punto de entrada: simula, exporta, revisa, limpia, consulta y grafica los datos de evidencias.

Uso (desde la raíz del proyecto):
    python main.py
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))


def agregar_carpetas_al_path():
    """Agrega src/ y todas las carpetas de notebook/ a sys.path para poder importar los módulos."""
    for base in ("src", "notebook"):
        ruta_base = os.path.join(RAIZ, base)
        if not os.path.isdir(ruta_base):
            continue
        for carpeta, _subcarpetas, _archivos in os.walk(ruta_base):
            if "__pycache__" not in carpeta and carpeta not in sys.path:
                sys.path.insert(0, carpeta)


agregar_carpetas_al_path()

from exportar_evidencias import exportar
from simular_evidencias import generar_evidencias

RUTA_CSV = os.path.join(RAIZ, "data", "crudo", "evidencias_sucio.csv")
SCRIPT_REVISION = os.path.join(RAIZ, "scripts", "revisar_datos.py")
# Se usa el primero que exista (src/ o notebook/limpiar/)
CANDIDATOS_LIMPIEZA = [
    os.path.join(RAIZ, "src", "limpiar_evidencias.py"),
    os.path.join(RAIZ, "notebook", "limpiar", "limpiar_evidencias.py"),
    os.path.join(RAIZ, "notebook", "limpiar", "limpiar-evidencia.py"),
]
RUTA_LIMPIO = os.path.join(RAIZ, "data", "limpio", "evidencias_limpio.csv")
# Se usa el primero que exista (src/ o notebook/consultas/)
CANDIDATOS_CONSULTAS = [
    os.path.join(RAIZ, "src", "consultas_evidencias.py"),
    os.path.join(RAIZ, "notebook", "consultas", "consultas_evidencias.py"),
]
# Se usa el primero que exista (src/ o notebook/graficas/)
CANDIDATOS_GRAFICAS = [
    os.path.join(RAIZ, "src", "reporte_evidencias.py"),
    os.path.join(RAIZ, "notebook", "graficas", "reporte_evidencias.py"),
]


def main():
    """Genera los datos sucios, los exporta, corre la revisión, limpia el CSV, hace las consultas y grafica."""
    # 1. Simulación (HU F01)
    df = generar_evidencias(n=600)
    print(f"Datos simulados: {df.shape}")

    # 2. Exportación (HU X01)
    for ruta in exportar(df):
        print(f"Exportado: {ruta} -> {df.shape}")

    # 3. Revisión con el script de la skill (se omite si no existe)
    print()
    if os.path.isfile(SCRIPT_REVISION):
        resultado = subprocess.run([sys.executable, SCRIPT_REVISION, RUTA_CSV])
        if resultado.returncode != 0:
            return resultado.returncode
    else:
        print(f"Aviso: no existe {SCRIPT_REVISION}, se omite la revisión.")

    # 4. Limpieza (HU L01)
    print()
    script_limpieza = next((r for r in CANDIDATOS_LIMPIEZA if os.path.isfile(r)), None)
    if script_limpieza is None:
        print("Error: no se encontró limpiar_evidencias.py en src/ ni en notebook/limpiar/.")
        return 1
    resultado = subprocess.run([sys.executable, script_limpieza, RUTA_CSV, RUTA_LIMPIO])
    if resultado.returncode != 0:
        return resultado.returncode

    # 5. Consultas (HU Q01): lee el CSV limpio y guarda evidencias_consulta_N.csv en data/limpio/
    print()
    script_consultas = next((r for r in CANDIDATOS_CONSULTAS if os.path.isfile(r)), None)
    if script_consultas is None:
        print("Error: no se encontró consultas_evidencias.py en src/ ni en notebook/consultas/.")
        return 1
    resultado = subprocess.run([sys.executable, script_consultas, RUTA_LIMPIO])
    if resultado.returncode != 0:
        return resultado.returncode

    # 6. Gráficas y conclusiones (HU G01): lee el CSV limpio y guarda las 3 imágenes en reportes/
    print()
    script_graficas = next((r for r in CANDIDATOS_GRAFICAS if os.path.isfile(r)), None)
    if script_graficas is None:
        print("Error: no se encontró reporte_evidencias.py en src/ ni en notebook/graficas/.")
        return 1
    resultado = subprocess.run([sys.executable, script_graficas, RUTA_LIMPIO], cwd=RAIZ)
    return resultado.returncode


if __name__ == "__main__":
    sys.exit(main())