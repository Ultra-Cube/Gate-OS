---
applyTo: "gateos_manager/**/*.py,tests/**/*.py"
description: "Python implementation and test conventions for Gate-OS"
---

Use Python 3.12-compatible typing and explicit return types. Preserve async boundaries and public APIs. Validate external data at boundaries with Pydantic or JSON Schema. Keep subprocesses timeout-bounded and check return codes. Do not log secrets or raw untrusted payloads. Add focused tests for success, failure, rollback, authentication, and permission boundaries. Run pytest and Ruff for touched code.
