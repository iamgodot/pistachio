from typing import Any

from pydantic import Field, MySQLDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    SECRET_KEY: str = Field(
        default="pistachio", validation_alias="PISTACHIO_SECRET_KEY"
    )

    MYSQL_USERNAME: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = ""
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = ""

    SQLALCHEMY_DATABASE_URI: str = ""
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @model_validator(mode="before")
    @classmethod
    def build_db_uri(cls, data: Any) -> Any:
        db_uri = MySQLDsn.build(
            scheme="mysql+mysqldb",
            username=data.get("MYSQL_USERNAME", "root"),
            password=data.get("MYSQL_PASSWORD", "root"),
            host=data.get("MYSQL_HOST", "localhost"),
            port=int(data.get("MYSQL_PORT", 3306)),
            path=f'{data.get("MYSQL_DB", "pistachio")}',
        )
        data["SQLALCHEMY_DATABASE_URI"] = str(db_uri)
        return data

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

    if settings_cls == "TestSettings":
        return globals()[settings_cls](MYSQL_DB="pistachio_test")
    return globals()[settings_cls]()


settings = init_settings()
