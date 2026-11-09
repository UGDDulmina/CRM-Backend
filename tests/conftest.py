import os
from pathlib import Path

import pytest

from dotenv import load_dotenv
from fastapi.testclient import TestClient

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

from app.models.customer import Customer
from app.models.company import Company
from app.models.lead import Lead
from app.models.activity import Activity
from app.models.task import Task
from app.models.users import User

from app.models.users import UserRole

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    PROJECT_ROOT / ".env.test",
    override=True
)

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not configured"
    )

database_name = make_url(TEST_DATABASE_URL).database

if database_name != "crm_test_db":
    raise RuntimeError(
        "Tests must use crm_test_db"
    )

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False
)

@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    with test_engine.connect() as connection:
        actual_database = connection.scalar(
            text("SELECT current_database()")
        )

    if actual_database != "crm_test_db":
        raise RuntimeError(
            "Connected to an unexpected databse"
        )

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(prepare_test_database):
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def clean_test_tables(prepare_test_database):
    with test_engine.begin() as connection:
        for table in reversed(
            Base.metadata.sorted_tables
        ):
            connection.execute(table.delete())


@pytest.fixture
def salesperson_headers(client):

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Sales Test User",
            "email": "sales@example.com",
            "password": "StrongPassword123!"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "sales@example.com",
            "password": "StrongPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def admin_headers(client, db_session):

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Admin Test User",
            "email": "admin@example.com",
            "password": "StrongPassword123!"
        }
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    user = db_session.get(User, user_id)

    user.role = UserRole.ADMIN

    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "StrongPassword123!"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }