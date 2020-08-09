from datetime import datetime, timedelta
import logging

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from lernbuero_app.models import Lernbuero, User, Enrolment, LbInstance, Block

from .. import db


logger = logging.getLogger(__name__)
ap_bp = Blueprint("ap_bp", __name__, template_folder="templates", static_folder="static")


@ap_bp.route('/api/v1/ap/block/', methods=["GET", "POST"])
@jwt_required
def get_enrolment_options():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return "Invalid user credentials", 400
    return jsonify([]), 200
