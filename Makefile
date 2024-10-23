# Default target: Run the FastAPI app with Uvicorn
run:
	poetry run uvicorn app.main:app --reload