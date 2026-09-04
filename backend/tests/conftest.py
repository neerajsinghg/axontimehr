import asyncio
from typing import Generator
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import init_db

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    asyncio.run(init_db())

@pytest.fixture
def sync_client() -> Generator[AsyncClient, None, None]:
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    asyncio.run(client.aclose())
