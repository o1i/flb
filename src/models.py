from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Lernbuero(db.Model):
    __tablename__ = "lernbueros"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    start = db.Column(db.Integer())
    end = db.Column(db.Integer())
    kw = db.Column(db.Integer())