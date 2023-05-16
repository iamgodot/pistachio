from pistachio.models import Post, User


def test_create(db):
    user = User(name="test", nickname="foobar", password_hash="123", description="")
    post = Post(
        filename="test_file",
        download_url="http://example.com/test_file",
        description="",
    )
    user.posts.append(post)
    db.session.add(user)
    db.session.commit()
    assert user.posts[0] is post
