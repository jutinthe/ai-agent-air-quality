# Air Quality–Health Research Agent

## Install

```bash
uv sync
```

## Run tests

```bash
uv run pytest -v
```

## Start the API

```bash
uv run fastapi dev app/main.py
```

Open:

- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Extraction schema: http://127.0.0.1:8000/schema/extraction

## Export the JSON schema

```bash
uv run python -m app.utils.export_schema
```
