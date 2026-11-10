# Integrador_NT_martes2026-1

Proyecto integrador de nuevas tecnologías.

## Ejecutar el flujo

Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
python main.py
```

El comando ejecuta las cinco etapas del proyecto para empresas, registros,
retos y categorías. Para ejecutar únicamente el aporte de categorías:

```bash
python main.py categorias
```

También se pueden ejecutar etapas específicas en orden:

```bash
python main.py categorias exportar limpiar consultar reportar
```

Las categorías se exportan a `data/crudo/`, se limpian y consultan en
`data/limpio/`, y sus gráficas quedan en `data/reportes/`.
