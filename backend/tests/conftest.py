import logging

import pytest

from pistachio import create_app
from pistachio.extensions import db as _db

# @pytest.fixture(scope="session", autouse=True)
# def setup_logging():
#     root_logger = logging.getLogger("")
#     root_logger.setLevel(logging.DEBUG)
#     stream_handler = logging.StreamHandler()
#     stream_handler.setLevel(logging.DEBUG)
#     root_logger.addHandler(stream_handler)
#
#     yield
#
#     root_logger.removeHandler(stream_handler)


@pytest.fixture(scope="session")
def app():
    _app = create_app(testing=True)
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
