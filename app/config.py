import os
from datetime import timedelta
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    DEBUG = os.environ.get("DEBUG", True)
