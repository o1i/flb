from flask import request, jsonify, Blueprint
import pandas as pd

from lernbuero_app.post_functions import post_verification, extract_info
from lernbuero_app.delete_functions import delete_verification
from lernbuero_app.models import Lernbuero

from .. import db


lehrer_bp = Blueprint("lehrer_bp", __name__, template_folder="templates", static_folder="static")


@lehrer_bp.route('/')
@lehrer_bp.route('/api/v1/lb', methods=["GET", "POST", "DELETE"])
def lb():
    if request.method == "DELETE":
        content = request.json
        try:
            print(content)
            delete_verification(content)
            print("content ok")
            Lernbuero.query.filter_by(id=content["id"]).delete()
            db.session.commit()
        except AssertionError:
            pass

    if request.method == "POST":
        content = request.json
        try:
            post_verification(content)
            lernbuero_instance = Lernbuero(**extract_info(content))
            db.session.add(lernbuero_instance)
            db.session.commit()
        except AssertionError:
            pass

    query = db.session.query(Lernbuero)
    return jsonify(pd.read_sql(query.statement, query.session.bind)
                   .groupby("kw")
                   .apply(lambda x: x.to_dict("records"))
                   .to_dict())
