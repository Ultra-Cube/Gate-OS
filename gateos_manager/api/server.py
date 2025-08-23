"""FastAPI control API (experimental)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uuid
import yaml

from gateos_manager.manifest.loader import load_manifest, ManifestValidationError
from gateos_manager.api.auth import verify_token
from gateos_manager.switch.orchestrator import switch_environment as orchestrate_switch
from gateos_manager.api.rate_limit import allow as rate_allow

app = FastAPI(title="Gate-OS Control API", version="0.0.1")


class EnvironmentSummary(BaseModel):
    name: str
    category: str


class SwitchResponse(BaseModel):
    status: str
    environment: str
    correlation_id: str

_ENV_CACHE: dict[str, dict[str, Any]] = {}


def _load_all(schema_path: Path) -> None:
    examples = Path("examples/environments")
    if not examples.exists():
        return
    for f in examples.glob("*.yaml"):
        try:
            data = load_manifest(f, schema_path)
            _ENV_CACHE[data["metadata"]["name"]] = data
        except ManifestValidationError:
            continue


@app.get("/environments", response_model=list[EnvironmentSummary])
def list_environments() -> list[EnvironmentSummary]:  # pragma: no cover - thin wrapper
    return [EnvironmentSummary(name=k, category=v["spec"]["profile"]["category"]) for k, v in sorted(_ENV_CACHE.items())]


@app.get("/environments/{name}")
def get_environment(name: str) -> dict[str, Any]:  # pragma: no cover
    if name not in _ENV_CACHE:
        raise HTTPException(status_code=404, detail="Environment not found")
    return _ENV_CACHE[name]


@app.post("/switch/{name}", response_model=SwitchResponse)
def switch_environment(name: str, request: Request, x_token: str | None = None, x_client_id: str | None = None) -> SwitchResponse:  # pragma: no cover - thin wrapper
    if not verify_token(x_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    client_key = x_client_id or "anon"
    if not rate_allow(f"switch:{client_key}"):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    if name not in _ENV_CACHE:
        raise HTTPException(status_code=404, detail="Environment not found")
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    result = orchestrate_switch(name, Path("docs/architecture/schemas/environment-manifest.schema.yaml"))
    return SwitchResponse(status=result["status"], environment=name, correlation_id=correlation_id)


def run_server(host: str, port: int, schema_path: Path) -> None:  # pragma: no cover
    _load_all(schema_path)
    import uvicorn  # local import so optional dep

    uvicorn.run(app, host=host, port=port, log_level="info")