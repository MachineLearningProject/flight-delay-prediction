from firebase.firebase import FirebaseApplication

from . import app


class Firebase:

    def __init__(self, url):
        self.firebase = FirebaseApplication(url, None)

    def get_all(self):
        response = self.firebase.get("/", None)
        if "metadata" in response:
            del response["metadata"]
        if "last_updated" in response:
            del response["last_updated"]
        if "_updated" in response:
            del response["_updated"]
        if "_credits" in response:
            del response["_credits"]
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
