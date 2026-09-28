import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.config import settings
from backend.database.base import Base
from backend.database.connection import get_db
from backend.database.models.enums import UserRole
from backend.database.models.user import User
from backend.main import app


@pytest.fixture(autouse=True)
def isolated_uploads_dir(tmp_path, monkeypatch):
    """Resume uploads should land in a throwaway temp dir, never the repo's uploads/."""
    monkeypatch.setattr(settings, "uploads_dir", str(tmp_path / "uploads"))


@pytest.fixture()
def db_session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


@pytest.fixture()
def client(db_session_factory):
    def override_get_db():
        db = db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def register_and_login(client):
    def _do(email: str = "student@example.com", password: str = "TestPass123", name: str = "Student One"):
        client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
        login_resp = client.post("/api/auth/login", data={"username": email, "password": password})
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _do


@pytest.fixture()
def auth_headers(register_and_login):
    return register_and_login()


@pytest.fixture()
def admin_headers(client, db_session_factory, register_and_login):
    headers = register_and_login(email="admin@example.com", name="Admin One")
    db = db_session_factory()
    try:
        user = db.query(User).filter(User.email == "admin@example.com").first()
        user.role = UserRole.ADMIN
        db.commit()
    finally:
        db.close()
    return headers
