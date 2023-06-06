import pytest

from pistachio.adapters.query import Query
from pistachio.models import User
from pistachio.services.session_manager import session_manager as sm


def test_commit(session):
    with sm:
        user = User(
            username="foo",
            nickname="foo",
            password="",
            email="",
        )
        sm.query.add(user)
        sm.commit()

    query = Query(session)
    users = query.list(User)
    assert len(users) == 1
    user = users[0]
    assert user.username == "foo"

    # NOTE: clean up since sm uses a separate session
    with sm:
        sm.query.delete(User, username="foo")
        sm.commit()


def test_rollback_on_exception(session):
    with pytest.raises(ValueError):
        with sm:
            user = User(
                username="foo",
                nickname="foo",
                password="",
                email="",
            )
            sm.query.add(user)
            raise ValueError
    assert Query(session).list(User) == []
