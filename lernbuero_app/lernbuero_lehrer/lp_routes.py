from datetime import datetime, timedelta
import logging

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from lernbuero_app.models import Lernbuero, User, Enrolment, LbInstance, Block

from .. import db


logger = logging.getLogger(__name__)
lp_bp = Blueprint("lp_bp", __name__, template_folder="templates", static_folder="static")


@lp_bp.route('/api/v1/lp/enrolment/', methods=["GET", "POST"])
@jwt_required
def get_enrolled_in():
    print("lp enrolment start")
    user_cred = get_jwt_identity()

    if request.method == "POST" and "id" not in request.json.keys():
        return "Pad post request", 400
    if "user_type" not in user_cred.keys():
        return "Invalid user credentials", 400
    if user_cred["user_type"] != "lp":
        return f"Invalid user type, expected lp, got {user_cred['user_type']}", 400
    if request.method == "POST":
        try:
            sus_id = request.json["sus_id"]
            lbi_id = request.json["lbi_id"]
            action = request.json["action"]
        except KeyError:
            print("Wrong request")
            return "incomplete request", 400
        if action not in ["enrol", "unenrol"]:
            return "Bad post request", 400
        if action == "enrol":
            sus = User.query.get(sus_id)
            lbi = LbInstance.query.get(lbi_id)
            e = Enrolment()
            e.enroled_sus_ = sus
            try:
                lbi.enroled_sus.append(e)
                db.session.commit()
            except IntegrityError:
                print("something went wrong with registration")
                db.session.rollback()
        if action == "unenrol":
            e = Enrolment.query.filter_by(user_id=sus.id, lbinstance_id=lbi.id).first()
            if e:
                db.session.delete(e)
                db.session.commit()
            del e

    # get part
    this_week = datetime.now().isocalendar()[1]
    kws = [this_week, this_week + 1, this_week + 2]
    enrolments = (
        db.session.query(LbInstance, Lernbuero, Enrolment, User, Block)
            .filter(LbInstance.lernbuero_id == Lernbuero.id)
            .filter(Lernbuero.block_id == Block.id)
            .filter(LbInstance.id == Enrolment.lbinstance_id)
            .filter(Enrolment.user_id == User.id)
            .filter(Lernbuero.lp_id == user_cred["user_id"])
            .filter(LbInstance.kw.in_(kws))
            .all()
        )
    lbis = {(e[0].id, e[0].kw): {"lbInstance": {
        "lb": {"id": e[1].id, "name": e[1].name, "ort": e[1].ort, "soft": e[1].capacity,
               "block": {"weekDay": e[4].weekday, "start": e[4].end, "end": e[4].end}},
        "current": 0, "start": e[0].start, "id": e[0].id},
                                 "sus": []} for e in enrolments}
    for e in enrolments:
        lbis[(e[0].id, e[0].kw)]["sus"].append({"name": e[3].email, "id": e[3].id})

    out = [[v for k, v in lbis.items() if k[1] == kw] for kw in kws]
    return jsonify(out), 200


@lp_bp.route('/api/v1/lp/list_sus/', methods=["POST"])
@jwt_required
def get_enrolment_options():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "lp":
        return "Invalid user credentials", 400
    if "lbinstance_id" not in request.json.keys():
            return "incomplete request", 400
    sus = LbInstance.query.get(request.json["lbinstance_id"]).lernbuero.gruppe.users
    return jsonify([{"name": s.email, "id": s.id} for s in sus if s.type=="sus"]), 200
