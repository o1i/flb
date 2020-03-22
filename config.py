import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME")
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get("SQLALCHEMY_POOL_RECYCLE"))
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")


class DevConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI")


class ProdConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("PROD_DATABASE_URI")
