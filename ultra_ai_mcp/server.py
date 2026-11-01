"""Dependency-free offline MCP stub for the Gate-OS/Ultra AI contract."""
from __future__ import annotations

import json
import sys
from typing import Any

TOOLS = [
    {"name": "describe_contract", "description": "Return the local Ultra AI integration contract status.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "preview_ui_spec", "description": "Preview a declarative UI spec without executing code.", "inputSchema": {"type": "object", "properties": {"spec": {"type": "object"}}, "required": ["spec"]}},
    {"name": "request_action", "description": "Record an action request for policy review; never execute it.", "inputSchema": {"type": "object", "properties": {"action": {"type": "string"}, "confirm": {"type": "boolean"}}, "required": ["action"]}},
]


def _text(value: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, sort_keys=True)}]}


def main() -> None:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            if method == "initialize":
                result = {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}}, "serverInfo": {"name": "ultra-ai-mcp", "version": "0.1.0"}}
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                if name == "describe_contract":
                    result = _text({"mode": "offline", "native_components_only": True, "external_network": False})
                elif name == "preview_ui_spec":
                    result = _text({"status": "preview-only", "keys": sorted(args.get("spec", {}).keys())})
                elif name == "request_action":
                    result = _text({"status": "requires_gateos_policy", "action": args.get("action"), "confirmed": bool(args.get("confirm"))})
                else:
                    result = _text({"error": f"unknown tool: {name}"})
            elif method == "notifications/initialized":
                continue
            else:
                result = {"error": {"code": -32601, "message": "method not found"}}
            print(json.dumps({"jsonrpc": "2.0", "id": request.get("id"), "result": result}), flush=True)
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": str(exc)}}), flush=True)


if __name__ == "__main__":
    main()
