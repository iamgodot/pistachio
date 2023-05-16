from datetime import datetime

from pistachio.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    nickname = db.Column(db.String(30), nullable=False, default="")
    password_hash = db.Column(db.String(16), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
