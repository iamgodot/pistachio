from pydantic import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = ""

    SQLALCHEMY_DATABASE_URI: str = "sqlite:////tmp/pistachio.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    JWT_SECRET: str = "development"
    ACCESS_TOKEN_TTL: int = 60 * 10  # 10 mins
    REFRESH_TOKEN_TTL: int = 60 * 60 * 24 * 7  # 1 week

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET = ""

    class Config:
        env_prefix = ""
        env_file = ".env"
        env_file_encoding = "utf-8"
        fields = {
            "GITHUB_CLIENT_ID": {"env": "GITHUB_CLIENT_ID"},
            "GITHUB_CLIENT_SECRET": {"env": "GITHUB_CLIENT_SECRET"},
        }

    MAX_CONTENT_LENGTH: int = 16 * 1000 * 1000


class TestSettings(Settings):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
