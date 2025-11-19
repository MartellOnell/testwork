from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_create_task_endpoint(client):
    with patch('app.services.queue_service.queue_service.publish_task', new_callable=AsyncMock):
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
                "priority": "HIGH"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["priority"] == "HIGH"
        assert data["status"] == "PENDING"
        assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_tasks_endpoint(client):
    with patch('app.services.queue_service.queue_service.publish_task', new_callable=AsyncMock):
        await client.post("/api/v1/tasks", json={"title": "Task 1", "priority": "HIGH"})
        await client.post("/api/v1/tasks", json={"title": "Task 2", "priority": "LOW"})

        response = await client.get("/api/v1/tasks")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["tasks"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_get_task_by_id_endpoint(client):
    with patch('app.services.queue_service.queue_service.publish_task', new_callable=AsyncMock):
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task", "priority": "MEDIUM"}
        )
        task_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"


@pytest.mark.asyncio
async def test_get_nonexistent_task(client):
    response = await client.get("/api/v1/tasks/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_task_endpoint(client):
    with patch('app.services.queue_service.queue_service.publish_task', new_callable=AsyncMock):
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"}
        )
        task_id = create_response.json()["id"]

        response = await client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_get_task_status_endpoint(client):
    with patch('app.services.queue_service.queue_service.publish_task', new_callable=AsyncMock):
        create_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test Task"}
        )
        task_id = create_response.json()["id"]

        response = await client.get(f"/api/v1/tasks/{task_id}/status")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task_id
        assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_get_tasks_with_pagination(client):
    with patch('app.services.queue_service.queue_service.publish_task', new_callable=AsyncMock):
        for i in range(15):
            await client.post("/api/v1/tasks", json={"title": f"Task {i}"})

        response = await client.get("/api/v1/tasks?page=1&page_size=10")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 15
        assert len(data["tasks"]) == 10
        assert data["page"] == 1

        response = await client.get("/api/v1/tasks?page=2&page_size=10")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 15
        assert len(data["tasks"]) == 5
        assert data["page"] == 2


@pytest.mark.asyncio
async def test_get_tasks_with_filters(client):
    with patch('app.services.queue_service.queue_service.publish_task', new_callable=AsyncMock):
        await client.post("/api/v1/tasks", json={"title": "High Priority", "priority": "HIGH"})
        await client.post("/api/v1/tasks", json={"title": "Low Priority", "priority": "LOW"})
        await client.post("/api/v1/tasks", json={"title": "High Priority 2", "priority": "HIGH"})

        response = await client.get("/api/v1/tasks?priority=HIGH")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["tasks"]) == 2
