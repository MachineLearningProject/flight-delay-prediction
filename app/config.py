import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    ENV = os.environ.get("ENV", "dev")

    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    DEBUG = os.environ.get("DEBUG", True)
    FIREBASE = os.environ.get("FIREBASE", "https://flight-delay-predict.firebaseio.com")
    FIREBASE_CLEAN = os.environ.get("FIREBASE_CLEAN", "https://flight-delay-clean.firebaseio.com/")
    FIREBASE_AIRPORT_DATE = os.environ.get("FIREBASE_AIRPORT_DATE", "https://publicdata-airports.firebaseio.com")
    # in seconds
    CRONJOB_CYCLE = os.environ.get("CRONJOB_CYCLE", 3600)
    CRONJOB_CHECK = os.environ.get("CRONJOB_CHECK", 300)

    # Binarization config
    TIME_SLOTS = os.environ.get("TIME_SLOTS", 24)
    SLOT_HOUR_SIZE = 24 / TIME_SLOTS

