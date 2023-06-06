from sqlalchemy import create_engine

from pistachio.settings import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
