# Makefile for IndiVillage Voice Agent System

# Variables
PYTHON := python
PIP := pip
VENV := venv
VENV_BIN := $(VENV)/bin
VENV_PYTHON := $(VENV_BIN)/python
VENV_PIP := $(VENV_BIN)/pip
PROJECT_NAME := indivillage-voice-agent
DOCKER_IMAGE := voice-agent-system
DOCKER_TAG := latest

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)IndiVillage Voice Agent System - Makefile Commands$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Examples:$(RESET)"
	@echo "  make setup          # Set up development environment"
	@echo "  make run            # Run the application"
	@echo "  make test           # Run all tests"
	@echo "  make docker-build   # Build Docker image"

# Environment setup
.PHONY: setup
setup: ## Set up development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip setuptools wheel
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PIP) install -r requirements-dev.txt
	@echo "$(GREEN)Development environment setup complete!$(RESET)"
	@echo "$(YELLOW)Activate with: source $(VENV_BIN)/activate$(RESET)"

.PHONY: setup-pre-commit
setup-pre-commit: ## Set up pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(RESET)"
	$(VENV_BIN)/pre-commit install
	$(VENV_BIN)/pre-commit install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed!$(RESET)"

.PHONY: install
install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed!$(RESET)"

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)Development dependencies installed!$(RESET)"

# Application commands
.PHONY: run
run: ## Run the application
	@echo "$(BLUE)Starting IndiVillage Voice Agent System...$(RESET)"
	$(PYTHON) client.py

.PHONY: run-dev
run-dev: ## Run the application in development mode
	@echo "$(BLUE)Starting application in development mode...$(RESET)"
	FLASK_ENV=development FLASK_DEBUG=1 $(PYTHON) client.py

.PHONY: run-prod
run-prod: ## Run the application in production mode
	@echo "$(BLUE)Starting application in production mode...$(RESET)"
	gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 client:app

# Testing
.PHONY: test
test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(RESET)"
	$(PYTHON) -m pytest tests/ -v

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(PYTHON) -m pytest tests/unit/ -v

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(PYTHON) -m pytest tests/integration/ -v

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest tests/ --cov=common --cov=knowledgebase --cov-report=html --cov-report=term-missing

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	$(PYTHON) -m pytest tests/ -f

# Code quality
.PHONY: lint
lint: ## Run all linting tools
	@echo "$(BLUE)Running linting tools...$(RESET)"
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .
	$(PYTHON) -m flake8 .
	$(PYTHON) -m pylint common/ knowledgebase/
	$(PYTHON) -m mypy common/ knowledgebase/ --ignore-missing-imports

.PHONY: format
format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(PYTHON) -m black .
	$(PYTHON) -m isort .
	@echo "$(GREEN)Code formatted!$(RESET)"

.PHONY: format-check
format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .

.PHONY: security
security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	$(PYTHON) -m bandit -r . -x tests/
	$(PYTHON) -m safety check

.PHONY: type-check
type-check: ## Run type checking
	@echo "$(BLUE)Running type checking...$(RESET)"
	$(PYTHON) -m mypy common/ knowledgebase/ --ignore-missing-imports

# Documentation
.PHONY: docs
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	@if [ -d "docs/_build" ]; then rm -rf docs/_build; fi
	sphinx-build -b html docs/ docs/_build/html
	@echo "$(GREEN)Documentation generated in docs/_build/html/$(RESET)"

.PHONY: docs-serve
docs-serve: docs ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(RESET)"
	cd docs/_build/html && $(PYTHON) -m http.server 8000

# Docker commands
.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(RESET)"

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -d --name voice-agent -p 5000:5000 \
		-e DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY} \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	@echo "$(GREEN)Container started at http://localhost:5000$(RESET)"

.PHONY: docker-stop
docker-stop: ## Stop Docker container
	@echo "$(BLUE)Stopping Docker container...$(RESET)"
	docker stop voice-agent || true
	docker rm voice-agent || true
	@echo "$(GREEN)Container stopped$(RESET)"

.PHONY: docker-logs
docker-logs: ## Show Docker container logs
	@echo "$(BLUE)Showing container logs...$(RESET)"
	docker logs -f voice-agent

.PHONY: docker-shell
docker-shell: ## Open shell in Docker container
	@echo "$(BLUE)Opening shell in container...$(RESET)"
	docker exec -it voice-agent /bin/bash

.PHONY: docker-compose-up
docker-compose-up: ## Start services with docker-compose
	@echo "$(BLUE)Starting services with docker-compose...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)Services started$(RESET)"

