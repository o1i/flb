from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from lernbuero_app import create_app
from lernbuero_app.models import Lernbuero, User, Enrolment

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
    sus1 = User(email="s1", password="s", level="feeder")
    sus2 = User(email="s2", password="s", level="feeder")
    sus3 = User(email="s3", password="s", level="feeder")
    lehrer1 = User(email="l1", password="l", level="carry")
    lehrer2 = User(email="l2", password="l", level="carry")
    with app.app_context():
        db.drop_all()
        db.session.commit()
        db.create_all()
        db.session.add(l1)
        db.session.add(l2)
        db.session.add(l3)
        db.session.add(sus1)
        db.session.add(sus2)
        db.session.add(sus3)
        db.session.add(lehrer1)
        db.session.add(lehrer2)

        e1 = Enrolment()
        e1.enroled_sus_ = sus1
        l1.enroled_sus.append(e1)

        e2 = Enrolment()
        e2.enroled_sus_ = sus2
        l1.enroled_sus.append(e2)

        e3 = Enrolment()
        e3.enroled_sus_ = sus2
        l2.enroled_sus.append(e3)

        e4 = Enrolment()
        e4.enroled_sus_ = sus3
        l1.enroled_sus.append(e4)

        e5 = Enrolment()
        e5.enroled_sus_ = sus3
        l2.enroled_sus.append(e5)

        e6 = Enrolment()
        e6.enroled_sus_ = sus3
        l3.enroled_sus.append(e6)

        db.session.commit()


if __name__ == '__main__':
    main()
