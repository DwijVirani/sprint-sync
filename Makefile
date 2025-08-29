# Variables
PYTHON := python
UV := uv
APP_MODULE := app.main:app
HOST := 0.0.0.0
PORT := 8000

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BLUE)SprintSync Makefile$(NC)"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

db-setup: ## Setup database (run migrations)
	@echo "$(BLUE)Setting up database...$(NC)"
	$(UV) run alembic upgrade head

db-migrate: ## Create new database migration
	@echo "$(BLUE)Creating new migration...$(NC)"
	@read -p "Enter migration message: " msg; \
	$(UV) run alembic revision --autogenerate -m "$$msg"

db-migrate-empty: ## Create empty migration file
	@echo "$(BLUE)Creating empty migration...$(NC)"
	@read -p "Enter migration message: " msg; \
	$(UV) run alembic revision -m "$$msg"

db-upgrade: ## Upgrade database to latest migration (alias for db-setup)
	@echo "$(BLUE)Upgrading database to latest...$(NC)"
	$(UV) run alembic upgrade head

db-upgrade-to: ## Upgrade database to specific revision
	@echo "$(BLUE)Upgrading database to specific revision...$(NC)"
	@read -p "Enter revision (e.g., +1, revision_id): " rev; \
	$(UV) run alembic upgrade "$$rev"

db-downgrade: ## Downgrade database by one migration
	@echo "$(BLUE)Downgrading database by one...$(NC)"
	$(UV) run alembic downgrade -1

db-downgrade-to: ## Downgrade database to specific revision
	@echo "$(BLUE)Downgrading database to specific revision...$(NC)"
	@read -p "Enter revision (e.g., -1, revision_id, base): " rev; \
	$(UV) run alembic downgrade "$$rev"

db-downgrade-base: ## Downgrade database to base (remove all migrations)
	@echo "$(RED)Downgrading database to base (removing all migrations)...$(NC)"
	@echo "$(YELLOW)Warning: This will remove all data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		$(UV) run alembic downgrade base; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

db-reset: ## Reset database (downgrade all and upgrade) - WARNING: destroys data
	@echo "$(RED)Resetting database...$(NC)"
	@echo "$(YELLOW)Warning: This will destroy all data and recreate the database!$(NC)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		$(UV) run alembic downgrade base; \
		$(UV) run alembic upgrade head; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Operation cancelled.$(NC)"; \
	fi

db-status: ## Show current database migration status
	@echo "$(BLUE)Checking database migration status...$(NC)"
	$(UV) run alembic current

db-history: ## Show migration history
	@echo "$(BLUE)Showing migration history...$(NC)"
	$(UV) run alembic history --verbose

db-show: ## Show specific migration details
	@echo "$(BLUE)Showing migration details...$(NC)"
	@read -p "Enter revision (or 'current' for current): " rev; \
	$(UV) run alembic show "$$rev"

docker-up: ## Start services with Docker Compose
	@echo "$(BLUE)Starting services with Docker Compose...$(NC)"
	docker compose up -d


dev: ## Run the application in development mode
	$(UV) run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload