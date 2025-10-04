.PHONY: help install install-dev test lint format type-check clean setup run-scrape run-clean run-analysis run-web

help: ## Show this help message
	@echo "Etsy Product Analysis & Recommendation System"
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .

setup: ## Initialize project structure
	python days/day01_setup.py

test: ## Run tests
	pytest tests/ -v

lint: ## Run linting
	ruff check src/ days/ tests/

format: ## Format code
	ruff format src/ days/ tests/

type-check: ## Run type checking
	mypy src/ days/ tests/

clean: ## Clean up generated files
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

run-scrape: ## Run sample scraping
	python days/day02_scrape_sample.py --category_url "https://www.etsy.com/search?q=poster" --delay 2.0

run-clean: ## Run data cleaning
	python days/day04_clean_data.py --input data/raw/day02_sample.csv

run-analysis: ## Run data analysis
	python days/day05_analysis.py --input data/processed/day04_clean.csv

run-web: ## Start web interface
	python days/day14_flask_app.py

all: install-dev setup test lint type-check ## Run all checks and setup
