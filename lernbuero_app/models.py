from flask_sqlalchemy import SQLAlchemy

from . import db


class Lernbuero(db.Model):
    __tablename__ = "lernbueros"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    start = db.Column(db.Integer())
    capacity = db.Column(db.Integer())
    participant_count = db.Column(db.Integer())
    end = db.Column(db.Integer())
    kw = db.Column(db.Integer())


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    level = db.Column(db.String(10))
