import pytest

from pistachio import create_app
from pistachio.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    from os import environ

    environ["PISTACHIO_SETTINGS"] = "TestSettings"
    _app = create_app()
    with _app.app_context():
        yield _app


@pytest.fixture(scope="function")
def db(app):
    _db.create_all()
    yield _db
    _db.session.close()
    _db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
