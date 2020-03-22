from socket import gethostname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

from .lernbuero_lehrer import lehrer_routes


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    if 'live' not in gethostname():
        from flask_cors import CORS
        CORS(app)
        app.config.from_object("config.DevConfig")
    else:
        app.config.from_object("config.ProdConfig")

    db.init_app(app)

    with app.app_context():
        from lernbuero_app.lernbuero_lehrer import lehrer_routes
        app.register_blueprint(lehrer_routes.lehrer_bp)
        db.create_all()
        return app
