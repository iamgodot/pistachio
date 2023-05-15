from os import getenv


class Config:
    SECRET_KEY = ""

    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/myapp.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = "development"
    ACCESS_TOKEN_TTL = 60 * 10  # 10 mins
    REFRESH_TOKEN_TTL = 60 * 60 * 24 * 7  # 1 week

    GITHUB_CLIENT_ID = getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = getenv("GITHUB_CLIENT_SECRET", "")
