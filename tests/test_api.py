import pytest

BASE_URL = "/v1"


@pytest.fixture
def register(db, client):
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


@pytest.fixture
def access_token(client, register):
    resp = client.post(
        BASE_URL + "/login", json={"username": "foo", "password": "secret"}
    )
    return resp.json["access_token"]


def test_login(client, register):
    resp = client.post(BASE_URL + "/login")
    assert resp.status_code == 400
    resp = client.post(
        BASE_URL + "/login", json={"username": "foo", "password": "secret"}
    )
    assert resp.status_code == 200
    assert resp.json["access_token"]


@pytest.mark.usefixtures("db")
def test_login_by_github(client, mocker):
    mocker.patch("pistachio.entrypoints.auth.get_gh_access_token")
    mocker.patch(
        "pistachio.entrypoints.auth.get_gh_user_info", return_value={"login": "foo"}
    )
    resp = client.post(
        BASE_URL + "/login", json={"type": "github", "github_code": "foo"}
    )
    assert resp.status_code == 200
    assert resp.json["access_token"]


def test_get_current_user(client, access_token):
    resp = client.get(
        BASE_URL + "/user", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp.status_code == 200
    assert resp.json["name"] == "foo"


def test_user(client, register):
    user_id = register

    resp = client.get(BASE_URL + f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json["name"] == "foo"
    resp = client.patch(BASE_URL + f"/users/{user_id}", json={"name": "bar"})
    assert resp.status_code == 200
    assert resp.json["name"] == "bar"


def test_post(client, register, access_token):
    from io import BytesIO

    from werkzeug.datastructures import FileStorage

    user_id = register
    resp = client.post(
        BASE_URL + "/posts",
        data={
            "user_id": user_id,
            "file": FileStorage(BytesIO(b"Hello world"), filename="test_file"),
            "description": "file for test",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 200
    assert resp.json["filename"] == "test_file"

    post_id = resp.json["id"]
    resp = client.get(BASE_URL + f"/posts/{post_id}")
    assert resp.json["id"] == post_id

    resp = client.delete(BASE_URL + f"/posts/{post_id}")
    assert resp.status_code == 204
    assert (
        client.get(
            BASE_URL + "/posts",
            headers={"Authorization": f"Bearer {access_token}"},
        ).json
        == []
    )
