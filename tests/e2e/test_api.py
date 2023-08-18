BASE_URL = "/api/v1"


def login(client, credential: dict):
    return client.post(BASE_URL + "/login", json=credential)


def test_user(client, mocker):
    # ---------- Register ----------

    resp = client.post(
        BASE_URL + "/register",
        json={
            "username": "foo",
            "email": "foo@example.com",
            "password": "secret",
        },
    )
    assert resp.status_code == 201
    # TODO: use this user id for later
    user_id = resp.json["id"]
    assert user_id == 1

    # ---------- Login ----------

    resp = login(client, {})
    assert resp.status_code == 400

    resp = login(client, {"email": "foo@example.com", "password": "secret"})
    # NOTE: save token for later
    access_token = resp.json["access_token"]
    assert resp.status_code == 200
    assert "access_token" in resp.json

    # ---------- Login via GitHub ----------

    mocker.patch("pistachio.services.auth.get_gh_access_token")
    mocker.patch(
        "pistachio.services.auth.get_gh_user_info",
        return_value={
            "login": "octocat",
            "email": "octocat@github.com",
            "avatar_url": "https://i.pravatar.cc/150?img=2",
        },
    )
    # NOTE: this is our second user with id=2
    resp = client.post(
        BASE_URL + "/login", json={"type": "github", "github_code": "foo"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json

    # ---------- Get current user ----------

    resp = client.get(
        BASE_URL + "/user", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp.status_code == 200
    assert resp.json["username"] == "foo"

    # ---------- Update current user ----------

    resp = client.patch(
        BASE_URL + "/user",
        json={"nickname": "bar"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 200
    assert resp.json["id"] == 1

    # ---------- Get user ----------

    # FIXME: hardcoded user_id
    resp = client.get(
        BASE_URL + "/users/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert resp.status_code == 200
    assert resp.json["username"] == "foo"

    # ---------- Delete user ----------

    # NOTE: keep this order since we need access
    for uid in 2, 1:
        resp = client.delete(
            BASE_URL + f"/users/{uid}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 204


# def test_post(client, register, access_token):
#     from io import BytesIO
#
#     from werkzeug.datastructures import FileStorage
#
#     user_id = register
#     resp = client.post(
#         BASE_URL + "/posts",
#         data={
#             "user_id": user_id,
#             "file": FileStorage(BytesIO(b"Hello world"), filename="test_file"),
#             "description": "file for test",
#         },
#         headers={"Authorization": f"Bearer {access_token}"},
#     )
#     assert resp.status_code == 200
#     assert resp.json["filename"] == "test_file"
#
#     post_id = resp.json["id"]
#     resp = client.get(BASE_URL + f"/posts/{post_id}")
#     assert resp.json["id"] == post_id
#
#     resp = client.delete(BASE_URL + f"/posts/{post_id}")
#     assert resp.status_code == 204
#     assert (
#         client.get(
#             BASE_URL + "/posts",
#             headers={"Authorization": f"Bearer {access_token}"},
#         ).json
#         == []
#     )