.PHONY: docker-compose-down
docker-compose-down: ## Stop services with docker-compose
	@echo "$(BLUE)Stopping services with docker-compose...$(RESET)"
	docker-compose down
	@echo "$(GREEN)Services stopped$(RESET)"

# Database and data management
.PHONY: generate-mock-data
generate-mock-data: ## Generate fresh mock data
	@echo "$(BLUE)Generating mock data...$(RESET)"
	$(PYTHON) -c "from common.business_logic import generate_mock_data; generate_mock_data()"
	@echo "$(GREEN)Mock data generated!$(RESET)"

.PHONY: validate-data
validate-data: ## Validate data integrity
	@echo "$(BLUE)Validating data integrity...$(RESET)"
	$(PYTHON) -c "from common.business_logic import validate_data_integrity; print('✅ Data valid' if validate_data_integrity() else '❌ Data invalid')"

.PHONY: backup-data
backup-data: ## Backup application data
	@echo "$(BLUE)Backing up application data...$(RESET)"
	@mkdir -p backups
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	cp -r mock_data_outputs backups/mock_data_$$DATE; \
	cp -r knowledgebase/mdx backups/knowledge_base_$$DATE; \
	echo "$(GREEN)Data backed up to backups/ directory$(RESET)"

# Knowledge base management
.PHONY: validate-knowledge-base
validate-knowledge-base: ## Validate knowledge base entries
	@echo "$(BLUE)Validating knowledge base...$(RESET)"
	$(PYTHON) -c "from knowledgebase.mdx_handler import MDXKnowledgeBase; kb = MDXKnowledgeBase(); entries = kb.read_knowledge_base(); print(f'✅ Knowledge base valid: {len(entries)} entries')"

.PHONY: search-knowledge-base
search-knowledge-base: ## Search knowledge base (usage: make search-knowledge-base QUERY="your query")
	@echo "$(BLUE)Searching knowledge base for: $(QUERY)$(RESET)"
	$(PYTHON) -c "from knowledgebase.mdx_handler import MDXKnowledgeBase; kb = MDXKnowledgeBase(); results = kb.search_knowledge_base('$(QUERY)'); print(f'Found {len(results)} results'); [print(f'- {r.get(\"title\", \"Untitled\")}') for r in results[:5]]"

# Maintenance and cleanup
.PHONY: clean
clean: ## Clean up temporary files and caches
	@echo "$(BLUE)Cleaning up temporary files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	@echo "$(GREEN)Cleanup complete!$(RESET)"

.PHONY: clean-all
clean-all: clean ## Clean everything including virtual environment
	@echo "$(BLUE)Cleaning everything...$(RESET)"
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "$(GREEN)Deep cleanup complete!$(RESET)"

.PHONY: reset
reset: clean-all setup ## Reset environment (clean + setup)
	@echo "$(GREEN)Environment reset complete!$(RESET)"

# Development utilities
.PHONY: check
check: format-check lint type-check security test ## Run all checks (format, lint, type, security, test)
	@echo "$(GREEN)All checks passed!$(RESET)"

.PHONY: fix
fix: format ## Fix common issues (formatting)
	@echo "$(GREEN)Common issues fixed!$(RESET)"

.PHONY: requirements
requirements: ## Update requirements files
	@echo "$(BLUE)Updating requirements...$(RESET)"
	$(VENV_PIP) freeze > requirements.txt
	@echo "$(GREEN)Requirements updated!$(RESET)"

.PHONY: upgrade
upgrade: ## Upgrade all dependencies
	@echo "$(BLUE)Upgrading dependencies...$(RESET)"
	$(VENV_PIP) install --upgrade pip setuptools wheel
	$(VENV_PIP) install --upgrade -r requirements.txt
	$(VENV_PIP) install --upgrade -r requirements-dev.txt
	@echo "$(GREEN)Dependencies upgraded!$(RESET)"

# Release management
.PHONY: version
version: ## Show current version
	@echo "$(BLUE)Current version:$(RESET)"
	@$(PYTHON) -c "import sys; print(f'Python: {sys.version}'); from client import __version__; print(f'App: {__version__}')" 2>/dev/null || echo "Version info not available"

.PHONY: changelog
changelog: ## Generate changelog
	@echo "$(BLUE)Generating changelog...$(RESET)"
	@echo "$(YELLOW)Manual changelog update required in CHANGELOG.md$(RESET)"

