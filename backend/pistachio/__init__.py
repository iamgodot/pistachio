from flask import Flask

from pistachio.entrypoints import auth, post
from pistachio.extensions import db


def create_app(testing=False, env_file=None):
    """Application factory, used to create application.

    When use flask shell, .env&.flaskenv will be autoloaded if dotenv installed.

    In general, `env_file` will be manually set and loaded into config, of which
    the file name can also be defined by env `APP_ENV_FILE`, otherwise .env will
    be used by default.
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
                    "level": "DEBUG",
                }
            },
            "pistachio": {"level": "DEBUG", "handlers": ["default"], "propagate": True},
        }
    )
    app = Flask("pistachio")

    from pistachio import config

    if testing:
        app.config.from_object(config.TestConfig)
    else:
        app.config.from_object(config.Config)

    from os import getenv

    env_file = env_file or getenv("APP_ENV") or ".env"
    if env_file:
        from dotenv import dotenv_values, load_dotenv

        load_dotenv(env_file)
        app.config.from_mapping(dotenv_values(env_file))

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
