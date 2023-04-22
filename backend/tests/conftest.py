import pytest


@pytest.fixture()
def app():
    from os import environ

    environ["TEST"] = "1"
    from pistachio.app import app

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
    yield app


@pytest.fixture()
def db(app):
    from pistachio.app import db

    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
