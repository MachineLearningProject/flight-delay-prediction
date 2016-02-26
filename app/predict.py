from collections import defaultdict

import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
from sklearn import cross_validation
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.cross_validation import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from firebase.firebase import FirebaseApplication

from . import mapper
from . import utils
import DatasetCreation


def clean_weather_string(s):
    return str(s).replace("/", " and ").replace("  ", " ")

def preprocess_weather():
    firebase_clean = mapper.get_clean_firebase()
    response = firebase_clean.get_all()
    weathers = {}
    for airport_code, date_status_dict in response.items():
        if type(date_status_dict) != dict or airport_code == "weathers":
            continue
        for date, event in date_status_dict.items():
            cleaned = clean_weather_string(event["weather"])
            weathers[cleaned] = True

    label_encoder = preprocessing.LabelEncoder()
    weathers = weathers.keys()
    label_encoder.fit(weathers)
    transformed = label_encoder.transform(weathers)
    weather_dict = {}
    for i in range(len(weathers)):
        weather_str = clean_weather_string(weathers[i])
        weather_dict[weather_str] = transformed[i]

    firebase_clean.firebase.put("/metadata", name="weathers", data=weather_dict)
    return weather_dict

def get_weather_array(weather_dict, weather_str):
    cleaned = clean_weather_string(weather_str)
    arr = np.zeros(len(weather_dict))
    if cleaned in weather_dict:
        pos = weather_dict[ cleaned]
        arr[pos] = 1
    else:
        print "ERROR could not clean:", weather_str
    return arr

def get_all_weathers_binarized(clean_data):
    firebase_clean = mapper.get_clean_firebase()
    weathers = firebase_clean.get_metadata()["weathers"]

    weather_series = []
    for code, events in clean_data.items():
        for date, event in events.items():
            weather_series.append(get_weather_array(weathers, event["weather"]))

    return np.array(weather_series)

def get_all_delays_binarized(clean_data):
    delay_series = []
    for code, events in clean_data.items():
        for date, event in events.items():
            delay_series.append(event["delay"])

    return np.array(delay_series)

def get_all_airports_binarized(clean_data):

    transformed = DatasetCreation.writeCities_Airports(clean_data)
    airports_binarized = []
    for code, events in clean_data.items():

        for date, event in events.items():
            airports_binarized.append(DatasetCreation.getAirportBinarizedRepresentation(transformed, code))

    return np.array(airports_binarized)

def get_all_wind_binarized(clean_data):

    windPair = []
    for code, events in clean_data.items():
        for date, event in events.items():
            windPair.append( [float(event["wind_x"]), float(event["wind_y"])] )

    return np.array(windPair)

def merge_binarized(arrays):
    return np.concatenate(arrays, axis=1)

def permute(datapoints, labels):

    p = np.random.permutation(len(labels))

    datapoints = np.array(datapoints)
    labels = np.array(labels)

    return (datapoints, labels)

def decide_model(datapoints, labels):

    classifiers = []
    classifiers.append( RandomForestClassifier(n_estimators=10, min_samples_split=1) )
    classifiers.append( DecisionTreeClassifier(max_depth=None, min_samples_split=1, random_state=0) )
    classifiers.append( linear_model.Perceptron() )
    #classifiers.append( linear_model.SGDClassifier() )
    #classifiers.append( KNeighborsClassifier() )

    best = 0
    model = None
    for clf in classifiers:
        fit = clf.fit(datapoints, labels)
        scores = cross_val_score(fit, datapoints, labels, cv=10, n_jobs=-1)
        res = scores.mean()

        if res > best:
            best = res
            model = fit

    print model, best
    return model

def predict(airport_code):
    firebase_source = mapper.get_source_firebase()
    firebase_clean = mapper.get_clean_firebase()

    all_clean = firebase_clean.get_all()

    airports_binarized = get_all_airports_binarized(all_clean)
    weathers_binarized = get_all_weathers_binarized(all_clean)
    wind_binarized = get_all_wind_binarized(all_clean)
    print "-----", airports_binarized.shape, weathers_binarized.shape, wind_binarized.shape

    features = [airports_binarized, weathers_binarized, wind_binarized]
    merged_binarized = merge_binarized(features)
    print merged_binarized.shape

    delays_binarized = get_all_delays_binarized(all_clean)
    print delays_binarized.shape

    datapoints, labels = permute(merged_binarized, delays_binarized)
    model = decide_model(datapoints, labels)
    #model = linear_model.Perceptron().fit(merged_binarized, delays_binarized)

    airport_status = firebase_source.get_airport(airport_code)
    cleaned_data = utils.get_clean_data(airport_status)
    weathers = firebase_clean.get_metadata()["weathers"]
    weather_binarized = get_weather_array(weathers, cleaned_data["weather"])
    transformed = DatasetCreation.writeCities_Airports(all_clean)
    airport_binarized = DatasetCreation.getAirportBinarizedRepresentation(transformed, airport_code)
    airport_binarized = np.concatenate((airport_binarized, weather_binarized))

    return model.predict([airport_binarized])
