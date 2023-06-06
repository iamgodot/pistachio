from flask import Flask

from pistachio.adapters.orm import metadata, start_mappers
from pistachio.entrypoints import auth, post
from pistachio.extensions import engine
from pistachio.settings import settings


def create_app():
    """Application factory, used to create application.

    When use flask shell, .env&.flaskenv will be autoloaded if dotenv installed.
    """

    app = Flask("pistachio")

    app.config.from_object(settings)

    configure_extensions(app)
    configure_blueprints(app)
    configure_cli()

    return app


def configure_extensions(app):
    start_mappers()
    metadata.create_all(engine)


def configure_blueprints(app):
    @app.get("/")
    def index():
        return "<html><h2>Welcome to Pistachio</h2></html>"

    app.register_blueprint(auth.bp, url_prefix="/v1")
    app.register_blueprint(post.bp, url_prefix="/v1")


def configure_cli():
    pass  # TODO


__all__ = ("create_app",)
__version__ = "0.1.0"
