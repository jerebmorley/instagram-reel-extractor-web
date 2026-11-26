.PHONY: install lint test

install:
	uv sync --locked

lint:
	uv run --locked ruff check src tests scripts app
	uv run --locked ruff format --check src tests scripts app

test: lint
	uv run --locked pytest

.PHONY: ui
ui:
	uv run --locked streamlit run app/campana.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
