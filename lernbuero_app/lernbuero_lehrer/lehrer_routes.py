import logging
import os

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
import pandas as pd
from sqlalchemy import update

from lernbuero_app.post_functions import post_verification_lb, extract_info_lb, post_verification_user
from lernbuero_app.delete_functions import delete_verification
from lernbuero_app.models import Lernbuero, User

from .. import db


logger = logging.getLogger(__name__)
lehrer_bp = Blueprint("lehrer_bp", __name__, template_folder="templates", static_folder="static")


@lehrer_bp.route('/api/v1/lb/lehrer', methods=["GET", "POST", "DELETE"])
@jwt_required
def lb():
    if "DEBUG" in os.environ.keys(): logger.info("/api/v1/lb/lehrer")
    logger.info("lb/lehrer")
    logger.info(request)
    if request.method == "DELETE":
        if "DEBUG" in os.environ.keys(): logger.info("delete")
        content = request.json
        try:
            logger.info(content)
            delete_verification(content)
            logger.info("content ok")
            Lernbuero.query.filter_by(id=content["id"]).delete()
            db.session.commit()
        except AssertionError:
            pass

    if request.method == "POST":
        if "DEBUG" in os.environ.keys(): logger.info("post")
        content = request.json
        try:
            post_verification_lb(content)
            lernbuero_instance = Lernbuero(**extract_info_lb(content))
            db.session.add(lernbuero_instance)
            db.session.commit()
        except AssertionError:
            pass

    if "DEBUG" in os.environ.keys(): logger.info("return")
    query = db.session.query(Lernbuero)
    return jsonify(pd.read_sql(query.statement, query.session.bind)
                   .groupby("kw")
                   .apply(lambda x: x.to_dict("records"))
                   .to_dict())


@lehrer_bp.route('/api/v1/users/lehrer', methods=["GET", "POST", "DELETE"])
@jwt_required
def handle_sus():
    if request.method == "DELETE":
        content = request.json
        try:
            logger.info(content)
            delete_verification(content)
            logger.info("content ok")
            User.query.filter_by(id=content["id"]).delete()
            db.session.commit()
        except AssertionError:
            pass

    if request.method == "POST":
        content = request.json
        try:
            post_verification_user(content)
            new_pw = 'abcd'
            existing = User.query.filter_by(email=content["email"]).first()
            if existing:
                stmt = update(User).where(User.id == existing.id).values(password=new_pw)
            else:
                user_instance = User(email=content["email"], password=new_pw, level="feeder")
                db.session.add(user_instance)
            db.session.commit()
        except AssertionError:
            pass

    query = db.session.query(Lernbuero)
    return jsonify(["success"]), 200
