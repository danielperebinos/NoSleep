# --- Makefile for NoSleep ---
# Usage: make [target]

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# --- Project ---
PROJECT  := NoSleep
SRC_DIR  := src
TEST_DIR := tests

# --- Git ---
VERSION    ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo "dev")
COMMIT     ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_TIME := $(shell date -u '+%Y-%m-%dT%H:%M:%SZ')

# ============================================================================
.DEFAULT_GOAL := help

##@ Development

.PHONY: install
install: ## Install all dependencies (including dev)
	uv sync

.PHONY: run
run: ## Run the application from source
	uv run python $(SRC_DIR)/main.py

##@ Testing

.PHONY: test
test: ## Run tests
	uv run pytest $(TEST_DIR)/ -v --tb=short

.PHONY: test-cover
test-cover: ## Run tests with coverage report
	uv run pytest $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing
	@echo "Coverage report: htmlcov/index.html"

##@ Code Quality

.PHONY: lint
lint: ## Run ruff linter
	uv run ruff check .

.PHONY: lint-fix
lint-fix: ## Run ruff linter with auto-fix
	uv run ruff check --fix .

.PHONY: fmt
fmt: ## Format code with ruff
	uv run ruff format .

.PHONY: fmt-check
fmt-check: ## Check code formatting (no changes)
	uv run ruff format --check .

.PHONY: check
check: lint fmt-check test ## Run all quality checks

##@ Build

.PHONY: build
build: ## Build standalone EXE with PyInstaller
	uv run pyinstaller --onefile --noconsole --icon=$(SRC_DIR)/icon.ico --add-data "$(SRC_DIR)/icon.ico;." --name $(PROJECT) $(SRC_DIR)/main.py
	@echo "Built: dist/$(PROJECT).exe ($(shell stat -c%s dist/$(PROJECT).exe 2>/dev/null || echo '?') bytes)"

.PHONY: installer
installer: build ## Build Windows installer with Inno Setup (requires Inno Setup 6)
	"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
	@echo "Installer built: $(PROJECT)Installer.exe"

##@ CI

.PHONY: ci
ci: install lint fmt-check test ## Run full CI pipeline locally

##@ Cleanup

.PHONY: clean
clean: ## Remove build artifacts and caches
	rm -rf dist/ build/ *.spec .pytest_cache .ruff_cache htmlcov/ coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

##@ Help

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make \033[36m<target>\033[0m\n"} \
		/^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2} \
		/^##@/ {printf "\n\033[1m%s\033[0m\n", substr($$0, 5)}' $(MAKEFILE_LIST)
