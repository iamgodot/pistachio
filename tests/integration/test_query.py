from sqlalchemy import text

from pistachio.adapters.query import Query
from pistachio.models import User


def create_user(session, name):
    session.execute(
        text(
            'INSERT INTO user (username, password_hash, nickname, email, avatar, bio, created_at) VALUES (:name, "", :name, "", "", "", "2000-01-01")'  # noqa
        ),
        [{"name": name}],
    )
    session.commit()


def test_create_user(session):
    user = User(
        nickname="foo",
        password="",
        email="",
    )
    Query(session).add(user)
    session.commit()
    assert session.execute(text("SELECT nickname FROM user")).all() == [
        ("foo",),
    ]


def test_user_follow(session):
    create_user(session, "foo")
    create_user(session, "bar")
    create_user(session, "bat")
    query = Query(session)

    foo = query.first(User)
    bar = query.get(User, nickname="bar")
    bat = query.get(User, nickname="bat")
    assert query.list(User) == [foo, bar, bat]
    foo.followers.append(bar)
    assert bar.followings == [foo]
    bat.followings.append(foo)
    assert foo.followers == [bar, bat]


# def test_user_with_posts(session):
#     user = create_user(session, "test")
#     post1 = Post(user=user, attachment=Attachment(name="foo", size=1, url=""))
#     post2 = Post(user=user, attachment=Attachment(name="bar", size=2, url=""))
#     posts = [post1, post2]
#     query = Query(session)
#     query.update(User, {"posts": posts}, username="test")
#     assert user.posts == posts
#     query.delete(user)
#     assert query.list(Post) == posts
