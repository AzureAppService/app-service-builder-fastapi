from datetime import datetime

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_serves_landing_page_and_deep_route():
    home = client.get("/")
    deep_route = client.get("/products/widget-1")

    assert home.status_code == 200
    assert home.headers["content-type"].startswith("text/html")
    assert "FastAPI backend is running" in home.text
    assert deep_route.status_code == 200
    assert "Widget 1" in deep_route.text


def test_reports_health_and_deployment_identity():
    health_response = client.get("/health")
    version_response = client.get("/api/version")
    health = health_response.json()
    app_version = version_response.json()

    assert health_response.status_code == 200
    assert version_response.status_code == 200
    assert health["status"] == "ok"
    assert health["app"] == "app-service-builder-fastapi"
    assert app_version["app"] == "app-service-builder-fastapi"
    assert app_version["framework"].startswith("FastAPI ")
    assert app_version["runtime"]


def test_root_actions_keep_health_inline_and_customization_local():
    home = client.get("/")
    assert 'data-health-app="app-service-builder-fastapi">Check app health' in home.text
    assert 'role="status"' in home.text
    assert "<summary>Customize this sample</summary>" in home.text
    assert "In your fork" in home.text
    assert 'href="https://fastapi.tiangolo.com/">FastAPI documentation' in home.text
    assert 'href="https://docs.python.org/3/">Python documentation' in home.text
    assert (
        'href="https://builder.appservice.azure.com/docs/">App Service Builder documentation'
        in home.text
    )
    for asset in ["/assets/styles.v2.css", "/assets/health.v1.js",
                  "/assets/brand/family.v1.css", "/assets/brand/builder.svg",
                  "/assets/brand/fastapi.svg"]:
        assert asset in home.text
        response = client.get(asset)
        assert response.status_code == 200
        assert len(response.content) > 0


def test_reports_availability_and_serves_stylesheet():
    status = client.get("/api/status")
    stylesheet = client.get("/assets/styles.v1.css")

    assert status.status_code == 200
    assert status.headers["content-type"].startswith("application/json")
    assert status.json()["status"] == "available"
    assert datetime.fromisoformat(status.json()["timestamp"]).tzinfo is not None
    assert stylesheet.status_code == 200
    assert stylesheet.headers["content-type"].startswith("text/css")
    assert ":root" in stylesheet.text


def test_reports_public_markers_and_escapes_them_in_html(monkeypatch):
    marker = "<sample>&demo"
    monkeypatch.setenv("DEPLOYMENT_MARKER", marker)
    monkeypatch.setenv("BUILD_MARKER", "build-demo")
    monkeypatch.setenv("RUNTIME_MARKER", "runtime-demo")

    home = client.get("/")
    health = client.get("/health").json()
    app_version = client.get("/api/version").json()

    assert marker not in home.text
    assert "&lt;sample&gt;&amp;demo" in home.text
    assert health["deploymentMarker"] == marker
    assert app_version["deploymentMarker"] == marker
    assert app_version["buildMarker"] == "build-demo"
    assert app_version["runtimeMarker"] == "runtime-demo"


def test_serves_openapi_schema_without_documentation_ui():
    schema = client.get("/openapi.json")

    assert schema.status_code == 200
    assert schema.json()["info"]["title"] == "App Service Builder: FastAPI sample"
    assert "/health" in schema.json()["paths"]
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404


def test_returns_safe_request_metadata():
    response = client.get(
        "/api/request",
        headers={
            "cookie": "session=demo",
            "user-agent": "builder-app-shape-test",
            "authorization": "Bearer must-not-be-returned",
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["method"] == "GET"
    assert body["path"] == "/api/request"
    assert body["headers"]["userAgent"] == "builder-app-shape-test"
    assert "authorization" not in body["headers"]
    assert "cookie" not in body["headers"]


def test_distinguishes_page_and_api_misses():
    page = client.get("/missing-page")
    api = client.get("/api/missing")

    assert page.status_code == 404
    assert "Page not found" in page.text
    assert api.status_code == 404
    assert api.json() == {
        "error": "not_found",
        "message": "The requested API route does not exist.",
    }
