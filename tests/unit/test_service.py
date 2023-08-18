import pytest

from pistachio.adapters.query import QueryBase
from pistachio.models import User
from pistachio.services.auth import (
    InvalidCredential,
    UsernameTaken,
    UserNotFound,
    login_user,
    register_user,
)
from pistachio.services.session_manager import SessionManagerBase


class FakeQuery(QueryBase):
    def __init__(self) -> None:
        self.items = []

    def add(self, obj):
        self.items.append(obj)

    def first(self, model, **filters):
        for item in self.items:
            for k, v in filters.items():
                if getattr(item, k, None) != v:
                    break
            else:
                return item

    def get(self, model, **filters):
        res = None
        for item in self.items:
            for k, v in filters.items():
                if getattr(item, k, None) != v:
                    break
            else:
                if res is not None:
                    raise ValueError("Multiple items get")
                res = item

    def list(self, model, **filters):
        res = []
        for item in self.items:
            for k, v in filters.items():
                if getattr(item, k, None) != v:
                    break
            else:
                res.append(item)
        return res

    def update(self, _, params: dict, **filters):
        for item in self.items:
            for k, v in filters.items():
                if getattr(item, k, None) != v:
                    break
            else:
                for k, v in params.items():
                    setattr(item, k, v)

    def delete(self, model, **filters):
        for item in self.items:
            for k, v in filters.items():
                if getattr(item, k, None) != v:
                    break
            else:
                self.items.remove(item)


class FakeSessionManager(SessionManagerBase):
    def __init__(self) -> None:
        self.committed = False
        self.query = FakeQuery()

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        pass


@pytest.fixture
def sm():
    return FakeSessionManager()


@pytest.fixture
def create_user(sm):
    with sm:
        sm.query.add(User(username="foo", email="", nickname="", password="testpass"))
        sm.commit()


def test_register_normal(sm):
    assert sm.committed is False
    user_dict = register_user("foo", "", "", sm)
    assert sm.committed is True
    assert user_dict["username"] == "foo"


@pytest.mark.usefixtures("create_user")
def test_register_fail(sm):
    with pytest.raises(UsernameTaken):
        register_user("foo", "", "", sm)


@pytest.mark.usefixtures("create_user")
def test_login_normal(sm):
    user_dict = login_user("foo", "testpass", sm)
    assert user_dict["username"] == "foo"


@pytest.mark.usefixtures("create_user")
def test_login_user_not_found(sm):
    with pytest.raises(UserNotFound):
        login_user("bar", "testpass", sm)


@pytest.mark.usefixtures("create_user")
def test_login_with_wrong_password(sm):
    with pytest.raises(InvalidCredential):
        login_user("foo", "anotherpass", sm)


def test_login_user_via_github():
    ...  # TODO
