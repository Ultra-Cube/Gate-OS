"""FastAPI control API (experimental)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import uuid
import yaml

from gateos_manager.manifest.loader import load_manifest, ManifestValidationError
from gateos_manager.api.auth import verify_token
from gateos_manager.switch.orchestrator import switch_environment as orchestrate_switch
from gateos_manager.plugins.registry import discover_entrypoint_plugins
from gateos_manager.logging.structured import info, warn
from gateos_manager.api.rate_limit import consume as rate_consume

api_key_scheme = APIKeyHeader(name="x-token", auto_error=False)

app = FastAPI(
    title="Gate-OS Control API",
    version="0.0.3",
    description="Control API for Gate-OS (experimental). Token auth with optional rate limits.",
    contact={"name": "Ultra Cube Tech"},
)


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


@app.post("/switch/{name}", response_model=SwitchResponse, tags=["Switch"],
          summary="Switch to environment (token required)",
          description="Switches to the specified environment. Requires x-token header.",
          responses={401: {"description": "Unauthorized"}, 429: {"description": "Rate limit exceeded"}})
def switch_environment(
    name: str,
    request: Request,
    response: Response,
    x_token: str | None = Security(api_key_scheme),
    x_client_id: str | None = None
) -> SwitchResponse:
    if not verify_token(x_token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    client_key = x_client_id or "anon"
    allowed, limit, remaining, reset_at = rate_consume(f"switch:{client_key}")
    if limit is not None:
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        if reset_at is not None:
            response.headers["X-RateLimit-Reset"] = str(int(reset_at))
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    if name not in _ENV_CACHE:
        raise HTTPException(status_code=404, detail="Environment not found")
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    info("switch.request", environment=name, client=client_key, correlation_id=correlation_id)
    result = orchestrate_switch(name, Path("docs/architecture/schemas/environment-manifest.schema.yaml"), correlation_id=correlation_id)
    return SwitchResponse(status=result["status"], environment=name, correlation_id=correlation_id)


@app.on_event("shutdown")
def _shutdown_cleanup():  # pragma: no cover - placeholder
    info("api.shutdown")


def run_server(host: str, port: int, schema_path: Path) -> None:  # pragma: no cover
    # Discover plugins before loading environments
    discover_entrypoint_plugins()
    _load_all(schema_path)
    # Optional hot reload controlled via env flag
    import os
    if os.getenv("GATEOS_WATCH_ENABLED") == "1":
        from gateos_manager.watch.reloader import start_watch
        env_dir = Path("examples/environments")
        if env_dir.exists():
            def _reload():  # pragma: no cover - watcher side-effect
                _ENV_CACHE.clear()
                _load_all(schema_path)
                info("env.cache.reloaded", count=len(_ENV_CACHE))
            start_watch(env_dir, _reload)
    import uvicorn  # local import so optional dep

    uvicorn.run(app, host=host, port=port, log_level="info")