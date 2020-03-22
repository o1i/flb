from datetime import datetime
from socket import gethostname
import sys

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import pandas as pd

sys.path.insert(0, '/home/Althir/flb')

from lernbuero_app.post_functions import post_verification, extract_info
from lernbuero_app.delete_functions import delete_verification

app = Flask(__name__)
if 'live' not in gethostname():
    print(gethostname())
    print("Local server settings")
    from flask_cors import CORS

    app.config.from_object('lernbuero_app.defaultconfig')
    CORS(app)
else:
    print("Server settings from envvar")
    app.config.from_envvar('SERVER_CONFIG')

db = SQLAlchemy(app)


if __name__ == '__main__':

    if 'live' not in gethostname():
        app.run(host="0.0.0.0", debug=True)
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