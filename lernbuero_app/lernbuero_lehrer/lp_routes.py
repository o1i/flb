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
    user_cred = get_jwt_identity()
    # request.json:  {sus_id: Number, lbi_id: Number, action: "enrol"|"unenrol"}
    if request.method == "POST" and "sus_id" not in request.json.keys():
        return jsonify(["Bad post request"]), 400
    if "user_type" not in user_cred.keys():
        return jsonify(["Invalid user credentials"]), 400
    if user_cred["user_type"] != "lp":
        return jsonify([f"Invalid user type, expected lp, got {user_cred['user_type']}"]), 400
    if request.method == "POST":
        try:
            sus_id = request.json["sus_id"]
            lbi_id = request.json["lbi_id"]
            action = request.json["action"]
        except KeyError:
            return "incomplete request", 400
        if action not in ["enrol", "unenrol"]:
            return "Bad post request", 400
        if action == "enrol":
            sus = User.query.get(sus_id)
            lbi = LbInstance.query.get(lbi_id)
            e = Enrolment()
            e.enroled_sus_ = sus
            e.forced = True
            db.session.add(e)
            try:
                lbi.enroled_sus.append(e)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        if action == "unenrol":
            e = Enrolment.query.filter_by(user_id=sus_id, lbinstance_id=lbi_id).first()
            if e:
                db.session.delete(e)
                db.session.commit()
            del e

    # get part
    this_week = datetime.now().isocalendar()[1]
    kws = [this_week, this_week + 1, this_week + 2]
    enrolments = (
        db.session.query(LbInstance, Lernbuero, Block, Enrolment, User)
            .filter(LbInstance.lernbuero_id == Lernbuero.id)
            .filter(Lernbuero.block_id == Block.id)
            .filter(Lernbuero.lp_id == user_cred["user_id"])
            .filter(LbInstance.kw.in_(kws))
            .join(Enrolment, LbInstance.id == Enrolment.lbinstance_id, isouter=True)
            .join(User, User.id == Enrolment.user_id, isouter=True)
            .all()
        )
    lbis = {(e[0].id, e[0].kw): {
        "lbInstance": {
            "lb": {"id": e[1].id, "name": e[1].name, "ort": e[1].ort, "soft": e[1].capacity,
                   "block": {"weekDay": e[2].weekday, "start": e[2].start, "end": e[2].end}},
            "current": 0, "start": e[0].start, "id": e[0].id},
        "sus": []} for e in enrolments}

    for e in enrolments:
        if e[4] is not None:
            lbis[(e[0].id, e[0].kw)]["sus"].append({"name": e[4].email, "id": e[4].id})

    for k, v in lbis.items():
        lbis[k]["lbInstance"]["current"] = len(lbis[k]["sus"])

    out = [[v for k, v in lbis.items() if k[1] == kw] for kw in kws]
    for part in out:
        part.sort(key=lambda x: x["lbInstance"]["start"])
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
    return jsonify([{"name": s.email, "id": s.id} for s in sus if s.type == "sus"]), 200
