from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="Althir",
    password="lernbuero_db_pw",
    hostname="Althir.mysql.pythonanywhere-services.com",
    databasename="Althir$default",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))


@app.route('/', methods=["GET", "POST"])
def render_template1():
    if request.method == "GET":
        return render_template("template1.html", comments=Comment.query.all())

    comment = Comment(content=request.form["contents"])
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('render_template1'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
