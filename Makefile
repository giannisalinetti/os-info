# Makefile for OpenStack Info Tool

.PHONY: help install install-dev install-editable test test-verbose test-coverage lint format clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development and testing dependencies"
	@echo "  install-editable - Install in development mode"
	@echo "  test          - Run tests"
	@echo "  test-verbose  - Run tests with verbose output"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint          - Run code linting"
	@echo "  format        - Format code with black and isort"
	@echo "  clean         - Clean up generated files"

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
