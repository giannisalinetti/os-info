# Makefile for OpenStack Info Tool

# Container image configuration
IMAGE_NAME ?= os-info
IMAGE_TAG ?= latest
IMAGE_FULL = $(IMAGE_NAME):$(IMAGE_TAG)
REGISTRY ?= 

# Container runtime detection
CONTAINER_RUNTIME ?= $(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker)

.PHONY: help install install-dev install-editable test test-verbose test-coverage lint format clean \
	run run-interactive run-env help-script \
	container-build container-build-docker container-build-podman container-build-multiarch \
	container-run container-run-docker container-run-podman container-shell \
	container-run-env container-run-config container-run-interactive \
	container-push container-clean container-prune container-save container-load container-info \
	compose-build compose-up compose-up-bg compose-down compose-logs compose-run compose-clean

# Default target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Development:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development and testing dependencies"
	@echo "  install-editable - Install in development mode"
	@echo "  test          - Run tests"
	@echo "  test-verbose  - Run tests with verbose output"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint          - Run code linting"
	@echo "  format        - Format code with black and isort"
	@echo "  clean         - Clean up generated files"
	@echo ""
	@echo "Container Management:"
	@echo "  container-build           - Build container image (auto-detect runtime)"
	@echo "  container-build-docker    - Build container image with Docker"
	@echo "  container-build-podman    - Build container image with Podman"
	@echo "  container-build-multiarch - Build multi-architecture image"
	@echo "  container-run             - Run container (show help)"
	@echo "  container-run-env         - Run container with environment credentials"
	@echo "  container-run-config      - Run container with config file"
	@echo "  container-run-interactive - Run container in interactive mode"
	@echo "  container-shell           - Open shell in container"
	@echo "  container-push            - Push image to registry"
	@echo "  container-clean           - Remove local container image"
	@echo "  container-prune           - Clean up unused container resources"
	@echo "  container-save            - Save image to tar file"
	@echo "  container-load            - Load image from tar file"
	@echo "  container-info            - Show container image information"
	@echo ""
	@echo "Docker Compose:"
	@echo "  compose-build  - Build services with docker-compose"
	@echo "  compose-up     - Start services with docker-compose"
	@echo "  compose-up-bg  - Start services in background"
	@echo "  compose-down   - Stop services with docker-compose"
	@echo "  compose-logs   - View docker-compose logs"
	@echo "  compose-run    - Run one-off container with docker-compose"
	@echo "  compose-clean  - Clean up docker-compose resources"
	@echo ""
	@echo "Runtime Configuration:"
	@echo "  Current container runtime: $(CONTAINER_RUNTIME)"
	@echo "  Image name: $(IMAGE_FULL)"
	@echo "  Registry: $(if $(REGISTRY),$(REGISTRY),<not set>)"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development and testing dependencies
install-dev:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

# Install in development mode
install-editable:
	pip install -e .

# Run tests
test:
	python -m pytest

# Run tests with verbose output
test-verbose:
	python -m pytest -v

# Run tests with coverage
test-coverage:
	python -m pytest --cov=os_info --cov-report=term-missing --cov-report=html

# Run specific test classes
test-auth:
	python -m pytest -k "TestAuthentication" -v

test-config:
	python -m pytest -k "TestConfiguration" -v

test-export:
	python -m pytest -k "TestDataProcessing" -v

# Run linting
lint:
	flake8 os_info.py test_os_info.py
	black --check os_info.py test_os_info.py
	isort --check-only os_info.py test_os_info.py

# Format code
format:
	black os_info.py test_os_info.py
	isort os_info.py test_os_info.py

# Clean up generated files
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .vscode/
	rm -rf .idea/
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	rm -rf .tox/
	rm -rf .mypy_cache/
	rm -f coverage.xml
	rm -f *.csv
	rm -f *.log
	rm -f *.tmp
	rm -f *.temp
	rm -f *.bak
	rm -f *.backup
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	find . -name "*.swp" -delete
	find . -name "*.swo" -delete
	find . -name ".DS_Store" -delete
	find . -name "*.ps" -delete
	find . -name "*.eps" -delete
	find . -name "*.ps3" -delete
	find . -name "*.eps3" -delete

# Run the main script (requires OpenStack credentials)
run:
	python os_info.py

# Run with specific authentication method
run-interactive:
	python os_info.py --auth-method interactive

run-env:
	python os_info.py --auth-method env

# Show help for the main script
help-script:
	python os_info.py --help

# =============================================================================
# Container Management Targets
# =============================================================================

# Build container image (auto-detect runtime)
container-build:
	@echo "Building container image with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_RUNTIME) build -t $(IMAGE_FULL) .
	@echo "Successfully built $(IMAGE_FULL)"

# Build container image with Docker
container-build-docker:
	@echo "Building container image with Docker..."
	docker build -t $(IMAGE_FULL) .
	@echo "Successfully built $(IMAGE_FULL)"

# Build container image with Podman
container-build-podman:
	@echo "Building container image with Podman..."
	podman build -t $(IMAGE_FULL) .
	@echo "Successfully built $(IMAGE_FULL)"

# Run container interactively (show help by default)
container-run:
	@echo "Running container with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_RUNTIME) run --rm $(IMAGE_FULL)

# Run container with Docker (specific runtime)
container-run-docker:
	@echo "Running container with Docker..."
	docker run --rm $(IMAGE_FULL)

# Run container with Podman (specific runtime)
container-run-podman:
	@echo "Running container with Podman..."
	podman run --rm $(IMAGE_FULL)

# Open shell in container for debugging
container-shell:
	@echo "Opening shell in container with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_RUNTIME) run --rm -it --entrypoint /bin/sh $(IMAGE_FULL)

