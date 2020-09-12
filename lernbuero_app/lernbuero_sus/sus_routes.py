from datetime import datetime, timedelta
import logging

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from lernbuero_app.models import Lernbuero, User, Enrolment, LbInstance, Block

from .. import db


logger = logging.getLogger(__name__)
sus_bp = Blueprint("sus_bp", __name__, template_folder="templates", static_folder="static")


@sus_bp.route('/api/v1/sus/enrolment/', methods=["GET", "POST", "DELETE"])
@jwt_required
def get_enrolled_in():
    user_cred = get_jwt_identity()
    if request.method == "POST" and "id" not in request.json.keys():
        return jsonify(["Pad post request"]), 400
    if "user_type" not in user_cred.keys():
        return jsonify(["Invalid user credentials"]), 400
    if user_cred["user_type"] != "sus":
        return jsonify(["Invalid user type"]), 400
    user = User.query.get(user_cred["user_id"])
    if request.method == "POST":
        try:
            lb_instance = LbInstance.query.get(request.json["id"])
            if len(lb_instance.enroled_sus.all()) < lb_instance.lernbuero.capacity:
                all_enrolled = (Enrolment.query.filter_by(user_id=user.id)
                                .join(Enrolment.enroled_in_, aliased=True)
                                .filter_by(start=lb_instance.start)
                                .all())
                for e in all_enrolled:
                    db.session.delete(e)
                db.session.commit()
                e = Enrolment()
                e.enroled_sus_ = user
                e.forced = False
                db.session.add(e)
                try:
                    lb_instance.enroled_sus.append(e)
                    db.session.commit()
                except IntegrityError:
                    print("Enrolment failed")
                    db.session.rollback()
        except KeyError:
            print("Wrong request")
            pass
    if request.method == "DELETE":
        enrolments = (db.session.query(Enrolment)
                      .filter(Enrolment.lbinstance_id == request.json["lbi_id"])
                      .filter(Enrolment.user_id == user.id)
                      .all())
        if enrolments:
            for e in enrolments:  # there should be only one, but one never knows
                db.session.delete(e)
            db.session.commit()
    current_week = datetime.now().isocalendar()[1]
    user = User.query.get(user_cred["user_id"])
    enrolments = [e for e in user.enroled_in.all() if current_week <= e.enroled_in_.kw <= current_week+2]
    enrolment_info = [{"lb": e.enroled_in_.lernbuero.get_dict(),
                       "status": "forced" if e.forced else (
                           "expired" if e.enroled_in_.start < datetime.now().timestamp() else "enrolled"),
                       "current": e.enroled_in_.participant_count,
                       "start": e.enroled_in_.start,
                       "id": e.enroled_in_.id} for e in enrolments]
    blocks = Block.query.filter_by(gruppe_id=user.gruppe_id).all()

    today = datetime.today()

    def one_week(offset):
        return {"index": current_week + offset,
                "from": (today + timedelta(days=-today.weekday(), weeks=offset)).strftime("%d.%m."),
                "to": (today + timedelta(days=-today.weekday() + 4, weeks=offset)).strftime("%d.%m.")}
    block_info = [{"id": b.id, "weekDay": b.weekday, "start": b.start, "end": b.end} for b in blocks]
    block_info.sort(key=lambda x: x["start"])
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