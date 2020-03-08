from src.defaultconfig import SQLALCHEMY_DATABASE_URI

from sqlalchemy import create_engine

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)

