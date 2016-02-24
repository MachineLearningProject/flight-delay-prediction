from firebase.firebase import FirebaseApplication

from . import app


class Firebase:

    def __init__(self, url):
        self.firebase = FirebaseApplication(url, None)

    def get_all(self):
        response = self.firebase.get("/", None)
        del response["metadata"]
        return response

    def get_metadata(self):
        return self.firebase.get("/metadata", None)

    def get_airport(self, airport_code):
        return self.firebase.get("/"+airport_code, None)


def get_clean_firebase():
    return Firebase(app.config["FIREBASE_CLEAN"])

def get_source_firebase():
    return Firebase(app.config["FIREBASE_AIRPORT_DATE"])

def get_dump_firebase():
    return Firebase(app.config["FIREBASE"])
