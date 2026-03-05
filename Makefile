# Gate-OS Makefile
# Usage: make <target>
# Requires: Python 3.10+, virtualenv, Ubuntu 22.04+

PYTHON   := python3
VENV     := .venv
ACTIVATE := source $(VENV)/bin/activate
PIP      := $(VENV)/bin/pip
PYTEST   := $(VENV)/bin/pytest
GATEOS   := $(VENV)/bin/gateos
RUFF     := $(VENV)/bin/ruff

.PHONY: all setup test lint lint-fix validate api clean help

## Default
all: help

## ── Setup ──────────────────────────────────────────────────────────────────
setup: ## Create venv and install all dev dependencies
	@echo "[Gate-OS] Setting up development environment..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo "[Gate-OS] Done! Activate with: source $(VENV)/bin/activate"

## ── Testing ─────────────────────────────────────────────────────────────────
test: ## Run all tests
	$(PYTEST) tests/ -q

test-cov: ## Run tests with coverage report
	$(PYTEST) tests/ --cov=gateos_manager --cov-report=term-missing -q

test-v: ## Run tests (verbose)
	$(PYTEST) tests/ -v

## ── Linting ─────────────────────────────────────────────────────────────────
lint: ## Run ruff linter (check only)
	$(RUFF) check gateos_manager

lint-fix: ## Run ruff linter (auto-fix)
	$(RUFF) check --fix gateos_manager
	$(RUFF) format gateos_manager

## ── Manifest ─────────────────────────────────────────────────────────────────
validate: ## Validate all example environment manifests
	$(GATEOS) validate examples/environments/*.yaml \
		--schema docs/architecture/schemas/environment-manifest.schema.yaml

## ── API ─────────────────────────────────────────────────────────────────────
api: ## Start the Gate-OS Control API locally (port 8088)
	$(GATEOS) api --host 127.0.0.1 --port 8088

token: ## Generate a new API token
	$(GATEOS) gen-token --length 40

## ── Dev check ────────────────────────────────────────────────────────────────
check: lint validate test ## Run full dev-check (lint + validate + tests)

## ── Cleanup ──────────────────────────────────────────────────────────────────
clean: ## Remove venv, caches, build artifacts
	rm -rf $(VENV) __pycache__ .pytest_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

## ── Help ─────────────────────────────────────────────────────────────────────
help: ## Show this help message
	@echo ""
	@echo "  Gate-OS — Available make targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
