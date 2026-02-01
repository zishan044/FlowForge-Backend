import pytest

@pytest.mark.asyncio
async def test_create_project_success(client, auth_headers):

    response = await client.post(
        "/projects/",
        json={"name": "Test Project"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    
    assert len(data["members"]) == 1
    assert data["members"][0]["role"] == "owner"

@pytest.mark.asyncio
async def test_get_projects_only_returns_mine(client, auth_headers):
    
    await client.post("/projects/", json={"name": "My Project"}, headers=auth_headers)
    
    response = await client.get("/projects/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.asyncio
async def test_add_member_requires_admin(client, auth_headers):
    
    p_res = await client.post("/projects/", json={"name": "Perms Test"}, headers=auth_headers)
    project_id = p_res.json()["id"]

    other_user_res = await client.post(
        "/auth/signup", 
        json={"email": "other@test.com", "password": "password1"}
    )
    assert other_user_res.status_code == 200, f"Signup failed: {other_user_res.json()}"
    other_user_id = other_user_res.json()["id"]
    
    response = await client.post(
        f"/projects/{project_id}/members",
        json={"user_id": other_user_id, "role": "member"},
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == other_user_id

@pytest.mark.asyncio
async def test_delete_owner_forbidden(client, auth_headers):
    
    p_res = await client.post("/projects/", json={"name": "Protected"}, headers=auth_headers)
    project_id = p_res.json()["id"]
    
    user_id = p_res.json()["members"][0]["user_id"]
    
    response = await client.delete(
        f"/projects/{project_id}/members/{user_id}",
        headers=auth_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot remove project owner"