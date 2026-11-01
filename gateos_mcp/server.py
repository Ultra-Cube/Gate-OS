"""Minimal dependency-free MCP stdio stub for safe Gate-OS development."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

TOOLS = [
    {"name": "list_environments", "description": "List example Gate-OS environment manifests.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "describe_environment", "description": "Read an example environment manifest by name.", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "validate_manifest", "description": "Report the requested manifest path for offline validation integration.", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "switch_environment", "description": "Request a dry-run switch; live mutation is disabled by default.", "inputSchema": {"type": "object", "properties": {"environment": {"type": "string"}, "dry_run": {"type": "boolean"}, "confirm": {"type": "boolean"}}, "required": ["environment"]}},
    {"name": "get_status", "description": "Return local development status.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "get_metrics", "description": "Return metrics integration status without contacting external services.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "run_tests", "description": "Describe the test command; execution requires explicit confirmation.", "inputSchema": {"type": "object", "properties": {"confirm": {"type": "boolean"}}}},
]


def _text(value: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, sort_keys=True)}]}


def _call(name: str, args: dict[str, Any]) -> dict[str, Any]:
    root = Path.cwd()
    if name == "list_environments":
        paths = sorted((root / "examples" / "environments").glob("*.yaml"))
        return _text({"environments": [p.stem for p in paths], "read_only": True})
    if name == "describe_environment":
        path = (root / "examples" / "environments" / f"{args['name']}.yaml").resolve()
        if root.resolve() not in path.parents:
            return _text({"error": "path outside workspace"})
        return _text({"path": str(path), "exists": path.is_file(), "read_only": True})
    if name == "validate_manifest":
        return _text({"path": args["path"], "status": "delegated_to_gateos_cli", "read_only": True})
    if name == "switch_environment":
        if os.getenv("GATEOS_MCP_READ_ONLY", "1") == "1" or not args.get("dry_run", False):
            return _text({"status": "blocked", "reason": "read-only mode requires dry_run=true", "environment": args["environment"]})
        return _text({"status": "dry_run", "environment": args["environment"]})
    if name == "get_status":
        return _text({"status": "local-dev", "read_only": True})
    if name == "get_metrics":
        return _text({"status": "offline", "read_only": True})
    if name == "run_tests":
        return _text({"status": "blocked" if not args.get("confirm") else "manual-command-required", "command": "make test"})
    return _text({"error": f"unknown tool: {name}"})


def main() -> None:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            if method == "initialize":
                result = {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}}, "serverInfo": {"name": "gateos-mcp", "version": "0.1.0"}}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = request.get("params", {})
                result = _call(params.get("name", ""), params.get("arguments", {}))
            elif method == "notifications/initialized":
                continue
            else:
                result = {"error": {"code": -32601, "message": "method not found"}}
            print(json.dumps({"jsonrpc": "2.0", "id": request.get("id"), "result": result}), flush=True)
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": str(exc)}}), flush=True)


if __name__ == "__main__":
    main()
