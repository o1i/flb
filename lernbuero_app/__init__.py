import logging
from socket import gethostname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    if 'live' not in gethostname():
        print("local settings")
        logger.info("local settings")
        app.config.from_object("config.DevConfig")
        from flask_cors import CORS
        CORS(app)
    else:
        logger.info("production settings")
        app.config.from_object("config.ProdConfig")

    logging.basicConfig(filename=app.config["LOG_PATH"], level=app.config["LOG_LEVEL"])
    db.init_app(app)

    jwt = JWTManager(app)
    # from lernbuero_app.auth.auth import add_claims_to_access_token
    # jwt.user_claims_loader(add_claims_to_access_token)

    with app.app_context():
        from lernbuero_app.lernbuero_ap import ap_routes
        app.register_blueprint(ap_routes.ap_bp)
        from lernbuero_app.lernbuero_lehrer import lp_routes
        app.register_blueprint(lp_routes.lp_bp)
        from lernbuero_app.lernbuero_sus import sus_routes
        app.register_blueprint(sus_routes.sus_bp)
        from lernbuero_app.auth import auth
        app.register_blueprint(auth.auth_bp)
        db.create_all()
        logger.info("Initialisation done")
        return app
