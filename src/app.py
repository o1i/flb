from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import pandas as pd

from src.post_functions import post_verification, extract_info
from src.delete_functions import delete_verification

app = Flask(__name__)
try:
    app.config.from_envvar('SERVER_CONFIG')
except RuntimeError:
    from flask_cors import CORS
    app.config.from_object('src.defaultconfig')
    CORS(app)
db = SQLAlchemy(app)


class Lernbuero(db.Model):
    __tablename__ = "lernbueros"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    start = db.Column(db.Integer())
    end = db.Column(db.Integer())
    kw = db.Column(db.Integer())


# l1 = Lernbuero(name="first", start=datetime(2020,3,1,12).timestamp(), end=datetime(2020,3,1,12,45).timestamp(), kw=1)
# l2 = Lernbuero(name="first", start=datetime(2020,3,1,12,45).timestamp(), end=datetime(2020,3,1,13,30).timestamp(), kw=1)
# l3 = Lernbuero(name="first", start=datetime(2020,3,1,12,45).timestamp(), end=datetime(2020,3,1,13,30).timestamp(), kw=2)
# db.session.add(l1)
# db.session.add(l2)
# db.session.add(l3)
# db.session.commit()


@app.route('/')
@app.route('/api/v1/lb', methods=["GET", "POST", "DELETE"])
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
            lb = Lernbuero(**extract_info(content))
            db.session.add(lb)
            db.session.commit()
        except AssertionError:
            pass

    query = db.session.query(Lernbuero)
    return jsonify(pd.read_sql(query.statement, query.session.bind).groupby("kw").apply(lambda x: x.to_dict("records")).to_dict())


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
