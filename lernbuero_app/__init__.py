from socket import gethostname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_claims

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    if 'live' not in gethostname():
        print("local settings")
        app.config.from_object("config.DevConfig")
        from flask_cors import CORS
        CORS(app)
    else:
        print("production settings")
        app.config.from_object("config.ProdConfig")

    db.init_app(app)
    jwt = JWTManager(app)

    with app.app_context():
        from lernbuero_app.lernbuero_lehrer import lehrer_routes
        app.register_blueprint(lehrer_routes.lehrer_bp)
        from lernbuero_app.auth import auth
        app.register_blueprint(auth.auth_bp)
        db.create_all()
        return app
