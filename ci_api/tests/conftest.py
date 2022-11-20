import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope='session')
def get_app():
    return app


@pytest.fixture(scope='session')
def get_test_app(get_app):
    client = TestClient(app=get_app)
    with client as session:
        yield session


@pytest.fixture(scope='session')
def base_url():
    return "/api/v1"
