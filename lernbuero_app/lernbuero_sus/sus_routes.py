from datetime import datetime, timedelta
import logging

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from lernbuero_app.models import Lernbuero, User, Enrolment, LbInstance, Block

from .. import db


logger = logging.getLogger(__name__)
sus_bp = Blueprint("sus_bp", __name__, template_folder="templates", static_folder="static")


@sus_bp.route('/api/v1/sus/enrolment/', methods=["GET", "POST"])
@jwt_required
def get_enrolled_in():
    print("enrolment start")
    user_cred = get_jwt_identity()
    print(request.json)
    print(type(request.json))
    print(type(user_cred))
    print(user_cred)
    if request.method == "POST" and "id" not in request.json.keys():
        return "Pad post request", 400
    if "user_type" not in user_cred.keys():
        return "Invalid user credentials", 400
    if user_cred["user_type"] != "sus":
        return "Invalid user type", 400
    if request.method == "POST":
        user = User.query.get(user_cred["user_id"])
        try:
            lb_instance = LbInstance.query.get(request.json["id"])
            all_enrolled = (Enrolment.query.filter_by(user_id=user.id)
                            .join(Enrolment.enroled_in_, aliased=True)
                            .filter_by(start=lb_instance.start)
                            .all())
            for e in all_enrolled:
                db.session.delete(e)
            db.session.commit()
            e = Enrolment()
            e.enroled_sus_ = user
            try:
                lb_instance.enroled_sus.append(e)
                db.session.commit()
            except IntegrityError:
                print("Enrolment failed")
                db.session.rollback()
        except KeyError:
            print("Wrong request")
            pass
    current_week = datetime.now().isocalendar()[1]
    user = User.query.get(user_cred["user_id"])
    enrolments = [e for e in user.enroled_in.all() if current_week <= e.enroled_in_.kw <= current_week+2]
    enrolment_info = [{"lb": e.enroled_in_.lernbuero.get_dict(),
                       "status": "forced" if e.forced else "normal",
                       "current": e.enroled_in_.participant_count,
                       "start": 0,
                       "id": e.enroled_in_.id} for e in enrolments]
    blocks = Block.query.filter_by(gruppe_id=user.gruppe_id).all()

    today = datetime.today()

    def one_week(offset):
        return {"index": current_week + offset,
                "from": today + timedelta(days=-today.weekday(), weeks=offset),
                "to": today + timedelta(days=-today.weekday() + 4, weeks=offset)}

    block_info = [{"id": b.id, "weekDay": b.weekday, "start": b.start, "end": b.end} for b in blocks]
    week_info = [one_week(i) for i in range(2)]
    return jsonify({"lbInstances": enrolment_info, "blocks": block_info, "kws": week_info}), 200


@sus_bp.route('/api/v1/sus/enrolment_options/', methods=["POST"])
@jwt_required
def get_enrolment_options():
    user_cred = get_jwt_identity()
    user = User.query.get(user_cred["user_id"])
    lbs = Lernbuero.query.filter_by(block_id=request.json["block_id"], gruppe_id=user.gruppe_id).all()
    lbis = {lb.id: LbInstance.query.filter_by(lernbuero_id=lb.id, kw=request.json["kw_index"]).first() for lb in lbs}
    lbis = {k: v for k, v in lbis.items() if v}
    lbs = [lb for lb in lbs if lb.id in lbis.keys()]
    counts = {}
    enrolled = {}
    for lb_id, lbi in lbis.items():
        all_enrolments = lbi.enroled_sus.all()
        counts[lb_id] = len(enrolled)
        enrolled[lb_id] = user.id in [e.user_id for e in all_enrolments]
    return jsonify([
        {"lb": {"name": lb.name, "lehrer": lb.lp.email, "ort": lb.ort, "soft": lb.capacity, "id": lb.id, "block": {}},
         "status": ("enrolled" if enrolled[lb.id] else "open"), "current": counts[lb.id], "id": lbis[lb.id].id
         } for lb in lbs
    ]), 200