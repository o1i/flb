from datetime import datetime
import logging
import os

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
import pandas as pd

from lernbuero_app.post_functions import subscription_verification, extract_info_lb
from lernbuero_app.models import Lernbuero, User, Enrolment

from .. import db


logger = logging.getLogger(__name__)
sus_bp = Blueprint("sus_bp", __name__, template_folder="templates", static_folder="static")


@sus_bp.route('/api/v1//sus/get_enrolled_in', methods=["GET"])
@jwt_required
def get_enrolled_in():
    user_cred = get_jwt_identity()
    current_week = datetime.now().isocalendar()[1]
    user = User.query.get(user_cred["user_id"])
    enrolments = [e for e in user.enroled_in.all() if current_week <= e.enroled_in_.kw <= current_week+2]
    print(enrolments)
    enrolment_info = [{"lb": e.enroled_in_.lernbuero.get_dict(),
                       "status": e.forced,
                       "current": e.enroled_in_.participant_count,
                       "start": 0,
                       "id": e.enroled_in_.id} for e in enrolments]
    return jsonify(enrolment_info), 200


@sus_bp.route('/api/v1/lb/sus/test', methods=["GET"])
@jwt_required
def test():
    user = get_jwt_identity()
    print(type(user))
    print(user)
    return jsonify({"test": "sucess"}), 200