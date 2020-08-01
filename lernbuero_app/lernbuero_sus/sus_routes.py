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


@sus_bp.route('/api/v1/lb/sus', methods=["GET", "POST", "DELETE"])
@jwt_required
def lb():
    if "DEBUG" in os.environ.keys(): logger.info("/api/v1/lb/sus")
    logger.info("lb/sus")
    claims = get_jwt_claims()
    print(f"claims: {claims}")

    if request.method == "POST":
        if "DEBUG" in os.environ.keys(): logger.info("post")
        content = request.json
        print(f"content: {content}")
        logger.info(content)
        spare_capacity_query = db.session.query(db.func.count(Lernbuero.enroled_sus), Lernbuero.capacity)\
            .select_from(Lernbuero).filter(Lernbuero.id == content["lb"])
        spare_capacity = pd.read_sql(spare_capacity_query.statement, spare_capacity_query.session.bind)
        print(spare_capacity)
        lb = Lernbuero.query.get(content["lb"])
        enrolled = sum(1 for _ in lb.enroled_sus)
        print(f"enrolled: {enrolled}")
        is_free = lb.capacity > enrolled
        print(f"is_free: {is_free}")
        if content["enrolled"] or is_free:
            try:
                subscription_verification(content)
                lb_in_kw = db.session.query(Lernbuero).\
                    filter(Lernbuero.kw==content["kw"]).\
                    with_entities(Lernbuero.id).all()
                for lb_id in lb_in_kw:
                    e = Enrolment.query.get((lb_id[0], claims["id"]))
                    print("lb: {lb}")
                    if e:
                        db.session.delete(e)
                    unsubscribe_lb = Lernbuero.query.get(lb_id[0])
                    new_enrolled = sum(1 for _ in unsubscribe_lb.enroled_sus)
                    unsubscribe_lb.participant_count = new_enrolled
                    db.session.commit()
                print("append")
                if not content["enrolled"] and is_free:
                    subscribe_lb = Lernbuero.query.get(content["lb"])
                    e = Enrolment()
                    e.enroled_sus_ = User.query.get(claims["id"])
                    subscribe_lb.enroled_sus.append(e)
                    new_enrolled = sum(1 for _ in subscribe_lb.enroled_sus)
                    subscribe_lb.participant_count = new_enrolled
                    db.session.commit()
            except AssertionError as err:
                logger.debug(err)

    if "DEBUG" in os.environ.keys(): logger.info("return")
    query = db.session.query(Lernbuero)
    df = pd.read_sql(query.statement, query.session.bind)
    enscribed = db.session.query(Enrolment).\
        filter(Enrolment.user_id==claims["id"])
    enrolled = pd.read_sql(enscribed.statement, enscribed.session.bind)
    df["enrolled"] = df["id"].isin(enrolled["lernbuero_id"])
    return jsonify(df
                   .groupby("kw")
                   .apply(lambda x: x.to_dict("records"))
                   .to_dict()), 200


@sus_bp.route('/api/v1/lb/sus/test', methods=["GET"])
@jwt_required
def test():
    user = get_jwt_identity()
    print(type(user))
    print(user)
    return jsonify({"test": "sucess"}), 200