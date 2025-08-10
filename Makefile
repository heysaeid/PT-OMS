# Variables
PYTHON := poetry run
POETRY := poetry
PRE_COMMIT := poetry run pre-commit
PROJECT_NAME := order-repository-service
PYTHON_FILES := $(PROJECT_NAME) src

# Colors for terminal output
BLUE := \033[1;34m
GREEN := \033[1;32m
RED := \033[1;31m
YELLOW := \033[1;33m
NC := \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo 'Usage:'
	@echo "${BLUE}make${NC} ${GREEN}<target>${NC}"
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z\-_0-9]+:.*?## / {printf "  ${BLUE}%-20s${NC} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: setup
setup: ## Setup project pre-requisites
	@echo "${BLUE}Setup project pre-requisites...${NC}"
	@echo "${GREEN}Installing poetry (may need your sudo password)...${NC}"
	sudo apt install pipx
	pipx install poetry
	pipx ensurepath
	poetry completions bash >> ~/.bash_completion

.PHONY: install
install: ## Install project dependencies
	@echo "${BLUE}Installing project dependencies...${NC}"
	$(POETRY) install
	$(PRE_COMMIT) install

.PHONY: install-dev
install-dev: ## Install project dependencies
	@echo "${BLUE}Installing project dependencies...${NC}"
	$(POETRY) install --with dev --all-extras
	$(PRE_COMMIT) install

.PHONY: update
update: ## Update dependencies to their latest versions
	@echo "${BLUE}Updating dependencies...${NC}"
	$(POETRY) update

.PHONY: clean
clean: ## Remove build artifacts and cache directories
	@echo "${BLUE}Cleaning project...${NC}"
	rm -rf dist/
	rm -rf build/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: format
format: ## Format code using black
	@echo "${BLUE}Formatting code...${NC}"
	$(PYTHON) black --config pyproject.toml $(PYTHON_FILES)

.PHONY: lint
lint: ## Run all linters
	@echo "${BLUE}Running linters...${NC}"
	$(PYTHON) ruff check --config pyproject.toml  $(PYTHON_FILES)
	$(PYTHON) mypy --config-file pyproject.toml $(PYTHON_FILES)

.PHONY: behave
behave: ## Run tests with behave
	@echo "${BLUE}Running tests...${NC}"
	$(PYTHON) behave

.PHONY: build
build: clean ## Build project distribution
	@echo "${BLUE}Building project distribution...${NC}"
	$(POETRY) build

.PHONY: version
version: ## Display current version
	@echo "${BLUE}Current version:${NC}"
	@$(POETRY) version
	@echo "${YELLOW}Current tag(Fetching...):${NC}"
	@git fetch && git describe --tags  --abbrev=0

.PHONY: bump-patch
bump-patch: ## Bump patch version
	@echo "${BLUE}Bumping patch version...${NC}"
	@if [ -n "$(message)" ]; then \
		$(PYTHON) python scripts/bump_version.py patch -m "$(message)"; \
	else \
		$(PYTHON) python scripts/bump_version.py patch -m "$$(git log -1 --pretty=%s)"; \
	fi

.PHONY: bump-minor
bump-minor: ## Bump minor version
	@echo "${BLUE}Bumping minor version...${NC}"
	@if [ -n "$(message)" ]; then \
		$(PYTHON) python scripts/bump_version.py minor -m "$(message)"; \
	else \
		$(PYTHON) python scripts/bump_version.py minor -m "$$(git log -1 --pretty=%s)"; \
	fi

.PHONY: bump-major
bump-major: ## Bump major version
	@echo "${BLUE}Bumping major version...${NC}"
	@if [ -n "$(message)" ]; then \
		$(PYTHON) python scripts/bump_version.py major -m "$(message)"; \
	else \
		$(PYTHON) python scripts/bump_version.py major -m "$$(git log -1 --pretty=%s)"; \
	fi

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "${BLUE}Building Docker image...${NC}"
	docker build -t $(PROJECT_NAME) .

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "${BLUE}Running Docker container...${NC}"
	docker run -it --rm $(PROJECT_NAME)

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	@echo "${BLUE}Running pre-commit hooks...${NC}"
	$(PRE_COMMIT) run --all-files

.PHONY: check
check: lint test ## Run all checks (linting and tests)

.PHONY: update-es-mapping
update-es-mapping:
	@echo "Updating Elasticsearch 'orders' index mapping..."
	@PYTHONPATH=. python scripts/elasticsearch/mapping_manager.py

.PHONY: register-schemas
register-schemas:
	@echo "Registering Avro schemas with Schema Registry..."
	@PYTHONPATH=. python scripts/schema_registry/register_schemas.py

.PHONY: deploy-connector-es-orders
deploy-connector-es-orders:
	@echo "Deploying Elasticsearch sink connector for orders..."
	@./scripts/connectors/manage_connectors.sh deploy connectors/config/elasticsearch-sink-orders.json

.PHONY: status-connector-es-orders
status-connector-es-orders:
	@echo "Checking status of Elasticsearch sink connector for orders..."
	@./scripts/connectors/manage_connectors.sh status connectors/config/elasticsearch-sink-orders.json

.PHONY: manage-es-indices
manage-es-indices:
	@echo "Managing Elasticsearch indices..."
	@PYTHONPATH=. python scripts/elasticsearch/manage_es_indices.py setup
	@PYTHONPATH=. python scripts/elasticsearch/manage_es_indices.py ensure
	@PYTHONPATH=. python scripts/elasticsearch/manage_es_indices.py rollover

.PHONY: ci
ci: ## Run CI pipeline locally
	@echo "${BLUE}Running CI pipeline...${NC}"
	$(MAKE) clean
	$(MAKE) install
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) build

.DEFAULT_GOAL := help