import pytest


@pytest.mark.asyncio
async def test_create(user_create, get_test_app, base_url):
    response = get_test_app.post(base_url + "/auth/register", json=user_create)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_me(get_test_app, user_payload, base_url, get_bearer):
    response = get_test_app.get(base_url + "/users/me", headers=get_bearer)
    assert response.status_code == 200
    assert response.json().get("id") is not None


@pytest.mark.asyncio
async def test_delete(get_test_app, user_payload, base_url, get_bearer):
    response = get_test_app.delete(base_url + "/users", headers=get_bearer, allow_redirects=True)
    assert response.status_code == 204
