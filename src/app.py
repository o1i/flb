from datetime import datetime
from socket import gethostname
import sys

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import pandas as pd

sys.path.insert(0, '/home/Althir/flb')

from src.post_functions import post_verification, extract_info
from src.delete_functions import delete_verification

app = Flask(__name__)
if 'live' not in gethostname():
    print(gethostname())
    print("Local server settings")
    from flask_cors import CORS

    app.config.from_object('src.defaultconfig')
    CORS(app)
else:
    print("Server settings from envvar")
    app.config.from_envvar('SERVER_CONFIG')

db = SQLAlchemy(app)


if __name__ == '__main__':

    if 'live' not in gethostname():
        app.run(host="0.0.0.0", debug=True)
