from logging import getLogger

from flask import Flask
from werkzeug.exceptions import HTTPException

from pistachio.adapters.orm import metadata, start_mappers
from pistachio.entrypoints import auth, post
from pistachio.extensions import apifairy, engine, ma
from pistachio.settings import settings

LOGGER = getLogger(__name__)


def create_app():
    """Application factory, used to create application.

    When use flask shell, .env&.flaskenv will be autoloaded if dotenv installed.
    """

    app = Flask("pistachio")

    app.config.from_object(settings)

    configure_extensions(app)
    configure_blueprints(app)
    configure_error_handlers(app)
    configure_cli()

    return app


def configure_extensions(app):
    start_mappers()
    metadata.create_all(engine)
    apifairy.init_app(app)
    ma.init_app(app)


def configure_blueprints(app):
    @app.get("/")
    def index():
        return "<html><h2>Welcome to Pistachio</h2></html>"

    app.register_blueprint(auth.bp, url_prefix="/api/v1")
    app.register_blueprint(post.bp, url_prefix="/api/v1")


def configure_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return {
                "error": e.name,
                "description": e.description,
            }, e.code
        LOGGER.exception(e)
        return {
            "error": repr(e),
        }, 500


def configure_cli():
    pass  # TODO


__all__ = ("create_app",)
__version__ = "0.1.0"
