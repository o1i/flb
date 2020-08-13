from datetime import datetime, timedelta
import logging

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from lernbuero_app.models import Lernbuero, User, Enrolment, LbInstance, Block, Gruppe

from .. import db


logger = logging.getLogger(__name__)
ap_bp = Blueprint("ap_bp", __name__, template_folder="templates", static_folder="static")


@ap_bp.route('/api/v1/ap/gruppe/', methods=["GET", "POST", "DELETE"])
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
            db.session.rollback()
            pass
    if request.method == "DELETE":
        # delete with payload [id1, id2,...]
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            delete_groups = db.session.query(Gruppe).filter(Gruppe.id.in_(request.json)).all()
            for g in delete_groups:
                db.session.delete(g)
            db.session.commit()
        except:
            print("rolling back")
            db.session.rollback()
                
    gruppen = Gruppe.query.all()
    return jsonify([{"name": g.name, "id": g.id} for g in gruppen]), 200


@ap_bp.route('/api/v1/ap/block/', methods=["GET", "POST", "DELETE"])
@jwt_required
def block():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return "Invalid user credentials", 400
    gruppe_get = None
    if request.method == "POST":
        print("block post")
        # call with list of dicts.
        # dicts with "id" as keys can be used to modify blocks (weekday, start, end)
        # dicts without "id" are assumed to have the key "gruppe" so that they can be matched
        gruppen = dict()
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            for b in request.json:
                if "id" in b.keys():
                    block = Block.query.get(b["id"])
                    gruppe_get = block.gruppe_id
                    if "weekday" in b.keys():
                        block.weekday = b["weekday"]
                    if "start" in b.keys():
                        block.start = b["start"]
                    if "end" in b.keys():
                        block.end = b["end"]
                else:
                    if b["gruppe"] not in gruppen.keys():
                        gruppen[b["gruppe"]] = Gruppe.query.get(b["gruppe"])
                        gruppe_get = b["gruppe"]
                    if "start" in b.keys() and "end" in b.keys() and "weekday" in b.keys():  # only accept complete
                        db.session.add(Block(weekday=b["weekday"], start=b["start"], end=b["end"], gruppe_id=b["gruppe"],
                                             gruppe=gruppen[b["gruppe"]]))
            db.session.commit()
        except Exception:
            db.session.rollback()
            pass

    if request.method == "DELETE":
        print("block delete")
        # call with a list of ids
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            delete_blocks = db.session.query(Block).filter(Block.id.in_(request.json)).all()
            for b in delete_blocks:
                gruppe_get = b.gruppe_id
                db.session.delete(b)
            db.session.commit()
        except:
            db.session.rollback()
    print("block get")
    # get is never called, since at least the group must be specified. if you want get, call post with [{gruppe: id}]
    # If the call is post or delete, the latest gruppe_id of affected blocks is taken
    bloecke = Block.query.filter_by(gruppe_id=gruppe_get)
    return jsonify([{"id": b.id, "gruppe_id": b.gruppe_id, "weekday": b.weekday, "start": b.start,
                     "end": b.end} for b in bloecke]), 200


@ap_bp.route('/api/v1/ap/user/', methods=["GET", "POST", "DELETE"])
@jwt_required
def user():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return "Invalid user credentials", 400
    if request.method == "POST":
        gruppen = dict()
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            for u in request.json:
                invalid = ("type" in u.keys and u["type"] == "ap")
                if "id" in u.keys() and not invalid:
                    user = Gruppe.query.get(u["id"])
                    user.email = u["email"] if "email" in u.keys() else user.email
                    user.password = u["password"] if "password" in u.keys() else user.password
                    user.type = u["type"] if "type" in u.keys() else user.type
                    user.gruppe_id = u["gruppe"] if "gruppe" in u.keys() else user.gruppe
                    if "gruppe" in u.keys() and not u["gruppe"] in gruppen.keys():
                        gruppen[u["gruppe"]] = Gruppe.query.get(u["gruppe"])
                    user.gruppe = gruppen[u["gruppe"]]
                elif not invalid:
                    if "gruppe" in u.keys() and not u["gruppe"] in gruppen.keys():
                        gruppen[u["gruppe"]] = Gruppe.query.get(u["gruppe"])
                    db.session.add(User(email=u["email"],
                                        password=u["password"],
                                        type=u["type"],
                                        gruppe_id=u["gruppe"] if "gruppe" in u.keys() else None,
                                        gruppe=gruppen[u["gruppe"]] if "gruppe" in u.keys() else None,
                                        ))
            db.session.commit()
        except Exception:
            db.session.rollback()
            pass
        
    if request.method == "DELETE":
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            delete_users = db.session.query(User).filter(User.id.in_(request.json)).all()
            for u in delete_users:
                if u.type in ["sus", "lp"]:
                    db.session.delete(u)
            db.session.commit()
        except:
            db.session.rollback()
        
    users = User.query.all()
    return jsonify([{"name": u.email, "id": u.id, "password": u.password, "type": u.type, "gruppe_id": u.gruppe_id} for u in users]), 200