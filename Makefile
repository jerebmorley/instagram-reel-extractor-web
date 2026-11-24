.PHONY: install lint test

install:
	uv sync --locked

lint:
	uv run --locked ruff check src tests scripts
	uv run --locked ruff format --check src tests scripts

test: lint
	uv run --locked pytest
