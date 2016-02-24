from datetime import datetime, timedelta
import threading
import time
import traceback

from dateutil import parser
from firebase.firebase import FirebaseApplication

from config import BaseConfig
import utils
import mapper
from . import app


class AirportDelayRetriever:

    def __init__(self):

        self.delta = timedelta(seconds=app.config["CRONJOB_CYCLE"])
        self.source_firebase = FirebaseApplication(app.config["FIREBASE_AIRPORT_DATE"], None)
        self.dump_firebase = mapper.get_dump_firebase()
        self.last_updated = parser.parse(self.dump_firebase.firebase.get("/", "last_updated"))

    def get_flight_info_from_firebase(self):
        response = self.source_firebase.get("", None)
        updated = parser.parse(response["_updated"])

        if updated <= self.last_updated + self.delta:
            raise Exception("Not time to sync yet.")

        print "Syncing Airpot Delays from", updated.isoformat()
        self.last_updated = updated
        update_str = updated.isoformat()
        firebase_clean = FirebaseApplication(app.config["FIREBASE_CLEAN"], None)

        for airport_code, info in response.items():
            # this is not an airport :)
            if airport_code == "_updated": continue

            try:
                self.dump_firebase.firebase.put(url="/"+airport_code, name=update_str, data=info)
                filtered_data = utils.get_clean_data(info)
                firebase_clean.put(url="/"+airport_code, name=update_str, data=filtered_data)
            except Exception as e:
                print "Something failed", e

        self.dump_firebase.firebase.put("/", "last_updated", update_str)


    def clean_data(self):
        uncleaned = self.dump_firebase.get_all()
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
                filtered_data = utils.get_clean_data(event)
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
