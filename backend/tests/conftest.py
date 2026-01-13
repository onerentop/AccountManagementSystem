"""Pytest fixtures for the test suite."""
import os
import pytest
from typing import Generator
from contextlib import asynccontextmanager

# Set test environment before importing app modules
os.environ["TESTING"] = "true"
os.environ["DATABASE_PATH"] = ":memory:"

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI

# Test database setup with shared cache for SQLite in-memory
# Using file:memdb1?mode=memory&cache=shared allows multiple connections
TEST_DATABASE_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Now import app modules
from app.models.database import Base, get_db
from app.models import database as db_module
from app.services.crypto_service import crypto_service
from app.api import auth_router, accounts_router, tags_router
from app.config import settings

# Override the engine and SessionLocal in the database module
db_module.engine = test_engine
db_module.SessionLocal = TestSessionLocal


def create_test_app() -> FastAPI:
    """Create a test application with proper lifespan."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Test startup: tables are created in the db fixture
        yield
        # Test shutdown

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/api")
    app.include_router(accounts_router, prefix="/api")
    app.include_router(tags_router, prefix="/api")

    @app.get("/")
    async def root():
        return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


# Create test app instance
test_app = create_test_app()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Clear crypto key at start of each test
    crypto_service.clear_encryption_key()

    # Create tables
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)
        # Clear crypto key after test
        crypto_service.clear_encryption_key()


@pytest.fixture(scope="function")
def client(db: Session):
    """Create a test client with database dependency override."""
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db
        finally:
            pass

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def initialized_system(client, db: Session):
    """Set up an initialized system with master password."""
    test_password = "TestPassword123!"

    # Setup master password (requires confirm_password)
    response = client.post(
        "/api/auth/setup",
        json={"password": test_password, "confirm_password": test_password}
    )
    assert response.status_code == 201, f"Setup failed: {response.json()}"

    return {"password": test_password}


@pytest.fixture(scope="function")
def auth_token(client, initialized_system):
    """Get authentication token for protected endpoints."""
    password = initialized_system["password"]

    response = client.post(
        "/api/auth/login",
        json={"password": password}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"

    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Get authorization headers for API requests."""
    return {"Authorization": f"Bearer {auth_token}"}
