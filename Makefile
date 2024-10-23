# Install project dependencies using Poetry
install:
	poetry install

# Install pre-commit hooks
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

# Run pre-commit on all files (for linting and formatting)
lint:
	poetry run pre-commit run --all-files

# For future use
# migrations:
# migrate:
# update: install migrate install-pre-commit

# Default target: Run the FastAPI app with Uvicorn
run:
	poetry run uvicorn app.main:app --reload
