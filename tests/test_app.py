import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.anyio
async def test_docs():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/docs")
        assert response.status_code == 200
