from flask import Flask

from pistachio.entrypoints import auth, post
from pistachio.extensions import db


def create_app(testing=False):
    """Application factory, used to create application.

    When use flask shell, .env&.flaskenv will be autoloaded if dotenv installed.
    """
    from logging.config import dictConfig

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "loggers": {
                "pistachio": {
                    "level": "WARNING",
                    "handlers": ["default"],
                    "propagate": False,
                },
            },
        }
    )
    app = Flask("pistachio")

    from pistachio import settings

    if testing:
        app.config.from_object(settings.TestSettings())
    else:
        app.config.from_object(settings.Settings())

    configure_extensions(app, testing)
    configure_blueprints(app)
    configure_cli()

    return app


def configure_extensions(app, testing=False):
    db.init_app(app)
    with app.app_context():
        db.create_all()


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
