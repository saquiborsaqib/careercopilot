from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get('/api/health')
    assert response.status_code == 200


def test_protected_me_requires_token():
    response = client.get('/api/auth/me')
    assert response.status_code == 401
