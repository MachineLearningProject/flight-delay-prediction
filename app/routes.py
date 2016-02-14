from flask import request, jsonify, session, g

from . import app
from . import firebase

@app.route("/", methods=["GET"])
def index():
    response = firebase.get("/", None)
    response = response or {}
    return jsonify(response)