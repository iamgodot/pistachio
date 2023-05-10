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
    register(client)
    resp = client.post(
        BASE_URL + "/login", json={"username": "foo", "password": "secret"}
    )
    assert resp.status_code == 200
    assert resp.json["access_token"]


@pytest.mark.usefixtures("db")
def test_login_by_github(client, mocker):
    mocker.patch("pistachio.app.get_gh_access_token")
    mocker.patch("pistachio.app.get_gh_user_info", return_value={"login": "foo"})
    resp = client.post(
        BASE_URL + "/login", json={"type": "github", "github_code": "foo"}
    )
    assert resp.status_code == 200
    assert resp.json["access_token"]


@pytest.mark.usefixtures("db")
def test_get_current_user(client):
    register(client)
    resp = client.post(
        BASE_URL + "/login", json={"username": "foo", "password": "secret"}
    )
    access_token = resp.json["access_token"]
    resp = client.get(
        BASE_URL + "/user", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp.status_code == 200
    assert resp.json["name"] == "foo"


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
    from io import BytesIO

    from werkzeug.datastructures import FileStorage

    user_id = register(client)
    resp = client.post(
        BASE_URL + "/posts",
        data={
            "user_id": user_id,
            "file": FileStorage(BytesIO(b"Hello world"), filename="test_file"),
            "description": "file for test",
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
