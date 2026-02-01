import pytest

@pytest.mark.asyncio
async def test_create_task_success(client, auth_headers):
    
    p_res = await client.post("/projects/", json={"name": "Task Project"}, headers=auth_headers)
    project_id = p_res.json()["id"]

    task_data = {"title": "Clean Task", "status": "todo"}
    response = await client.post(
        f"/tasks/{project_id}", 
        json=task_data, 
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["project_id"] == project_id

@pytest.mark.asyncio
async def test_get_tasks_success(client, auth_headers):
    
    p_res = await client.post("/projects/", json={"name": "List Project"}, headers=auth_headers)
    project_id = p_res.json()["id"]
    
    await client.post(f"/tasks/{project_id}", json={"title": "T1"}, headers=auth_headers)
    await client.post(f"/tasks/{project_id}", json={"title": "T2"}, headers=auth_headers)

    response = await client.get(f"/tasks/{project_id}", headers=auth_headers)
    
    assert response.status_code == 200
    assert len(response.json()) == 2