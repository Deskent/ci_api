import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope='session')
def get_app() -> FastAPI:
    return app


@pytest.fixture(scope='session')
def get_test_session(get_app) -> TestClient:
    client = TestClient(app=get_app)
    with client as session:
        yield session


@pytest.fixture(scope='session')
def base_url() -> str:
    return "/api/v1"