# Performance and monitoring
.PHONY: profile
profile: ## Run performance profiling
	@echo "$(BLUE)Running performance profiling...$(RESET)"
	$(PYTHON) -m cProfile -o profile.stats client.py &
	@echo "$(YELLOW)Profiling started. Stop with Ctrl+C and analyze with 'python -m pstats profile.stats'$(RESET)"

.PHONY: benchmark
benchmark: ## Run benchmarks
	@echo "$(BLUE)Running benchmarks...$(RESET)"
	$(PYTHON) -m pytest tests/ -k "benchmark" -v

# CI/CD helpers
.PHONY: ci-setup
ci-setup: ## Set up CI environment
	@echo "$(BLUE)Setting up CI environment...$(RESET)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

.PHONY: ci-test
ci-test: ## Run tests for CI
	@echo "$(BLUE)Running CI tests...$(RESET)"
	$(PYTHON) -m pytest tests/ --cov=common --cov=knowledgebase --cov-report=xml --cov-report=term-missing

.PHONY: ci-lint
ci-lint: ## Run linting for CI
	@echo "$(BLUE)Running CI linting...$(RESET)"
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .
	$(PYTHON) -m flake8 .

# Platform-specific commands
.PHONY: install-audio-linux
install-audio-linux: ## Install audio dependencies on Linux
	@echo "$(BLUE)Installing audio dependencies for Linux...$(RESET)"
	sudo apt-get update
	sudo apt-get install -y portaudio19-dev python3-pyaudio
	@echo "$(GREEN)Audio dependencies installed!$(RESET)"

.PHONY: install-audio-macos
install-audio-macos: ## Install audio dependencies on macOS
	@echo "$(BLUE)Installing audio dependencies for macOS...$(RESET)"
	brew install portaudio
	@echo "$(GREEN)Audio dependencies installed!$(RESET)"

# Monitoring and health checks
.PHONY: health-check
health-check: ## Check application health
	@echo "$(BLUE)Checking application health...$(RESET)"
	@curl -f http://localhost:5000/health 2>/dev/null && echo "$(GREEN)✅ Application is healthy$(RESET)" || echo "$(RED)❌ Application is not responding$(RESET)"

.PHONY: logs
logs: ## Show application logs
	@echo "$(BLUE)Showing application logs...$(RESET)"
	@if [ -f "voice_agent.log" ]; then tail -f voice_agent.log; else echo "$(YELLOW)No log file found$(RESET)"; fi

# Quick commands
.PHONY: dev
dev: setup run-dev ## Quick development setup and run

.PHONY: prod
prod: install run-prod ## Quick production setup and run

.PHONY: all
all: setup check test docker-build ## Run complete build pipeline

# Information commands
.PHONY: info
info: ## Show project information
	@echo "$(CYAN)IndiVillage Voice Agent System$(RESET)"
	@echo "$(YELLOW)Project Information:$(RESET)"
	@echo "  Name: $(PROJECT_NAME)"
	@echo "  Docker Image: $(DOCKER_IMAGE):$(DOCKER_TAG)"
	@echo "  Python: $(shell $(PYTHON) --version 2>&1)"
	@echo "  Pip: $(shell $(PIP) --version 2>&1)"
	@echo "  Virtual Environment: $(VENV)"
	@echo ""
	@echo "$(YELLOW)Key Files:$(RESET)"
	@echo "  Main Application: client.py"
	@echo "  Requirements: requirements.txt, requirements-dev.txt"
	@echo "  Configuration: .env (create from .env.example)"
	@echo "  Docker: Dockerfile, docker-compose.yml"
	@echo ""
	@echo "$(YELLOW)Useful Commands:$(RESET)"
	@echo "  make setup      # Set up development environment"
	@echo "  make run        # Run the application"
	@echo "  make test       # Run tests"
	@echo "  make check      # Run all quality checks"
	@echo "  make help       # Show all available commands"

# Phony targets (targets that don't create files)
.PHONY: all setup setup-pre-commit install install-dev run run-dev run-prod
.PHONY: test test-unit test-integration test-coverage test-watch
.PHONY: lint format format-check security type-check
.PHONY: docs docs-serve
.PHONY: docker-build docker-run docker-stop docker-logs docker-shell
.PHONY: docker-compose-up docker-compose-down
.PHONY: generate-mock-data validate-data backup-data
.PHONY: validate-knowledge-base search-knowledge-base
.PHONY: clean clean-all reset check fix requirements upgrade
.PHONY: version changelog profile benchmark
.PHONY: ci-setup ci-test ci-lint
.PHONY: install-audio-linux install-audio-macos
.PHONY: health-check logs dev prod info help