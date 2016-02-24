from flask import request, jsonify, session, g
import numpy as np
from DatasetCreation import ConstructDataset

from . import app
from . import firebase

from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from sklearn.cross_validation import cross_val_score


@app.route("/", methods=["GET"])
def index():
	response = firebase.get("/", None)
	response = response or {}

	datapoints, labels = ConstructDataset(response)
	print len(datapoints)
	print len(labels)

	#	print datapoints[ labels == True ]
	print datapoints[10]

	#enc = preprocessing.OneHotEncoder()
	#print enc.fit(datapoints)

	#clf = RandomForestClassifier(n_estimators=10, min_samples_split=1)
	#clf = clf.fit(datapoints, labels)

	#scores = cross_val_score(clf, datapoints, labels)
	#scores.mean()

	#clf = DecisionTreeClassifier(max_depth=None, min_samples_split=1, random_state=0)
	#scores = cross_val_score(clf, datapoints, labels)
	#scores.mean()

	return jsonify(response)