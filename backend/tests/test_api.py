import pytest

BASE_URL = "/v1"


@pytest.mark.usefixtures("db")
def register(client):
    resp = client.post(
        BASE_URL + "/register",
        json={
            "name": "foo",
            "nickname": "bar",
            "password": "secret",
            "description": "",
        },
    )
    assert resp.status_code == 201
    assert resp.json["name"] == "foo"
    return resp.json["id"]


@pytest.mark.usefixtures("db")
def test_login(client):
    resp = client.post(BASE_URL + "/login")
    assert resp.status_code == 400
    user_id = register(client)
    resp = client.post(
        BASE_URL + "/login", json={"username": "foo", "password": "secret"}
    )
    assert resp.status_code == 200
    assert resp.json["id"] == user_id


@pytest.mark.usefixtures("db")
def test_user(client):
    user_id = register(client)

    resp = client.get(BASE_URL + f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json["name"] == "foo"
    resp = client.patch(BASE_URL + f"/users/{user_id}", json={"name": "bar"})
    assert resp.status_code == 200
    assert resp.json["name"] == "bar"


@pytest.mark.usefixtures("db")
def test_post(client):
    user_id = register(client)
    resp = client.post(
        BASE_URL + "/posts",
        json={
            "user_id": user_id,
            "filename": "test_file",
            "download_url": "http://example.com/test_file",
            "description": "",
        },
    )
    assert resp.status_code == 200
    assert resp.json["filename"] == "test_file"

    post_id = resp.json["id"]
    resp = client.get(BASE_URL + f"/posts/{post_id}")
    assert resp.json["id"] == post_id

    resp = client.delete(BASE_URL + f"/posts/{post_id}")
    assert resp.status_code == 204
    assert client.get(BASE_URL + "/posts").json == []
