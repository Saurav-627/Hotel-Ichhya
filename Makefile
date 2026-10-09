.PHONY: help install sync migrate makemigrations migrations collectstatic seed-all superuser run shell backup test clean docker-up docker-down docker-logs docker-clean setup build-css watch-css

# Default shell
SHELL := /bin/bash

# Detect uv and python path
UV := $(shell which uv 2> /dev/null)
PYTHON := $(if $(UV),uv run python,python)

# Detect npm and npx path
NPM := $(shell which npm 2> /dev/null)
NPX := $(shell which npx 2> /dev/null)

help: ## Show this help message (default)
	@echo "Usage: make [target]"
	@awk ' \
		/^[a-zA-Z_-]+:.*?##/ { \
			helpMessage = match($$0, /## (.*)/); \
			if (helpMessage) { \
				helpLine = substr($$0, RSTART + 3); \
				name = $$1; \
				sub(/:$$/, "", name); \
				printf "  \033[36m%-20s\033[0m %s\n", name, helpLine; \
				} \
		} \
		/^##@/ { \
			printf "\n\033[1m%s\033[0m\n", substr($$0, 5); \
		} \
	' $(MAKEFILE_LIST)

##@ Environment & Dependency Management
sync: ## Install/sync virtual environment and dependencies using uv (or fallback to pip)
	@if [ -n "$(UV)" ]; then \
		echo "Found uv. Syncing dependencies..."; \
		uv sync; \
	else \
		echo "uv not found. Using pip to install requirements..."; \
		pip install -r requirements.txt; \
	fi

install: sync build-css migrate seed-all ## Complete workspace setup (dependencies, CSS build, migrations, and seed all data)
	@echo "Setup completed! Run 'make run' to start the development server."

##@ Development & Run
run: ## Start the local development server (accessible from other devices)
	$(PYTHON) manage.py runserver

shell: ## Open a Django shell with models and database access
	$(PYTHON) manage.py shell

build-css: ## Build minified production Tailwind CSS
	@if [ -n "$(NPM)" ]; then \
		if [ ! -d "node_modules" ]; then \
			echo "Installing frontend npm dependencies..."; \
			npm install; \
		fi; \
		echo "Building production Tailwind CSS bundle..."; \
		npm run build:css; \
	elif [ -n "$(NPX)" ]; then \
		echo "npm not found, but npx found. Compiling Tailwind CSS..."; \
		npx tailwindcss -i static/css/input.css -o static/css/main.bundle.css --minify; \
	else \
		echo "Warning: Neither npm nor npx found. Skipping Tailwind CSS compilation."; \
		echo "Ensure static/css/main.bundle.css is present or install Node.js/npm."; \
	fi

watch-css: ## Watch and compile Tailwind CSS in real time during development
	@if [ -n "$(NPM)" ]; then \
		if [ ! -d "node_modules" ]; then \
			echo "Installing frontend npm dependencies..."; \
			npm install; \
		fi; \
		npm run watch:css; \
	elif [ -n "$(NPX)" ]; then \
		npx tailwindcss -i static/css/input.css -o static/css/main.bundle.css --watch; \
	else \
		echo "Error: npm/npx is required to run Tailwind watch mode."; \
		exit 1; \
	fi

collectstatic: build-css ## Collect static files into staticfiles directory
	$(PYTHON) manage.py collectstatic --noinput --clear

mailpit: ## Run Mailpit local SMTP server (1025) & Web UI (8025) via Docker
	docker run -d --name mailpit --rm -p 8025:8025 -p 1025:1025 axllent/mailpit

##@ Database & Migrations
makemigrations: ## Generate new migrations based on model changes
	$(PYTHON) manage.py makemigrations

migrations: makemigrations ## Alias for makemigrations

migrate: ## Apply database migrations
	$(PYTHON) manage.py migrate

seed-all: ## Import all modular YAML data from core/records/ using seed_data command
	$(PYTHON) manage.py seed_data

superuser: ## Create an administrative superuser (interactive)
	$(PYTHON) manage.py createsuperuser

backup: ## Perform manual database backup and clean old ones (keeps last 10)
	$(PYTHON) manage.py db_backup --keep 10

##@ Docker Management
docker-up: ## Start all project services using Docker Compose in background
	docker compose up -d

docker-down: ## Stop and remove Docker containers
	docker compose down

docker-logs: ## View real-time logs from Docker containers
	docker compose logs -f

docker-clean: ## Stop Docker containers and clean persistent database/cache volumes
	docker compose down -v

##@ Testing & Maintenance
test: ## Run the test suite
	$(PYTHON) manage.py test

clean: ## Clean Python cache files (__pycache__, .pyc, .pyo)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete

setup: install ## Complete one-step workspace setup (alias for install)
