"""Exporta el mismo conjunto sucio de categorias a CSV, Excel y JSON."""

from pathlib import Path

from src.notebook.simulacion.simular_categorias import generar_categorias


RAIZ = Path(__file__).resolve().parents[3]
CARPETA_CRUDO = RAIZ / "data" / "crudo"


def exportar_categorias(df):
    """Guarda el DataFrame sucio en los tres formatos del proyecto."""
    CARPETA_CRUDO.mkdir(parents=True, exist_ok=True)
    rutas = [
        CARPETA_CRUDO / "categorias_sucio.csv",
        CARPETA_CRUDO / "categorias_sucio.xlsx",
        CARPETA_CRUDO / "categorias_sucio.json",
    ]
    df.to_csv(rutas[0], index=False, encoding="utf-8")
    df.to_excel(rutas[1], index=False, sheet_name="categorias")
    df.to_json(rutas[2], orient="records", force_ascii=False, indent=2)
    return rutas


def main() -> None:
    df = generar_categorias()
    for ruta in exportar_categorias(df):
        print(
            f"Generado: {ruta.relative_to(RAIZ)} | "
            f"df.shape: {df.shape} | tamaño: {ruta.stat().st_size} bytes"
        )


if __name__ == "__main__":
    main()
