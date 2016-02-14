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

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True

        thread.start()


    def get_flight_info_from_firebase(self):

        response = self.source_firebase.get("", None)
        updated = parser.parse(response["_updated"])

        if updated <= self.last_updated + self.delta:
            raise Exception("Not time to sync yet.")

        print "Syncing Airpot Delays from", updated.isoformat()
        self.last_updated = updated
        update_str = updated.isoformat()
        firebase.put("/", "last_updated", update_str)
        for airport_code, info in response.items():
            # this is not an airport :)
            if airport_code == "_updated": continue

            firebase.put(url="/"+airport_code, name=update_str, data=info)

    def run(self):

        while True:
            try:
                self.get_flight_info_from_firebase()
            except Exception as e:
                print e
            else:
                print "Updated Info at", self.last_updated.isoformat()
            time.sleep(app.config["CRONJOB_CYCLE"])

AirportDelayRetriever()
