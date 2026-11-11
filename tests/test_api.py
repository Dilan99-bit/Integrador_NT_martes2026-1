import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch

import httpx
from PIL import Image

import api


class GraficasApiTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.carpeta = Path(self.temp_dir.name)
        patcher = patch.object(api, "CARPETA_GRAFICAS", self.carpeta)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.temp_dir.cleanup)
        token_patcher = patch.dict(os.environ, {"ANALYTICS_API_TOKEN": "test-token"})
        token_patcher.start()
        self.addCleanup(token_patcher.stop)
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=api.app),
            base_url="http://testserver",
            headers={"Authorization": "Bearer test-token"},
        )
        self.addAsyncCleanup(self.client.aclose)

    def crear_png(self, nombre: str) -> None:
        Image.new("RGB", (2, 2), color="blue").save(self.carpeta / nombre, format="PNG")

    async def test_legacy_catalog_includes_only_valid_png_files(self):
        self.crear_png("empresas_grafica_1.png")
        (self.carpeta / "archivo_danado.png").write_bytes(b"not a PNG")
        (self.carpeta / "no_es_grafica.txt").write_text("archivo de texto", encoding="utf-8")

        respuesta = await self.client.get("/api/graficas")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json(),
            [{
                "title": "Cantidad de empresas por sector",
                "image_url": "/graficas/empresas_grafica_1.png",
            }],
        )

    async def test_analytics_catalog_includes_metadata_for_valid_png_files(self):
        self.crear_png("empresas_grafica_1.png")
        (self.carpeta / "archivo_danado.png").write_bytes(b"not a PNG")

        respuesta = await self.client.get("/api/analytics/charts")

        self.assertEqual(respuesta.status_code, 200)
        grafica = respuesta.json()[0]
        self.assertEqual(grafica["id"], "empresas_grafica_1")
        self.assertEqual(grafica["title"], "Cantidad de empresas por sector")
        self.assertEqual(
            grafica["imageUrl"],
            "/api/analytics/charts/empresas_grafica_1/image",
        )
        self.assertEqual(grafica["altText"], grafica["title"])
        self.assertRegex(grafica["generatedAt"], r"^\d{4}-\d\d-\d\dT.*Z$")
        self.assertEqual(len(respuesta.json()), 1)

    async def test_analytics_image_route_serves_png_and_handles_missing_charts(self):
        self.crear_png("retos_grafica_1.png")
        (self.carpeta / "archivo_danado.png").write_bytes(b"not a PNG")

        respuesta = await self.client.get(
            "/api/analytics/charts/retos_grafica_1/image"
        )
        no_encontrada = await self.client.get(
            "/api/analytics/charts/inexistente/image"
        )
        danada = await self.client.get(
            "/api/analytics/charts/archivo_danado/image"
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.headers["content-type"], "image/png")
        self.assertEqual(
            respuesta.headers["cache-control"],
            "private, no-cache, must-revalidate",
        )
        self.assertEqual(respuesta.content[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(no_encontrada.status_code, 404)
        self.assertEqual(danada.status_code, 404)

    async def test_legacy_static_route_still_serves_only_valid_png_files(self):
        self.crear_png("retos_grafica_1.png")
        (self.carpeta / "archivo_danado.png").write_bytes(b"not a PNG")

        respuesta = await self.client.get("/graficas/retos_grafica_1.png")
        archivo_danado = await self.client.get("/graficas/archivo_danado.png")
        extension_invalida = await self.client.get("/graficas/retos_grafica_1.txt")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.headers["content-type"], "image/png")
        self.assertEqual(respuesta.content[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(archivo_danado.status_code, 404)
        self.assertEqual(extension_invalida.status_code, 404)

    async def test_protected_routes_reject_missing_or_invalid_tokens(self):
        sin_token = await self.client.get(
            "/api/analytics/charts",
            headers={"Authorization": "Basic not-a-bearer-token"},
        )
        legacy_sin_token = await self.client.get(
            "/api/graficas",
            headers={"Authorization": "Basic not-a-bearer-token"},
        )
        respuesta_sesion = httpx.Response(
            401,
            request=httpx.Request("GET", api.URL_VALIDACION_SESION),
        )
        cliente_backend = AsyncMock()
        cliente_backend.__aenter__.return_value = cliente_backend
        cliente_backend.__aexit__.return_value = False
        cliente_backend.get.return_value = respuesta_sesion
        with patch.object(api.httpx, "AsyncClient", return_value=cliente_backend):
            token_invalido = await self.client.get(
                "/api/analytics/charts",
                headers={"Authorization": "Bearer wrong-token"},
            )

        self.assertEqual(sin_token.status_code, 401)
        self.assertEqual(sin_token.headers["www-authenticate"], "Bearer")
        self.assertEqual(legacy_sin_token.status_code, 401)
        self.assertEqual(token_invalido.status_code, 401)

    async def test_session_cookie_is_validated_and_requires_admin_role(self):
        respuesta_admin = httpx.Response(
            200,
            json={"idusuario": "1", "rol": "ADMIN"},
            request=httpx.Request("GET", api.URL_VALIDACION_SESION),
        )
        cliente_backend = AsyncMock()
        cliente_backend.__aenter__.return_value = cliente_backend
        cliente_backend.__aexit__.return_value = False
        cliente_backend.get.return_value = respuesta_admin

        with patch.object(api.httpx, "AsyncClient", return_value=cliente_backend):
            respuesta = await self.client.get(
                "/api/analytics/charts",
                headers={
                    "Authorization": "",
                    "Cookie": "JSESSIONID=session-id",
                },
            )

        self.assertEqual(respuesta.status_code, 200)
        cliente_backend.get.assert_awaited_once_with(
            api.URL_VALIDACION_SESION,
            headers={"Cookie": "JSESSIONID=session-id"},
        )

        respuesta_empresa = httpx.Response(
            200,
            json={"idusuario": "2", "rol": "EMPRESA"},
            request=httpx.Request("GET", api.URL_VALIDACION_SESION),
        )
        cliente_backend.get.return_value = respuesta_empresa
        with patch.object(api.httpx, "AsyncClient", return_value=cliente_backend):
            sin_permiso = await self.client.get(
                "/api/analytics/charts",
                headers={
                    "Authorization": "",
                    "Cookie": "JSESSIONID=company-session",
                },
            )

        self.assertEqual(sin_permiso.status_code, 403)

    async def test_cors_preserves_existing_origin_and_adds_vite_origin(self):
        def preflight(origin, method="GET"):
            return self.client.options(
                "/api/analytics/charts",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": method,
                    "Access-Control-Request-Headers": "authorization,content-type",
                },
            )

        vite_permitida = await preflight("http://localhost:5173")
        origen_existente = await preflight("http://localhost:3000")
        no_permitida = await preflight("http://localhost:3001")
        metodo_no_permitido = await preflight("http://localhost:5173", "POST")

        self.assertEqual(vite_permitida.status_code, 200)
        self.assertEqual(
            vite_permitida.headers["access-control-allow-origin"],
            "http://localhost:5173",
        )
        self.assertIn(
            "authorization",
            vite_permitida.headers["access-control-allow-headers"].lower(),
        )
        self.assertIn(
            "content-type",
            vite_permitida.headers["access-control-allow-headers"].lower(),
        )
        self.assertEqual(
            origen_existente.headers["access-control-allow-origin"],
            "http://localhost:3000",
        )
        self.assertEqual(
            vite_permitida.headers["access-control-allow-credentials"],
            "true",
        )
        self.assertEqual(no_permitida.status_code, 400)
        self.assertNotIn("access-control-allow-origin", no_permitida.headers)
        self.assertEqual(metodo_no_permitido.status_code, 400)


if __name__ == "__main__":
    unittest.main()
