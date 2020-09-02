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
                if "id" in g.keys() and g["id"] > 0:
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
        # call with list of dicts.
        # dicts with "id" as keys can be used to modify blocks (weekday, start, end)
        # dicts without "id" are assumed to have the key "gruppe" so that they can be matched
        gruppen = dict()
        try:
            if not isinstance(request.json, list):
                return "invalid request", 400
            for b in request.json:
                # if gruppe is in keys, ignore the rest (only get) (payload: [{gruppe: x}]
                if "gruppe_get" in b.keys():
                    gruppe_get = b["gruppe_get"]
                elif "id" in b.keys():
                    block = Block.query.get(b["id"])
                    gruppe_get = block.gruppe_id
                    if "weekday" in b.keys():
                        block.weekday = b["weekday"]
                    if "start" in b.keys():
                        block.start = b["start"]
                    if "end" in b.keys():
                        block.end = b["end"]
                else:
                    if b["gruppe"]["id"] not in gruppen.keys():
                        gruppen[b["gruppe"]["id"]] = Gruppe.query.get(b["gruppe"]["id"])
                        gruppe_get = b["gruppe"]["id"]
                    if "start" in b.keys() and "end" in b.keys() and "weekday" in b.keys():  # only accept complete
                        db.session.add(Block(weekday=b["weekday"], start=b["start"], end=b["end"], gruppe_id=b["gruppe"]["id"],
                                             gruppe=gruppen[b["gruppe"]["id"]]))
            db.session.commit()
        except ValueError:
            db.session.rollback()
            pass

    if request.method == "DELETE":
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
    # get is never called, since at least the group must be specified. if you want get, call post with [{gruppe: id}]
    # If the call is post or delete, the latest gruppe_id of affected blocks is taken
    bloecke = Block.query.filter_by(gruppe_id=gruppe_get).all()
    return jsonify([{"id": b.id, "gruppe": {"id": b.gruppe_id}, "weekDay": b.weekday, "start": b.start,
                     "end": b.end} for b in bloecke]), 200


