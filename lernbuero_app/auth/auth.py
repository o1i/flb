from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import jwt_required, create_access_token
import pandas as pd
from werkzeug.security import safe_str_cmp

from lernbuero_app.post_functions import post_verification_lb, extract_info_lb
from lernbuero_app.delete_functions import delete_verification
from lernbuero_app.models import Lernbuero, User

from .. import db

app = current_app

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth_bp.route("/api/v1/auth", methods=["POST"])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(email=email).first()
    if not user or not safe_str_cmp(password.encode("utf-8"), user.password.encode("utf-8")):
        return jsonify({"msg": "Bad username or password"}), 401

    ret = {'access_token': create_access_token(email)}
    return jsonify(ret), 200


def add_claims_to_access_token(identity):
    user = User.query.filter_by(email=identity).first()
    return {
        'email': identity,
        'level': user.type,
        "id": user.id
    }