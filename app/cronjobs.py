from datetime import datetime, timedelta
import threading
import time
import traceback

from dateutil import parser
from firebase.firebase import FirebaseApplication

from config import BaseConfig
from . import app
from . import firebase

class AirportDelayRetriever:

    def __init__(self):

        self.delta = timedelta(seconds=app.config["CRONJOB_CYCLE"])
        self.source_firebase = FirebaseApplication(app.config["FIREBASE_AIRPORT_DATE"], None)
        self.last_updated = parser.parse(firebase.get("/", "last_updated"))

    def get_flight_info_from_firebase(self):
        response = self.source_firebase.get("", None)
        updated = parser.parse(response["_updated"])

        if updated <= self.last_updated + self.delta:
            raise Exception("Not time to sync yet.")

        print "Syncing Airpot Delays from", updated.isoformat()
        self.last_updated = updated
        update_str = updated.isoformat()
        firebase.put("/", "last_updated", update_str)
        firebase_clean = FirebaseApplication(app.config["FIREBASE_CLEAN"], None)

        for airport_code, info in response.items():
            # this is not an airport :)
            if airport_code == "_updated": continue

            try:
                firebase.put(url="/"+airport_code, name=update_str, data=info)
                filtered_data = self.get_clean_data(info)
                firebase_clean.put(url="/"+airport_code, name=date, data=filtered_data)
            except Exception as e:
                print e


    def get_clean_data(self, data):
        if "weather" not in data or "weather" not in data["weather"]:
            print "EXCEPTION", data
            return None

        filtered_data = {
            "code" : data["IATA"],
            "city" : data["city"],
            "delay" : data["delay"],
            "state" : data["state"],
            "visibility" : data["weather"]["visibility"],
            "weather" : data["weather"]["weather"],
        }

        temp = data["weather"]["temp"]
        temp = temp[temp.index("(")+1:-3]
        try:
            filtered_data["temp"] = float(temp)
        except Exception as e:
            print "EXCEPTION: Could not parse temperature:", temp
            return None

        directions = {
            "North" :       [0, 1],
            "Northeast" :   [0.707, 0.707],
            "East" :        [1, 0],
            "Southeast" :   [0.707, -0.707],
            "South" :       [0, -1],
            "Southwest" :   [-0.707, -0.707],
            "West" :        [-1, 0],
            "Northwest" :   [-0.707, 0.707],
            "Variable" :    [0, 0]
        }
        wind = data["weather"]["wind"]
        at_index = wind.index(" at ")
        prev_wind = wind
        wind = wind[:at_index]

        if wind not in directions:
            print "EXCEPTION: No direction found", data["weather"]["wind"]
            return None

        direction = directions[wind]
        filtered_data["wind_x"] = direction[0]
        filtered_data["wind_y"] = direction[1]

        wind = data["weather"]["wind"]
        mph_index = wind.index("mph")
        wind_magnitude = wind[at_index+5:mph_index]
        try:
            wind_magnitude = float(wind_magnitude)
        except Exception as e:
            print "EXCEPTION: Could not parse wind:", wind
            return None

        filtered_data["wind_magnitude"] = wind_magnitude

        return filtered_data


    def clean_data(self):
        uncleaned = firebase.get("/", None)
        uncleaned = uncleaned or {}
        firebase_clean = FirebaseApplication(app.config["FIREBASE_CLEAN"], None)
        cleaned = firebase_clean.get("/", None)
        for airport_code, date_status_dict in uncleaned.items():
            if type(date_status_dict) != dict:
                print airport_code, date_status_dict
                continue
            for date, event in date_status_dict.items():
                if airport_code in cleaned and date in cleaned[airport_code]:
                    continue
                filtered_data = self.get_clean_data(event)
                try:
                    firebase_clean.put(url="/"+airport_code, name=date, data=filtered_data)
                    print "Cleaned", airport_code, date
                except Exception as e:
                    print "Could not clean", airport_code, date, event
                    print e

    def run(self):

        while True:
            try:
                self.get_flight_info_from_firebase()
            except Exception as e:
                print e
            else:
                print "Updated Info at", self.last_updated.isoformat()
            time.sleep(app.config["CRONJOB_CHECK"])
