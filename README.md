# Integrador_NT_martes2026-1

Proyecto de analítica que genera gráficas PNG en `data/reportes` y las
expone por una API FastAPI en `http://localhost:8000`.

## Ejecutar el flujo

Desde la raíz del proyecto:

```powershell
pip install -r requirements.txt
python main.py
```

El comando ejecuta las cinco etapas del proyecto para empresas, registros,
retos y categorías. Para ejecutar únicamente el aporte de categorías:

```powershell
python main.py categorias
```

También se pueden ejecutar etapas específicas en orden:

```powershell
python main.py categorias exportar limpiar consultar reportar
```

Las categorías se exportan a `data/crudo/`, se limpian y consultan en
`data/limpio/`, y sus gráficas quedan en `data/reportes/`.

## Iniciar los servicios

Inicia Spring Boot en el puerto `8081` y después, desde la raíz de este
proyecto, inicia la API de analítica:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

El Frontend II se inicia desde
`C:\Users\dilan\Music\Integrador_frontend_II_2026` con `npm run dev`; Vite
queda en `http://localhost:3000`. El Frontend II usa la sesión de Spring por
cookie y configura la API de gráficas con `VITE_ANALYTICS_URL` en `.env`.

## Rutas y autenticación

- `GET /api/analytics/charts` devuelve el catálogo con `id`, `title`,
  `imageUrl`, `altText` y `generatedAt`.
- `GET /api/analytics/charts/{id}/image` devuelve el PNG real con
  `Content-Type: image/png`.
- Las rutas anteriores `GET /api/graficas` y
  `GET /graficas/{nombre-del-PNG}` se conservan.

El Frontend II envía la cookie de sesión de Spring con credenciales. La API
valida esa sesión consultando `GET http://localhost:8081/api/usuarios/me` y
permite analítica únicamente al rol `ADMIN`. `ANALYTICS_AUTH_VERIFY_URL`
permite cambiar el endpoint de validación; su valor predeterminado es el
anterior. Una sesión ausente o inválida recibe `401`, un rol insuficiente
recibe `403` y un backend de autenticación inaccesible recibe `503`.

Para una integración servidor-a-servidor también se puede configurar
`ANALYTICS_API_TOKEN` como secreto del servidor de analítica. No lo guardes en
el repositorio ni lo expongas al navegador en una variable `VITE_*`.

## CORS

FastAPI permite los orígenes exactos `http://localhost:3000` y
`http://localhost:5173`, y requiere credenciales para transportar la sesión.
Spring conserva `http://localhost:3000` y agrega `http://localhost:5173`.
No se permite el origen comodín `*`. La API de analítica acepta `GET` y los
encabezados `Authorization` y `Content-Type`.

## Gráficas

Los PNG se leen directamente desde `data/reportes`; no se vuelven a generar
al consultarlos. Para regenerarlos, ejecuta `python main.py`. La fecha
`generatedAt` refleja la última modificación del archivo en UTC. Las imágenes
usan `Cache-Control: private, no-cache, must-revalidate` para revalidar el
contenido después de regenerarlo.
