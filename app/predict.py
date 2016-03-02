from collections import defaultdict

import numpy as np
from datetime import datetime, timedelta
from dateutil.parser import parse
from sklearn import preprocessing
from sklearn import linear_model
from sklearn import cross_validation
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from firebase.firebase import FirebaseApplication

from . import app
from . import mapper
from . import utils
import DatasetCreation


class Predictor:

    def __init__(self):
        self.model = None
        metadata = mapper.get_clean_firebase().get_metadata()
        self.weather_metadata = metadata["weathers"]
        self.airports_metadata = metadata["airports"]

    def clean_weather_string(self, s):
        return str(s).replace("/", " and ").replace("  ", " ")

    def preprocess_weather(self):
        firebase_clean = mapper.get_clean_firebase()
        response = firebase_clean.get_all()
        weathers = {}
        for airport_code, date_status_dict in response.items():
            if type(date_status_dict) != dict or airport_code == "weathers":
                continue
            for date, event in date_status_dict.items():
                cleaned = self.clean_weather_string(event["weather"])
                weathers[cleaned] = True

        label_encoder = preprocessing.LabelEncoder()
        weathers = weathers.keys()
        label_encoder.fit(weathers)
        transformed = label_encoder.transform(weathers)
        weather_dict = {}
        for i in range(len(weathers)):
            weather_str = self.clean_weather_string(weathers[i])
            weather_dict[weather_str] = transformed[i]

        firebase_clean.firebase.put("/metadata", name="weathers", data=weather_dict)
        return weather_dict

    def preprocess_airports(self):
        firebase_clean = mapper.get_clean_firebase()
        all_clean = firebase_clean.get_all()

        transformed = DatasetCreation.writeCities_Airports(all_clean)
        firebase_clean.firebase.put("/metadata", name="airports", data=transformed)

    def get_weather_array(self, weather_str):
        cleaned = self.clean_weather_string(weather_str)
        arr = np.zeros(len(self.weather_metadata))
        if cleaned.strip() in self.weather_metadata:
            pos = self.weather_metadata[cleaned]
            arr[pos] = 1
        else:
            print "ERROR could not clean:", weather_str
        return arr

    def get_all_weathers_binarized(self, clean_data):
        weather_series = []
        for code, events in clean_data.items():
            for date, event in events.items():
                weather_series.append(self.get_weather_array(event["weather"]))

        return np.array(weather_series)

    def get_all_delays_binarized(self, clean_data):
        delay_series = []
        for code, events in clean_data.items():
            for date, event in events.items():
                delay_series.append(event["delay"])

        return np.array(delay_series)

    def get_all_airports_binarized(self, clean_data):

        transformed = DatasetCreation.writeCities_Airports(clean_data)
        airports_binarized = []
        for code, events in clean_data.items():

            for date, event in events.items():
                airports_binarized.append(DatasetCreation.getAirportBinarizedRepresentation(transformed, code))

        return np.array(airports_binarized)

    def get_all_wind_binarized(self, clean_data):

        windPair = []
        for code, events in clean_data.items():
            for date, event in events.items():
                windPair.append( (float(event["wind_x"]), float(event["wind_y"]), float(event["wind_magnitude"])) )

        return np.array(windPair)

    def binarize_time(self, datetime):
        slot = datetime.hour / app.config["SLOT_HOUR_SIZE"]
        row = np.zeros(app.config["TIME_SLOTS"])
        row[slot] = 1
        return row

    def get_all_times_binarized(self, clean_data):
        # we will experiment with having hour as features
        times_binarized = []
        for code, events in clean_data.items():
            for date, event in events.items():
                parsed_date = parse(date.split()[0])
                row = self.binarize_time(parsed_date)
                times_binarized.append(row)

        return np.array(times_binarized)

    def get_all_visibility(self, clean_data):

        visibility_array = []
        for code, events in clean_data.items():
            for date, event in events.items():
                visibility_array.append([event["visibility"]])

        return np.array(visibility_array)

    def get_all_temp(self, clean_data):

        temp_array = []
        for code, events in clean_data.items():
            for date, event in events.items():
                temp_array.append([event["temp"]])

        return np.array(temp_array)

    def merge_binarized(self, arrays):
        return np.concatenate(arrays, axis=1)

    def decide_model(self, datapoints, labels):

        classifiers = []
        classifiers.append( RandomForestClassifier(n_estimators=4) )
        classifiers.append( svm.SVC(probability=True) )
        classifiers.append( linear_model.Perceptron() )
        classifiers.append( linear_model.SGDClassifier(shuffle=True) )
        classifiers.append( KNeighborsClassifier() )

        best = 0
        model = None
        for clf in classifiers:

            p = np.random.permutation(len(labels))
            datapoints = datapoints[p]
            labels = labels[p]

            partition = datapoints.shape[0]/10
            Tr_data = datapoints[partition:]
            Tr_labels = labels[partition:]
            Te_data = datapoints[:partition]
            Te_labels = labels[:partition]

            fit = clf.fit(Tr_data, Tr_labels)
            '''
            scores = cross_val_score(fit, datapoints, labels, cv=10, n_jobs=-1)
            res = scores.mean()
            '''
            Te_pred = fit.predict(Te_data)

            cr =  classification_report(Te_labels, Te_pred)
            trues = self.get_precission_from_report(cr)[1]

            if trues > best:
                best = trues
                model = fit

        print type(model), best
        return model

    def get_precission_from_report(self, cr):

        splitted_report = cr.split('\n')
        splitted_report = [x for x in splitted_report if len(x.strip()) != 0]

        headers = splitted_report[0]
        content = splitted_report[1:-1]

        headers =  headers.split()
        content = np.array([x.split() for x in content])

        precision_false = content[:,1][0]
        precision_true = content[:,1][1]

        return (precision_false, precision_true)

    # airport_status must come from source_firebase
    def binarize_airport(self, airport_code, airport_status):
        cleaned_data = utils.get_clean_data(airport_status)
        weather_binarized = self.get_weather_array(cleaned_data["weather"])
        airport_binarized = DatasetCreation.getAirportBinarizedRepresentation(self.airports_metadata, airport_code)
        wind = [ cleaned_data["wind_x"], cleaned_data["wind_y"], cleaned_data["wind_magnitude"] ]
        temp = [cleaned_data["temp"] ]
        visibility = [ cleaned_data["visibility"] ]
        time_binarized = self.binarize_time(datetime.now())

        return np.concatenate((weather_binarized, wind, time_binarized, temp, visibility))

    def predict(self, airport_code):
        firebase_source = mapper.get_source_firebase()

        airport_status = firebase_source.get_airport(airport_code)
        airport_binarized = self.binarize_airport(airport_code, airport_status)
        return self.model.predict([airport_binarized])

    def predict_all(self):
        firebase_source = mapper.get_source_firebase()

        all_source = firebase_source.get_all()
        results = {}
        for airport_code, airport_status in all_source.items():
            airport_binarized = self.binarize_airport(airport_code, airport_status)
            results[airport_code] = bool(self.model.predict([airport_binarized])[0])

        return results

    def build_model(self):
        firebase_clean = mapper.get_clean_firebase()

        all_clean = firebase_clean.get_all()

        airports_binarized = self.get_all_airports_binarized(all_clean)
        weathers_binarized = self.get_all_weathers_binarized(all_clean)
        wind_binarized = self.get_all_wind_binarized(all_clean)
        times_binarized = self.get_all_times_binarized(all_clean)
        temp = self.get_all_temp(all_clean)
        visibility = self.get_all_visibility(all_clean)

        features = [weathers_binarized, wind_binarized, times_binarized, temp, visibility]
        datapoints = self.merge_binarized(features)

        labels = self.get_all_delays_binarized(all_clean)
        self.model = self.decide_model(datapoints, labels)

predictor = Predictor()