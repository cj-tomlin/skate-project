from http import HTTPStatus
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_fastapi_client_open():
    """
    Test that the FastAPI client is open and responding
    """
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Application running"}
