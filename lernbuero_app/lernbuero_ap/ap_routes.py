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
def blocks():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return "Invalid user credentials", 400
    if request.method == "POST":
        if "id" in request.json.keys() and "name" in request.json.keys():
            gruppe = Gruppe.query.get(request.json["id"])
            gruppe.name = request.json["name"]
            db.session.commit()
        elif "name" in request.json.keys():
            gruppe = Gruppe(name=request.json["name"])
            db.session.add(gruppe)
            db.session.commit()
    gruppen = Gruppe.query.all()
    return jsonify([{"name": g.name, "id": g.id} for g in gruppen]), 200


@ap_bp.route('/api/v1/ap/block/', methods=["GET", "POST"])
@jwt_required
def blocks():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return "Invalid user credentials", 400
    return jsonify([]), 200
