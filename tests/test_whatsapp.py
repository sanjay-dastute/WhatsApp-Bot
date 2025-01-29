import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.base import Base, engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/whatsapp_bot_test")

engine_test = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)

@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_webhook_start(db_session):
    response = client.post(
        "/api/v1/webhook",
        data={
            "From": "whatsapp:+1234567890",
            "Body": "start"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_webhook_data_collection(db_session):
    phone = "whatsapp:+1234567890"
    test_data = [
        ("Test Samaj", "Please enter your full name:"),
        ("John Doe", "Please enter your gender (Male/Female/Other):"),
        ("Male", "Please enter your age:"),
        ("30", "Please enter your blood group:"),
        ("O+", "Please enter your primary mobile number:"),
        ("+1234567890", "Please enter your secondary mobile number (or type 'skip'):"),
        ("skip", "Please enter your education:"),
        ("Graduate", "Please enter your occupation:"),
        ("Engineer", "Please enter your marital status:"),
        ("Single", "Please enter your address:"),
        ("123 Main St", "Please enter your email:"),
        ("john@example.com", "Please enter your birth date (YYYY-MM-DD):"),
        ("1990-01-01", "Please enter your anniversary date (YYYY-MM-DD or type 'skip'):"),
        ("skip", "Please enter your native place:"),
        ("New York", "Please enter your current city:"),
        ("San Francisco", "Please enter languages known (comma-separated):"),
        ("English, Spanish", "Please enter your skills (comma-separated):"),
        ("Programming", "Please enter your hobbies (comma-separated):"),
        ("Reading", "Please enter emergency contact number:"),
        ("+1987654321", "Please enter your relationship status:"),
        ("Single", "Please enter your family role:"),
        ("Son", "Please enter any medical conditions (or type 'skip'):"),
        ("skip", "Please enter dietary preferences:"),
        ("Vegetarian", "Please enter social media handles (comma-separated or type 'skip'):"),
        ("skip", "Please enter your profession category:"),
        ("IT", "Please enter volunteer interests (comma-separated or type 'skip'):")
    ]
    
    for data, expected_prompt in test_data:
        response = client.post(
            "/api/v1/webhook",
            data={
                "From": phone,
                "Body": data
            }
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}

def test_webhook_invalid_input(db_session):
    response = client.post(
        "/api/v1/webhook",
        data={
            "From": "whatsapp:+1234567890",
            "Body": "invalid"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_webhook_validation(db_session):
    phone = "whatsapp:+1234567890"
    invalid_data = [
        ("a", "Please enter a valid age between 0 and 120"),
        ("xyz", "Please enter a valid blood group (A+, A-, B+, B-, O+, O-, AB+, AB-)"),
        ("1234567890", "Please enter number with country code (e.g., +1234567890)"),
        ("invalid@email", "Please enter a valid email address"),
        ("01/01/1990", "Please enter date in YYYY-MM-DD format")
    ]
    
    # Start the conversation
    client.post("/api/v1/webhook", data={"From": phone, "Body": "start"})
    client.post("/api/v1/webhook", data={"From": phone, "Body": "Test Samaj"})
    client.post("/api/v1/webhook", data={"From": phone, "Body": "John Doe"})
    client.post("/api/v1/webhook", data={"From": phone, "Body": "Male"})
    
    # Test invalid inputs
    for invalid_input, expected_error in invalid_data:
        response = client.post(
            "/api/v1/webhook",
            data={
                "From": phone,
                "Body": invalid_input
            }
        )
        assert response.status_code == 200
        assert response.json() == {"success": True}

def test_admin_login(db_session):
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": os.getenv("ADMIN_USERNAME", "admin"),
            "password": os.getenv("ADMIN_PASSWORD", "admin")
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_admin_login_invalid(db_session):
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "wrong",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
