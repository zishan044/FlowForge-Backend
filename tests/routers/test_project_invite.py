import pytest

@pytest.mark.asyncio
async def test_send_invite_success(client, auth_headers):
    p_res = await client.post("/projects/", json={"name": "Invite Lab"}, headers=auth_headers)
    project_id = p_res.json()["id"]

    user_b_res = await client.post("/auth/signup", json={"email": "user_b@test.com", "password": "password"})
    user_b_id = user_b_res.json()["id"]

    response = await client.post(
        f"/projects/{project_id}/invites",
        json={"invited_user_id": user_b_id},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pending"

@pytest.mark.asyncio
async def test_accept_invite_creates_member(client, auth_headers):

    p_res = await client.post("/projects/", json={"name": "Join Me"}, headers=auth_headers)
    project_id = p_res.json()["id"]
    
    email_b = "user_b_accept@test.com"
    u_b = await client.post("/auth/signup", json={"email": email_b, "password": "password"})
    user_b_id = u_b.json()["id"]
    
    login_res = await client.post("/auth/login", json={"email": email_b, "password": "password"})
    token_b = login_res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    invite_res = await client.post(
        f"/projects/{project_id}/invites",
        json={"invited_user_id": user_b_id},
        headers=auth_headers
    )
    invite_id = invite_res.json()["id"]

    response = await client.patch(
        f"/projects/invites/{invite_id}",
        json={"status": "accepted"},
        headers=headers_b
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

    members_res = await client.get(f"/projects/{project_id}/members", headers=headers_b)
    member_ids = [m["user_id"] for m in members_res.json()]
    assert user_b_id in member_ids