# Run container with OpenStack credentials from environment
container-run-env:
	@echo "Running container with environment credentials..."
	$(CONTAINER_RUNTIME) run --rm \
		-e OS_AUTH_URL \
		-e OS_USERNAME \
		-e OS_PASSWORD \
		-e OS_PROJECT_NAME \
		-e OS_USER_DOMAIN_NAME \
		-e OS_PROJECT_DOMAIN_NAME \
		-e OS_REGION_NAME \
		-e OS_INTERFACE \
		-v $(PWD)/reports:/app/reports \
		$(IMAGE_FULL) $(ARGS)

# Run container with configuration file
container-run-config:
	@echo "Running container with configuration file..."
	@mkdir -p reports config
	$(CONTAINER_RUNTIME) run --rm \
		-v $(PWD)/config:/app/config:ro \
		-v $(PWD)/reports:/app/reports \
		$(IMAGE_FULL) --auth-method config --config-file /app/config/openstack.conf $(ARGS)

# Run container interactively for credential input
container-run-interactive:
	@echo "Running container in interactive mode..."
	@mkdir -p reports
	$(CONTAINER_RUNTIME) run --rm -it \
		-v $(PWD)/reports:/app/reports \
		$(IMAGE_FULL) --auth-method interactive $(ARGS)

# Push image to registry
container-push:
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Error: REGISTRY variable not set. Use 'make container-push REGISTRY=your-registry.com'"; \
		exit 1; \
	fi
	@echo "Tagging image for registry $(REGISTRY)..."
	$(CONTAINER_RUNTIME) tag $(IMAGE_FULL) $(REGISTRY)/$(IMAGE_FULL)
	@echo "Pushing $(REGISTRY)/$(IMAGE_FULL)..."
	$(CONTAINER_RUNTIME) push $(REGISTRY)/$(IMAGE_FULL)

# Remove local container image
container-clean:
	@echo "Removing local container image $(IMAGE_FULL)..."
	-$(CONTAINER_RUNTIME) rmi $(IMAGE_FULL)
	@if [ "$(REGISTRY)" ]; then \
		echo "Removing registry-tagged image $(REGISTRY)/$(IMAGE_FULL)..."; \
		$(CONTAINER_RUNTIME) rmi $(REGISTRY)/$(IMAGE_FULL) 2>/dev/null || true; \
	fi

# Clean up unused container resources
container-prune:
	@echo "Cleaning up unused container resources with $(CONTAINER_RUNTIME)..."
	$(CONTAINER_RUNTIME) system prune -f
	@if [ "$(CONTAINER_RUNTIME)" = "docker" ]; then \
		echo "Cleaning up unused Docker volumes..."; \
		docker volume prune -f; \
	fi

# =============================================================================
# Docker Compose Targets
# =============================================================================

# Build services with docker-compose
compose-build:
	@echo "Building services with docker-compose..."
	docker-compose build

# Start services with docker-compose
compose-up:
	@echo "Starting services with docker-compose..."
	docker-compose up

# Start services in background
compose-up-bg:
	@echo "Starting services in background with docker-compose..."
	docker-compose up -d

# Stop services with docker-compose
compose-down:
	@echo "Stopping services with docker-compose..."
	docker-compose down

# View docker-compose logs
compose-logs:
	@echo "Viewing docker-compose logs..."
	docker-compose logs -f

# Run one-off container with docker-compose
compose-run:
	@echo "Running one-off container with docker-compose..."
	@mkdir -p reports
	docker-compose run --rm openstack-info $(ARGS)

# Clean up docker-compose resources
compose-clean:
	@echo "Cleaning up docker-compose resources..."
	docker-compose down --volumes --remove-orphans
	docker-compose rm -f

# =============================================================================
# Advanced Container Targets
# =============================================================================

# Build multi-architecture image (requires buildx)
container-build-multiarch:
	@echo "Building multi-architecture image..."
	docker buildx build --platform linux/amd64,linux/arm64 -t $(IMAGE_FULL) .

# Save container image to tar file
container-save:
	@echo "Saving container image to $(IMAGE_NAME)-$(IMAGE_TAG).tar..."
	$(CONTAINER_RUNTIME) save $(IMAGE_FULL) > $(IMAGE_NAME)-$(IMAGE_TAG).tar
	@echo "Image saved to $(IMAGE_NAME)-$(IMAGE_TAG).tar"

# Load container image from tar file
container-load:
	@if [ ! -f "$(IMAGE_NAME)-$(IMAGE_TAG).tar" ]; then \
		echo "Error: $(IMAGE_NAME)-$(IMAGE_TAG).tar not found"; \
		exit 1; \
	fi
	@echo "Loading container image from $(IMAGE_NAME)-$(IMAGE_TAG).tar..."
	$(CONTAINER_RUNTIME) load < $(IMAGE_NAME)-$(IMAGE_TAG).tar

# Show container image information
container-info:
	@echo "Container image information:"
	@echo "  Image: $(IMAGE_FULL)"
	@echo "  Registry: $(if $(REGISTRY),$(REGISTRY),<not set>)"
	@echo "  Runtime: $(CONTAINER_RUNTIME)"
	@echo ""
	@if $(CONTAINER_RUNTIME) inspect $(IMAGE_FULL) >/dev/null 2>&1; then \
		echo "Image exists locally:"; \
		$(CONTAINER_RUNTIME) inspect $(IMAGE_FULL) --format '  Created: {{.Created}}'; \
		$(CONTAINER_RUNTIME) inspect $(IMAGE_FULL) --format '  Size: {{.Size}} bytes'; \
	else \
		echo "Image does not exist locally. Run 'make container-build' to create it."; \
	fi
