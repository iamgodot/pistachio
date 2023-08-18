from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine

from pistachio.settings import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
apifairy = APIFairy()
ma = Marshmallow()
