from collections import defaultdict

import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
from sklearn import cross_validation
from firebase.firebase import FirebaseApplication

from . import mapper
from . import utils

def clean_weather_string(s):
    return str(s).replace("/", " and ").replace("  ", " ")

def preprocess_weather():
    firebase_clean = FirebaseApplication(app.config["FIREBASE_CLEAN"], None)

    response = firebase_clean.get("/", None)
    weathers = {}
    for airport_code, date_status_dict in response.items():
        if type(date_status_dict) != dict or airport_code == "weathers":
            continue
        for date, event in date_status_dict.items():
            weathers[event["weather"]] = True

    label_encoder = preprocessing.LabelEncoder()
    weathers = weathers.keys()
    label_encoder.fit(weathers)
    transformed = label_encoder.transform(weathers)
    weather_dict = {}
    for i in range(len(weathers)):
        weather_str = clean_weather_string(weathers[i])
        weather_dict[weather_str] = transformed[i]

    firebase_clean.put("/metadata", name="weathers", data=weather_dict)
    return weather_dict

def get_weather_array(weather_dict, weather_str):
    cleaned = clean_weather_string(weather_str)
    arr = np.zeros(len(weather_dict))
    if cleaned in weather_dict:
        pos = weather_dict[cleaned]
        arr[pos] = 1
    else:
        print "ERROR could not clean:", weather_str
    return arr

def predict_with_weather(airport_code):
    firebase_source = mapper.get_source_firebase()
    firebase_clean = mapper.get_clean_firebase()
    weathers = firebase_clean.get_metadata()["weathers"]

    airport_status = firebase_source.get_airport(airport_code)
    cleaned_data = utils.get_clean_data(airport_status)
    weather = get_weather_array(weathers, cleaned_data["weather"])
    all = firebase_clean.get_all()

    weather_series = []
    delay_series = []
    for code, events in all.items():
        for date, event in events.items():
            weather_series.append(get_weather_array(weathers, event["weather"]))
            delay_series.append(event["delay"])

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(
                    weather_series, delay_series, test_size=0.4, random_state=0)

    model = linear_model.Perceptron().fit(X_train, y_train)

    return model.predict([weather])
