from datetime import datetime
from socket import gethostname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from lernbuero_app import create_app
from lernbuero_app.models import Lernbuero, User

db = SQLAlchemy()


def main():
    app = create_app()
    db.init_app(app)
    l1 = Lernbuero(name="first", start=datetime(2020, 3, 1, 12).timestamp(),
                   end=datetime(2020, 3, 1, 12, 45).timestamp(), kw=1, capacity=30, participant_count=20)
    l2 = Lernbuero(name="first", start=datetime(2020, 3, 1, 12, 45).timestamp(),
                   end=datetime(2020, 3, 1, 13, 30).timestamp(), kw=1, capacity=30, participant_count=10)
    l3 = Lernbuero(name="first", start=datetime(2020, 3, 1, 12, 45).timestamp(),
                   end=datetime(2020, 3, 1, 13, 30).timestamp(), kw=2, capacity=30, participant_count=00)
    sus1 = User(email="sus1@schule.ch", password="sus1", level="feeder")
    sus2 = User(email="sus2@schule.ch", password="sus2", level="feeder")
    sus3 = User(email="sus3@schule.ch", password="sus3", level="feeder")
    lehrer1 = User(email="l1@schule.ch", password="l1", level="carry")
    lehrer2 = User(email="l2@schule.ch", password="l2", level="carry")
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(l1)
        db.session.add(l2)
        db.session.add(l3)
        db.session.add(sus1)
        db.session.add(sus2)
        db.session.add(sus3)
        db.session.add(lehrer1)
        db.session.add(lehrer2)
        db.session.commit()


if __name__ == '__main__':
    main()
