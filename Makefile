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
	pytest --cov=app tests/

# Run coverage tests and print output to file for easy ChatGPT diagnosis
test-print:
	pytest --cov=app tests/ | tee pytest_output.txt

# Run the FastAPI app with Uvicorn
run:
	poetry run uvicorn app.main:app --reload
