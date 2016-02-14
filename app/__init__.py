from flask import Flask, request, jsonify, session
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

from firebase import firebase

from config import BaseConfig


app = Flask(__name__)
app.config.from_object(BaseConfig)

def make_json_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code
                            if isinstance(ex, HTTPException)
                            else 500)
    return response

for code in default_exceptions.iterkeys():
    app.error_handler_spec[None][code] = make_json_error

firebase = firebase.FirebaseApplication(app.config["FIREBASE"], None)

from . import routes
from . import cronjobs
