.PHONY: install test lint format clean run-api run-dashboard docker-api docker-dashboard

install:
	pip install -e ".[dev]"

test:
	pytest tests -v --cov=esg_model

lint:
	ruff check src tests
	mypy src --ignore-missing-imports

format:
	ruff check --fix src tests

clean:
	rm -rf data/ models/ mlruns/ .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-pipeline:
	python -m esg_model.pipeline

run-api:
	uvicorn esg_model.api.main:app --reload

run-dashboard:
	streamlit run src/esg_model/dashboard/app.py

docker-api:
	docker build -f docker/Dockerfile.api -t esg-api .
	docker run -p 8000:8000 esg-api

docker-dashboard:
	docker build -f docker/Dockerfile.dashboard -t esg-dashboard .
	docker run -p 8501:8501 esg-dashboard
