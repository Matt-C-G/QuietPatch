# QuietPatch Development Makefile

.PHONY: help notes test clean install

help: ## Show this help message
	@echo "QuietPatch Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

notes: ## Generate release notes for a tag (usage: make notes TAG=v0.2.6)
	@if [ -z "$(TAG)" ]; then \
		echo "Usage: make notes TAG=v0.2.6"; \
		exit 1; \
	fi
	@echo "Generating release notes for $(TAG)..."
	@bash tools/generate_release_notes.sh "$(TAG)" "https://github.com/Matt-C-G/QuietPatch"
	@echo "Opening NOTES.md..."
	@if command -v open >/dev/null 2>&1; then \
		open NOTES.md; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open NOTES.md; \
	else \
		echo "Generated NOTES.md - open it manually"; \
	fi

test: ## Run all tests
	@echo "Running tests..."
	@python -m pytest -v

test-release-notes: ## Test release notes generator
	@echo "Testing release notes generator..."
	@bash tools/test_release_notes.sh

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .coverage
	@rm -f NOTES.md
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

install: ## Install in development mode
	@echo "Installing QuietPatch in development mode..."
	@python -m pip install -e ".[test]"

lint: ## Run linting
	@echo "Running ruff linter..."
	@python -m ruff check . --fix
	@echo "Running ruff formatter..."
	@python -m ruff format .

build: ## Build wheel and PEX locally
	@echo "Building wheel..."
	@python -m build -w -n
	@echo "Building PEX..."
	@python -m pip install pex
	@mkdir -p dist-pex
	@whl=$$(ls dist/*.whl | head -1); \
	python -m pex $$whl -c quietpatch --find-links dist --no-build --strip-pex-env --venv prepend -o dist-pex/quietpatch-local.pex
	@echo "Built: dist-pex/quietpatch-local.pex"

smoke: build ## Run smoke test on local PEX
	@echo "Running smoke test..."
	@python3.11 dist-pex/quietpatch-local.pex scan --help >/dev/null
	@echo "✅ Smoke test passed"

# Development workflow
dev: clean install test lint ## Full development setup
	@echo "✅ Development environment ready"

# Release preparation
pre-release: clean test lint build smoke ## Prepare for release
	@echo "✅ Ready for release tagging"
