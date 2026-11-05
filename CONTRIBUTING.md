# Contributing to App Service Builder: FastAPI sample

This project welcomes contributions and suggestions.

## Contributor License Agreement

Most contributions require a Contributor License Agreement (CLA) declaring
that you have the right to grant us the rights to use your contribution.
See [Microsoft Contributor License Agreements](https://cla.opensource.microsoft.com/).
Follow any CLA instructions shown on your pull request.

## Code of Conduct

This project follows the
[Microsoft Open Source Code of Conduct](.github/CODE_OF_CONDUCT.md).

## Issues and feature requests

Search [existing issues](https://github.com/AzureAppService/app-service-builder-fastapi/issues)
before opening a new one. Include reproduction steps, expected and actual
behavior, Python version, operating system, and sanitized logs.
For larger changes, open an issue to discuss the proposal first.

Do not include credentials, private environment values, or other sensitive
information. For security concerns, follow [the security policy](SECURITY.md)
instead of opening a public issue.

## Development and pull requests

1. Fork the repository and create a branch for your change.
2. Create a virtual environment and install `requirements-dev.txt` as described
   in [the README](README.md).
3. Keep the sample standalone, small, and free of external service dependencies.
4. Add or update tests for behavior changes and update relevant documentation.
5. Run the tests and describe the changes and results in your pull request.

Windows PowerShell:

```powershell
.\.venv\Scripts\python -m pytest
```

Linux or macOS:

```sh
.venv/bin/python -m pytest
```

For startup or routing changes, also run the server and check the endpoints
listed in [the README](README.md). PowerShell 7 users can run:

```powershell
pwsh -NoProfile -File .\scripts\verify.ps1 -BaseUrl http://localhost:8080
```

Preserve the `/health` response and the startup contract in `builder.yaml`.
Local tests do not replace deployment verification when the manifest changes.
Do not commit virtual environments, caches, environment files, or credentials.
