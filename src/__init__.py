from datetime import datetime
from socket import gethostname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    if 'live' not in gethostname():
        app.config.from_object("config.DevConfig")
    else:
        app.config.from_object("config.ProdConfig")

    db.init_app(app)

    with app.app_context():
        from . import routes
        from .models import Lernbuero

        if 'live' not in gethostname():
            from flask_cors import CORS
            CORS(app)
            db.create_all()
            l1 = Lernbuero(name="first", start=datetime(2020, 3, 1, 12).timestamp(),
                           end=datetime(2020, 3, 1, 12, 45).timestamp(), kw=1)
            l2 = Lernbuero(name="first", start=datetime(2020, 3, 1, 12, 45).timestamp(),
                           end=datetime(2020, 3, 1, 13, 30).timestamp(), kw=1)
            l3 = Lernbuero(name="first", start=datetime(2020, 3, 1, 12, 45).timestamp(),
                           end=datetime(2020, 3, 1, 13, 30).timestamp(), kw=2)
            db.session.add(l1)
            db.session.add(l2)
            db.session.add(l3)
            db.session.commit()
        return app