@ap_bp.route('/api/v1/ap/lernbuero/', methods=["POST", "DELETE"])
@jwt_required
def lernbuero():
    # Never called with get, since block id has to be provided.
    # Get: {"block_id": block_id}
    # Add/Edit: dict with id, name ,capacity, lp_id, block, ort. id<0 means add
    # delete: {"id": id}
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        return jsonify(["Bad user type"]), 400
    block_to_get = -1
    if request.method == "POST":
        if "block_id" in request.json.keys():  # get
            block_to_get = request.json["block_id"]
        elif not {"id", "name", "capacity", "lp_name", "block", "ort"} - request.json.keys():
            block = Block.query.get(request.json["block"]["id"])
            block_to_get = block.id
            lp = db.session.query(User).filter(User.email == request.json["lp_name"]).first()
            if not lp:
                return jsonify(["invalid teacher name"]), 400
            if request.json["id"] > 0:  # edit
                lb = Lernbuero.query.get(request.json["id"])
                lb.name = request.json["name"]
                lb.capacity = request.json["capacity"]
                lb.lp_id = lp.id
                lb.ort = request.json["ort"]
                db.session.commit()
            else:  # add
                gruppe = Gruppe.query.get(request.json["block"]["gruppe"]["id"])
                lb = Lernbuero(
                    name=request.json["name"],
                    capacity=request.json["capacity"],
                    lp_id=lp.id,
                    lp=lp,
                    gruppe_id=request.json["block"]["gruppe"]["id"],
                    gruppe=gruppe,
                    block_id=request.json["block"]["id"],
                    block=block,
                    ort=request.json["ort"]
                )
                db.session.add(lb)
                this_week = datetime.now().isocalendar()[1]
                for i in range(52):
                    start = datetime.strptime(str(datetime.now().year)+str(this_week)+str(block.weekday)+block.start,
                                              "%G%V%u%H:%M") + timedelta(weeks=i)
                    db.session.add(LbInstance(
                        lernbuero_id=lb.id,
                        lernbuero=lb,
                        participant_count=0,
                        start=int(start.timestamp()),
                        kw=start.strftime("%V")
                    ))
                db.session.commit()
    if request.method == "DELETE":
        try:
            lb = Lernbuero.query.get(request.json["id"])
            block_to_get = lb.block_id
            lbis = db.session.query(LbInstance).filter(LbInstance.lernbuero_id == lb.id).all()
            enrolments = db.session.query(Enrolment).filter(Enrolment.lbinstance_id.in_([lbi.id for lbi in lbis])).all()
            for e in enrolments:
                db.session.delete(e)
            for lbi in lbis:
                db.session.delete(lbi)
            db.session.delete(lb)
            db.session.commit()
        except Exception:
            db.session.rollback()
    lbs = (db.session.query(Lernbuero, User, Block, Gruppe)
           .filter(Lernbuero.lp_id == User.id)
           .filter(Lernbuero.block_id == Block.id)
           .filter(Block.gruppe_id == Gruppe.id)
           .filter(Lernbuero.block_id == block_to_get)
           .all())
    out = [{"name": lb.Lernbuero.name,
            "lehrer": lb.User.email,
            "ort": lb.Lernbuero.ort,
            "soft": lb.Lernbuero.capacity,
            "hard": 1000000,
            "block": {"weekDay": lb.Block.weekday,
                      "start": lb.Block.start,
                      "end": lb.Block.end,
                      "gruppe": {"name": lb.Gruppe.name,
                                 "id": lb.Gruppe.id},
                      "id": lb.Lernbuero.block.id},
            "block_id": lb.Lernbuero.block_id,
            "id": lb.Lernbuero.id,
            } for lb in
         lbs]
    return jsonify(out), 200


@ap_bp.route('/api/v1/ap/user/', methods=["GET", "POST", "DELETE"])
@jwt_required
def user():
    user_cred = get_jwt_identity()
    if "user_type" not in user_cred.keys() or user_cred["user_type"] != "ap":
        print("208")
        return "Invalid user credentials", 400
    if request.method == "POST":
        gruppen = dict()
        try:
            if not isinstance(request.json, list):
                print("213")
                return "invalid request", 400
            for u in request.json:
                invalid = ("type" in u.keys() and u["type"] == "ap")
                if "id" in u.keys() and not invalid:
                    user = User.query.get(u["id"])
                    user.email = u["email"] if "email" in u.keys() else user.email
                    user.password = u["password"] if "password" in u.keys() else user.password
                    user.type = u["type"] if "type" in u.keys() else user.type
                    user.gruppe_id = u["gruppe"] if "gruppe" in u.keys() else user.gruppe_id
                    if "gruppe" in u.keys() and not u["gruppe"] in gruppen.keys():
                        gruppen[u["gruppe"]] = Gruppe.query.get(u["gruppe"])
                    user.gruppe = gruppen[u["gruppe"]] if "gruppe" in u.keys() else user.gruppe
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
        except:
            db.session.rollback()
            pass
        
    if request.method == "DELETE":
        try:
            if not isinstance(request.json, list):
                print("242")
                return "invalid request", 400
            delete_users = db.session.query(User).filter(User.id.in_(request.json)).all()
            for u in delete_users:
                if u.type in ["sus", "lp"]:
                    db.session.delete(u)
            db.session.commit()
        except:
            db.session.rollback()
    users = (db.session.query(User, Gruppe)
             .outerjoin(Gruppe, User.gruppe_id == Gruppe.id)
             .all())
    out = [{
        "name": u.User.email,
        "id": u.User.id,
        "password": u.User.password,
        "type": u.User.type,
        "gruppe": u.Gruppe.name if u[1] is not None else "",
    } for u in users]
    return jsonify(out), 200