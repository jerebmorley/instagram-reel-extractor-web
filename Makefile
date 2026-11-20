.PHONY: install lint test

install:
	uv sync --locked

lint:
	uv run --locked ruff check src tests
	uv run --locked ruff format --check src tests

test: lint
	uv run --locked pytest
