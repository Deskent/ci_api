import asyncio
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def get_app() -> FastAPI:
    return app


@pytest.fixture(scope='session')
def get_test_client_app(get_app) -> TestClient:
    client = TestClient(app=get_app)
    with client as session:
        yield session


@pytest.fixture(scope='session')
def base_url() -> str:
    return "/api/v1"
