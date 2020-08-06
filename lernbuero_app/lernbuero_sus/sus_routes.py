from datetime import datetime
import logging
import os

from flask import request, jsonify, Blueprint, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
import pandas as pd
from sqlalchemy.exc import IntegrityError

from lernbuero_app.post_functions import subscription_verification, extract_info_lb
from lernbuero_app.models import Lernbuero, User, Enrolment, LbInstance

from .. import db


logger = logging.getLogger(__name__)
sus_bp = Blueprint("sus_bp", __name__, template_folder="templates", static_folder="static")


@sus_bp.route('/api/v1/sus/enrolment/', methods=["GET", "POST"])
@jwt_required
def get_enrolled_in():
    user_cred = get_jwt_identity()
    if request.method == "POST":
        user = User.query.get(user_cred["user_id"])
        lb_instance = LbInstance.query.get(request.json["id"])
        e = Enrolment()
        e.enroled_sus_ = user
        try:
            lb_instance.enroled_sus.append(e)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    current_week = datetime.now().isocalendar()[1]
    user = User.query.get(user_cred["user_id"])
    enrolments = [e for e in user.enroled_in.all() if current_week <= e.enroled_in_.kw <= current_week+2]
    enrolment_info = [{"lb": e.enroled_in_.lernbuero.get_dict(),
                       "status": e.forced,
                       "current": e.enroled_in_.participant_count,
                       "start": 0,
                       "id": e.enroled_in_.id} for e in enrolments]
    return jsonify(enrolment_info), 200
