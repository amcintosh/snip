.PHONY: install-dev
.PHONY: test, check-style, test-all

install-dev:
	poetry install --with dev

check-style:
	poetry run flake8 snip --count --show-source --statistics
	poetry run flake8 tests --count --show-source --statistics

test:
	poetry run pytest --cov=snip --cov-report=term-missing tests

test-all: test check-style
