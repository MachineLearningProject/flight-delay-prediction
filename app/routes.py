from flask import request, jsonify, session, g

from . import app

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message" : "hi"})
