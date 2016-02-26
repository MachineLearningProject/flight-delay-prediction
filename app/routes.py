from flask import jsonify

from . import app
import mapper
import utils
import predict


@app.route("/", methods=["GET"])
def index():
    firebase_dump = mapper.get_dump_firebase()
    response = firebase_dump.get_all()
    response = response or {}
    return jsonify(response)

@app.route("/predict/<airport_code>", methods=["GET"])
def predict_delay(airport_code):
    firebase_source = mapper.get_source_firebase()
    airport_status = firebase_source.get_airport(airport_code)
    cleaned_data = utils.get_clean_data(airport_status)

    res = predict.predict(airport_code)
    cleaned_data["prediction"] = bool(res[0])
    return jsonify(cleaned_data)
