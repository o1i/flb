import logging
import os

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_claims
import pandas as pd

from lernbuero_app.post_functions import subscription_verification, extract_info_lb
from lernbuero_app.models import Lernbuero, User

from .. import db


logger = logging.getLogger(__name__)
sus_bp = Blueprint("sus_bp", __name__, template_folder="templates", static_folder="static")


@sus_bp.route('/api/v1/lb/sus', methods=["GET", "POST", "DELETE"])
@jwt_required
def lb():
    if "DEBUG" in os.environ.keys(): logger.info("/api/v1/lb/sus")
    logger.info("lb/sus")
    claims = get_jwt_claims()

    if request.method == "POST":
        if "DEBUG" in os.environ.keys(): logger.info("post")
        content = request.json
        logger.info(content)
        try:
            print("trying")
            print(content)
            print(content["enrolled"])
            subscription_verification(content)
            sus = User.query.filter_by(id=claims["id"]).first()
            sus.enroled_in = sus.enroled_in.filter(Lernbuero.kw != content["kw"])
            sus.enroled_in.append(Lernbuero.query.get(content["lb"]))
            db.session.commit()
        except AssertionError as err:
            logger.debug(err)

    if "DEBUG" in os.environ.keys(): logger.info("return")
    query = db.session.query(Lernbuero)
    df = pd.read_sql(query.statement, query.session.bind)
    enscribed = db.session.query(User, Lernbuero).\
        filter(Lernbuero.id==User.enroled_in).\
        filter(User.id == claims["id"]).\
        with_entities(Lernbuero.id)
    enrolled = pd.read_sql(enscribed.statement, enscribed.session.bind)
    df["enrolled"] = df["id"].isin(enrolled["id"])
    return jsonify(df
                   .groupby("kw")
                   .apply(lambda x: x.to_dict("records"))
                   .to_dict()), 200

