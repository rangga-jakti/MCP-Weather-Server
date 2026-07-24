.PHONY: install test lint run docker-build docker-run clean

install:
	pip install -e ".[dev]"

test:
	pytest

test-v:
	pytest -v

lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

run:
	python -m weather.server

docker-build:
	docker build --target runtime -t mcp-weather-server .

docker-run:
	docker compose up

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	rm -f .coverage coverage.xml
