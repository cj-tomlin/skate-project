# Install project dependencies using Poetry
install:
	poetry install

# Install pre-commit hooks
install-pre-commit:
	poetry run pre-commit install

# Run pre-commit on all files (for linting and formatting)
lint:
	poetry run pre-commit run --all-files

# Spin up PostgreSQL and Redis in Docker
start-db:
	docker-compose up -d postgres redis

# Stop PostgreSQL and Redis in Docker
stop-db:
	docker-compose down

# Create a new Alembic migration
# Usage: make migrations msg="Your migration message here"
migrations:
	poetry run alembic revision --autogenerate -m "$(msg)"

# Apply migrations to the database
migrate:
	poetry run alembic upgrade head

# Run all migrations in one command (create and apply)
# Usage: make migrate-all msg="Your migration message here"
migrate-all:
	make migrations msg="$(msg)" && make migrate

# Reset database (drops all data)
reset-db:
	make stop-db && docker-compose rm -f postgres redis && make start-db && make migrate

# Run tests with coverage
test:
	pytest --cov=app --log-cli-level=INFO tests/

# Run coverage tests and print output to file for easy ChatGPT diagnosis
test-print:
	pytest --cov=app tests/ | tee pytest_output.txt

# Run the FastAPI app with Uvicorn
run:
	poetry run uvicorn app.main:app --reload

# Run only unit tests
test-unit:
	pytest --cov=app --log-cli-level=INFO tests/unit/

# Run only integration tests
test-integration:
	pytest --cov=app --log-cli-level=INFO tests/integration/

# Run tests for a specific domain
# Usage: make test-domain domain=users
test-domain:
	pytest --cov=app.domain.$(domain) --log-cli-level=INFO tests/unit/domain/$(domain)/ tests/integration/api/test_$(domain)_*.py

# Generate OpenAPI documentation to a file
generate-openapi:
	poetry run python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json

# Export OpenAPI documentation to HTML using Swagger UI
export-docs:
	poetry run python -c "from app.main import app; import json; from pathlib import Path; Path('docs').mkdir(exist_ok=True); Path('docs/openapi.json').write_text(json.dumps(app.openapi(), indent=2))" && \
	echo '<!DOCTYPE html><html><head><title>API Documentation</title><meta charset="utf-8"/><link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css"/></head><body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script><script>const ui = SwaggerUIBundle({url: "openapi.json", dom_id: "#swagger-ui"})</script></body></html>' > docs/index.html

# Create a new domain structure
# Usage: make new-domain name=events
new-domain:
	mkdir -p app/domain/$(name)/api app/domain/$(name)/models app/domain/$(name)/repositories app/domain/$(name)/schemas app/domain/$(name)/services
	touch app/domain/$(name)/__init__.py app/domain/$(name)/api/__init__.py app/domain/$(name)/models/__init__.py app/domain/$(name)/repositories/__init__.py app/domain/$(name)/schemas/__init__.py app/domain/$(name)/services/__init__.py
	mkdir -p tests/unit/domain/$(name) tests/integration/api
	touch tests/unit/domain/$(name)/__init__.py
	@echo "Created domain structure for $(name)"

# Run the application in different environments
run-dev:
	ENV=development poetry run uvicorn app.main:app --reload

run-test:
	ENV=testing poetry run uvicorn app.main:app --reload

run-prod:
	ENV=production poetry run uvicorn app.main:app --workers 4

# Setup a new development environment from scratch
setup-dev: install install-pre-commit start-db migrate

# Clean up Python cache files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

.PHONY: install install-pre-commit lint start-db stop-db migrations migrate migrate-all reset-db test test-print run test-unit test-integration test-domain generate-openapi export-docs new-domain run-dev run-test run-prod setup-dev clean
