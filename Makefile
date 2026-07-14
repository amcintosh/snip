.PHONY: install-dev
.PHONY: test, check-style, test-all

help: ## Show this help message
	@echo "Dotfiles v2 - Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install-dev: ## Install with dev dependencies using poetry
	poetry install --with dev

check-style: ## Run lint checks
	poetry run flake8 snip --count --show-source --statistics
	poetry run flake8 tests --count --show-source --statistics

test: ## Run unit tests with coverage
	poetry run pytest --cov=snip --cov-report=term-missing tests

test-all: test check-style ## Run lint checks and tests
