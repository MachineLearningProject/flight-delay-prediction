from flask import jsonify

from . import app
import mapper
import utils
from predict import predictor


@app.route("/", methods=["GET"])
def index():
    firebase_dump = mapper.get_dump_firebase()
    response = firebase_dump.get_all()
    response = response or {}
    return jsonify(response)

@app.route("/build", methods=["POST"])
def build_model():
    predictor.preprocess_airports()
    if not predictor.model:
        predictor.build_model()

    return jsonify({"message:" : "OK"})

@app.route("/predict", methods=["GET"])
def predict_all_delays():
    results = None
    try:
        results = predictor.predict_all()
    except Exception as e:
        return jsonify({"message" : e.message})
    return jsonify(results)

@app.route("/predict/<airport_code>", methods=["GET"])
def predict_delay(airport_code):
    firebase_source = mapper.get_source_firebase()
    airport_status = firebase_source.get_airport(airport_code)
    cleaned_data = utils.get_clean_data(airport_status)

    res = predictor.predict(airport_code)
    cleaned_data["prediction"] = bool(res[0])
    return jsonify(cleaned_data)

@app.route("/status", methods=["GET"])
def get_airport_statuses():
    firebase_source = mapper.get_source_firebase()
    airports = firebase_source.get_all()
    for airport_code, status in airports.items():
        if "status" in status:
            del status["status"]

    return jsonify(airports)
