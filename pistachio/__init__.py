from flask import Flask

from pistachio.entrypoints import auth, post
from pistachio.extensions import db


def create_app():
    """Application factory, used to create application.

    When use flask shell, .env&.flaskenv will be autoloaded if dotenv installed.
    """
    from logging.config import dictConfig

    logging_config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in func `%(funcName)s` by logger `%(name)s`: %(message)s",  # NOQA
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

    app = Flask("pistachio")

    from os import getenv

    from pistachio import settings

    if not (settings_cls := getenv("PISTACHIO_SETTINGS")):
        print("Env `PISTACHIO_SETTINGS` is not set, exit now.")
        from sys import exit

        exit(1)
    else:
        print(f"Using {settings_cls} from PISTACHIO_SETTINGS.")
        if settings_cls != "ProdSettings":
            logging_config["loggers"]["pistachio"]["level"] = "DEBUG"
        dictConfig(logging_config)
        app.config.from_object(getattr(settings, settings_cls)())

    configure_extensions(app)
    configure_blueprints(app)
    configure_cli()

    return app


def configure_extensions(app):
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
