from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    SECRET_KEY: str = Field(
        default="pistachio", validation_alias="PISTACHIO_SECRET_KEY"
    )

    # TODO: dsn builder
    SQLALCHEMY_DATABASE_URI: str = "mysql+mysqldb://root:root@localhost/pistachio"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    JWT_SECRET: str = ""
    ACCESS_TOKEN_TTL: int = 60 * 10  # 10 mins
    REFRESH_TOKEN_TTL: int = 60 * 60 * 24 * 7  # 1 week

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    MAX_CONTENT_LENGTH: int = 16 * 1000 * 1000

    APIFAIRY_TITLE: str = "Pistachio API Documentation"
    APIFAIRY_VERSION: str = ""
    APIFAIRY_UI: str = "redoc"
    APIFAIRY_UI_PATH: str = "/api/docs"

    CHATPDF_API_KEY: str = ""

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION_NAME: str = ""


class TestSettings(Settings):
    TESTING: bool = True


class LocalSettings(Settings):
    DEBUG: bool = True

    JWT_SECRET: str = "development"
    ACCESS_TOKEN_TTL: int = 60 * 60 * 24  # 1 day


class ProdSettings(Settings):
    pass


def init_settings():
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
    from os import getenv

    if not (settings_cls := getenv("PISTACHIO_SETTINGS", "LocalSettings")):
        print("Env `PISTACHIO_SETTINGS` is not set, exit now.")
        from sys import exit

        exit(1)
    print(f"Using {settings_cls} from PISTACHIO_SETTINGS.")
    if settings_cls != "ProdSettings":
        logging_config["loggers"]["pistachio"]["level"] = "DEBUG"
    dictConfig(logging_config)

    return globals()[settings_cls]()


settings = init_settings()
