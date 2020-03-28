from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import jwt_required, create_access_token
import pandas as pd

from lernbuero_app.post_functions import post_verification, extract_info
from lernbuero_app.delete_functions import delete_verification
from lernbuero_app.models import Lernbuero

from .. import db

app = current_app

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")

@auth_bp.route("/auth", methods=["POST"])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'test' or password != 'test':
        return jsonify({"msg": "Bad username or password"}), 401

    ret = {'access_token': create_access_token(username)}
    return jsonify(ret), 200
