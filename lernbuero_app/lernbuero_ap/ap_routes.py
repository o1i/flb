from datetime import datetime, timedelta
import logging

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from lernbuero_app.models import Lernbuero, User, Enrolment, LbInstance, Block, Gruppe

from .. import db


logger = logging.getLogger(__name__)
ap_bp = Blueprint("ap_bp", __name__, template_folder="templates", static_folder="static")


@ap_bp.route('/api/v1/ap/gruppe/', methods=["GET", "POST"])
@jwt_required
def gruppe():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return "Invalid user credentials", 400
    if request.method == "POST":
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            for g in request.json:
                if "id" in g.keys():
                    gruppe = Gruppe.query.get(g["id"])
                    gruppe.name = g["name"]
                else:
                    db.session.add(Gruppe(name=g["name"]))
            db.session.commit()
        except Exception:
            pass
    gruppen = Gruppe.query.all()
    return jsonify([{"name": g.name, "id": g.id} for g in gruppen]), 200


@ap_bp.route('/api/v1/ap/block/', methods=["GET", "POST"])
@jwt_required
def block():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return "Invalid user credentials", 400
    if request.method == "POST":
        gruppen = dict()
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            for b in request.json["blocks"]:
                if "id" in b.keys:
                    block = Block.query.get(b["id"])
                    if "weekday" in b.keys():
                        block.weekday = b["weekday"]
                    if "start" in b.keys():
                        block.start = b["start"]
                    if "end" in b.keys():
                        block.end = b["end"]
                else:
                    if b["gruppe"] not in gruppen.keys():
                        gruppen[b["gruppe"]] = Gruppe.query.get(b["gruppe"])
                    db.session.add(Block(weekday=b["weekday"], start=b["start"], end=b["end"], gruppe_id=b["gruppe"],
                                         gruppe=gruppen[b["gruppe"]]))
            db.session.commit()
        except Exception:
            pass
    bloecke = Block.query.filter_by(gruppe_id=b["gruppe"])
    return jsonify([{"gruppe_id": b.gruppe_id, "weekday": b.weekday, "start": b.start,
                     "end": b.end} for b in bloecke]), 200
