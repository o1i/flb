from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from lernbuero_app import create_app
from lernbuero_app.models import Lernbuero, User, Enrolment, Gruppe, Block, LbInstance

from lernbuero_app import db


def main():
    app = create_app()
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.session.commit()
        db.create_all()

        g1 = Gruppe(name="g1")
        g2 = Gruppe(name="g2")
        db.session.add(g1)
        db.session.add(g2)
        db.session.commit()

        b1 = Block(weekday=1, start="10:15", end="11:00", gruppe_id=g1.id, gruppe=g1)
        b2 = Block(weekday=1, start="11:15", end="12:00", gruppe_id=g1.id, gruppe=g1)
        b3 = Block(weekday=1, start="11:15", end="12:00", gruppe_id=g2.id, gruppe=g2)
        db.session.add(b1)
        db.session.add(b2)
        db.session.add(b3)
        db.session.commit()

        s1 = User(email="s1", password="pw", type="sus", gruppe=g1, gruppe_id=g1.id)
        s2 = User(email="s2", password="pw", type="sus", gruppe=g1, gruppe_id=g1.id)
        s3 = User(email="s3", password="pw", type="sus", gruppe=g1, gruppe_id=g1.id)
        s4 = User(email="s4", password="pw", type="sus", gruppe=g2, gruppe_id=g1.id)
        l1 = User(email="l1", password="pw", type="lp")
        l2 = User(email="l2", password="pw", type="lp")
        a1 = User(email="a1", password="pw", type="ap")
        db.session.add(s1)
        db.session.add(s2)
        db.session.add(s3)
        db.session.add(s4)
        db.session.add(l1)
        db.session.add(l2)
        db.session.add(a1)
        db.session.commit()

        s1.lp = l1
        s2.lp= l1
        s3.lp = l2
        s4.lp = l2
        db.session.commit()

        lb1 = Lernbuero(name="lb1", capacity=25, block=b1, block_id=b1.id, lp_id=l1.id, lp=l1, ort="ort1", gruppe=g1, gruppe_id=g1.id)
        lb2 = Lernbuero(name="lb2", capacity=25, block=b1, block_id=b1.id, lp_id=l2.id, lp=l2, ort="ort2", gruppe=g1, gruppe_id=g1.id)
        lb3 = Lernbuero(name="lb3", capacity=25, block=b2, block_id=b2.id, lp_id=l1.id, lp=l1, ort="ort3", gruppe=g1, gruppe_id=g1.id)
        lb4 = Lernbuero(name="lb4", capacity=25, block=b3, block_id=b3.id, lp_id=l1.id, lp=l1, ort="ort4", gruppe=g2, gruppe_id=g2.id)
        lb5 = Lernbuero(name="lb5", capacity=25, block=b2, block_id=b2.id, lp_id=l2.id, lp=l2, ort="ort5", gruppe=g1, gruppe_id=g1.id)
        db.session.add(lb1)
        db.session.add(lb2)
        db.session.add(lb3)
        db.session.add(lb4)
        db.session.add(lb5)
        db.session.commit()

        this_week = datetime.now().isocalendar()[1]
        lbis = dict()
        for lb in [lb1, lb2, lb3, lb4, lb5]:
            for kw in [this_week, this_week + 1, this_week + 2, this_week + 3]:
                lbi = LbInstance(lernbuero_id=lb.id, lernbuero=lb, participant_count=0, start=datetime.strptime(f"2020{kw}{lb.block.weekday}{lb.block.start}", "%G%V%u%H:%M").timestamp(), kw=kw)
                lbis[(lb.id, kw)] = lbi
                db.session.add(lbi)
        db.session.commit()

        e1 = Enrolment()
        e1.enroled_sus_ = s1
        lbis[(1, this_week)].enroled_sus.append(e1)

        e2 = Enrolment()
        e2.enroled_sus_ = s1
        e2.forced = True
        lbis[(2, this_week+1)].enroled_sus.append(e2)

        e3 = Enrolment()
        e3.enroled_sus_ = s1
        lbis[(5, this_week+2)].enroled_sus.append(e3)

        e4 = Enrolment()
        e4.enroled_sus_ = s2
        lbis[(1, this_week)].enroled_sus.append(e4)

        e5 = Enrolment()
        e5.enroled_sus_ = s2
        lbis[(2, this_week+2)].enroled_sus.append(e5)

        e6 = Enrolment()
        e6.enroled_sus_ = s3
        lbis[(1, this_week+1)].enroled_sus.append(e6)

        e7 = Enrolment()
        e7.enroled_sus_ = s2
        lbis[(4, this_week)].enroled_sus.append(e7)

        e8 = Enrolment()
        e8.enroled_sus_ = s2
        lbis[(5, this_week)].enroled_sus.append(e8)

        db.session.add(e1)
        db.session.add(e2)
        db.session.add(e6)
        db.session.add(e4)
        db.session.add(e5)
        db.session.add(e6)
        db.session.add(e7)
        db.session.add(e8)
        db.session.commit()

        gruppen=Gruppe.query.all()
        for g in gruppen:
            print(g)

        blocks = Block.query.all()
        for b in blocks:
            print(b)

        lbis = LbInstance.query.all()
        for lbi in lbis:
            print(lbi)
            enrolments = lbi.enroled_sus.all()
            for e in enrolments:
                print(e.enroled_sus_.email)


if __name__ == '__main__':
    main()
