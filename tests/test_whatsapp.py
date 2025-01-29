import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.base import Base, engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/whatsapp_bot_test"

engine_test = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_webhook_start():
    response = client.post(
        "/api/v1/webhook",
        data={
            "From": "whatsapp:+1234567890",
            "Body": "start"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_webhook_invalid_input():
    response = client.post(
        "/api/v1/webhook",
        data={
            "From": "whatsapp:+1234567890",
            "Body": "invalid"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_admin_login():
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "admin",
            "password": "admin"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_admin_login_invalid():
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "wrong",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
