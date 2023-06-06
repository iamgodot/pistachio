import pytest

from pistachio import create_app
from pistachio.adapters.orm import metadata
from pistachio.extensions import engine
from pistachio.services.session_manager import DEFAULT_SESSION_FACTORY


@pytest.fixture(scope="session")
def app():
    _app = create_app()
    yield _app
    metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def session_factory(app):
    return DEFAULT_SESSION_FACTORY


@pytest.fixture
def session(session_factory):
    connection = engine.connect()
    trans = connection.begin()
    session = session_factory(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    trans.rollback()
    connection.close()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
