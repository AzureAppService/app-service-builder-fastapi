import html
import os
import platform
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

APP_NAME = "app-service-builder-fastapi"
APP_VERSION = "1.0.0"
PUBLIC_DIRECTORY = Path(__file__).parent / "public"

app = FastAPI(
    title="App Service Builder: FastAPI sample",
    version=APP_VERSION,
    docs_url=None,
    redoc_url=None,
)
app.mount(
    "/assets",
    StaticFiles(directory=PUBLIC_DIRECTORY),
    name="assets",
)


def deployment_info() -> dict[str, str]:
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "framework": f"FastAPI {version('fastapi')}",
        "runtime": platform.python_version(),
        "deploymentMarker": os.getenv("DEPLOYMENT_MARKER", "local"),
        "buildMarker": os.getenv("BUILD_MARKER", "local"),
        "runtimeMarker": os.getenv("RUNTIME_MARKER", "local"),
    }


def page(title: str, content: str) -> str:
    info = {key: html.escape(value) for key, value in deployment_info().items()}

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{html.escape(title)}</title>
    <link rel="stylesheet" href="/assets/styles.v2.css">
    <script type="module" src="/assets/health.v1.js"></script>
  </head>
  <body>
    <main>
      <p class="eyebrow">App Service Builder / FastAPI</p>
      <h1>{html.escape(title)}</h1>
      {content}
      <dl>
        <div><dt>Application</dt><dd>{info["app"]} {info["version"]}</dd></div>
        <div><dt>Framework</dt><dd>{info["framework"]}</dd></div>
        <div><dt>Runtime</dt><dd>{info["runtime"]}</dd></div>
        <div><dt>Deployment</dt><dd>{info["deploymentMarker"]}</dd></div>
        <div><dt>Build setting</dt><dd>{info["buildMarker"]}</dd></div>
        <div><dt>Runtime setting</dt><dd>{info["runtimeMarker"]}</dd></div>
      </dl>
    </main>
  </body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home() -> str:
    return page(
        "FastAPI backend is running",
        '<p>The application started successfully and is serving HTTP traffic.</p>'
        f"""<nav aria-label="Sample actions">
        <a class="button" href="/products/widget-1">Open the deep route</a>
        <button class="secondary" type="button" data-health-app="{APP_NAME}">Check app health</button>
        <a href="/api/version">View version JSON</a>
      </nav>
      <p class="health-result" role="status">Check the JSON health endpoint without leaving this page.</p>
      <details>
        <summary>Customize this sample</summary>
        <p>In your fork, edit the home page title and content in <code>main.py</code>
        and the styles in <code>public/styles.v2.css</code>. Commit your changes and
        deploy your fork through your Builder App.</p>
      </details>
      <nav class="documentation" aria-label="Documentation">
        <a href="https://fastapi.tiangolo.com/">Framework documentation</a>
        <a href="https://builderapps.azure.com/docs/">App Service Builder documentation</a>
      </nav>""",
    )


@app.get("/products/widget-1", response_class=HTMLResponse)
async def product() -> str:
    return page(
        "Widget 1",
        "<p>This page proves that direct navigation to a server-rendered deep "
        'route works.</p><p><a href="/">Return home</a></p>',
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": APP_NAME,
        "deploymentMarker": os.getenv("DEPLOYMENT_MARKER", "local"),
    }


@app.get("/api/status")
async def status() -> dict[str, str]:
    return {
        "status": "available",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/api/version")
async def api_version() -> dict[str, str]:
    return deployment_info()


@app.get("/api/request")
async def request_metadata(request: Request) -> dict[str, object]:
    return {
        "method": request.method,
        "path": request.url.path,
        "headers": {
            "host": request.headers.get("host"),
            "userAgent": request.headers.get("user-agent"),
            "forwardedProto": request.headers.get("x-forwarded-proto"),
        },
    }


@app.exception_handler(404)
async def not_found(request: Request, _exception: Exception):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={
                "error": "not_found",
                "message": "The requested API route does not exist.",
            },
        )

    return HTMLResponse(
        status_code=404,
        content=page(
            "Page not found",
            '<p>The requested page does not exist.</p><p><a href="/">Return home</a></p>',
        ),
    )


def configured_port() -> int:
    raw_port = os.getenv("PORT", "8080")

    try:
        port = int(raw_port)
    except ValueError as error:
        raise ValueError(
            f'PORT must be an integer between 1 and 65535; received "{raw_port}".'
        ) from error

    if not 1 <= port <= 65535:
        raise ValueError(
            f'PORT must be an integer between 1 and 65535; received "{raw_port}".'
        )

    return port


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=configured_port(),
    )
