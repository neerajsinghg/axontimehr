import asyncio
from httpx import AsyncClient

def test_health_endpoint(sync_client: AsyncClient) -> None:
    async def _run() -> None:
        response = await sync_client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "message" in data
        assert "version" in data
        assert "environment" in data
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]
        assert "request_id" in data
        assert response.headers.get("X-Request-ID") == data["request_id"]

    asyncio.run(_run())
