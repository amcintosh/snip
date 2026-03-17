.PHONY: install-dev, tag, clean
.PHONY: test, check-style

ifeq ($(BRANCH_NAME),)
BRANCH_NAME="$$(git rev-parse --abbrev-ref HEAD)"
endif

install-dev:
	poetry install

check-style:
	flake8 snip --count --show-source --statistics
	flake8 tests --count --show-source --statistics

test:
	pytest --cov=snip --cov-report=term-missing tests

test-all: test check-style
