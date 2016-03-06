import numpy as np
import matplotlib.pyplot as plt

def get_clean_data(data):
    if "weather" not in data or "weather" not in data["weather"]:
        raise Exception("Weather no found in data")

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
        raise Exception("Could not parse temperature: %s" % temp)

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
        raise Exception("No direction found: %s" % data["weather"]["wind"])

    direction = directions[wind]
    filtered_data["wind_x"] = direction[0]
    filtered_data["wind_y"] = direction[1]

    wind = data["weather"]["wind"]
    mph_index = wind.index("mph")
    wind_magnitude = wind[at_index+5:mph_index]
    try:
        wind_magnitude = float(wind_magnitude)
    except Exception as e:
        raise Exception("Could not parse wind: %s" % wind)

    filtered_data["wind_magnitude"] = wind_magnitude

    '''
    filtered_data["reason"] = data["status"]["reason"]

    '''
    return filtered_data

def plot_classification_report(cr, title='Classification report ', cmap=plt.cm.Blues):

    lines = cr.split('\n')

    classes = []
    plotMat = []
    for line in lines[2 : (len(lines) - 3)]:
        
        lineSplit = line.split()
        nClasses = len(lineSplit)

        classes.append(lineSplit[0])
        classValues = [float(x) for x in lineSplit[1: nClasses - 1]]
        
        plotMat.append(classValues)

    plt.imshow(plotMat, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    x_tick_marks = np.arange(3)
    y_tick_marks = np.arange(len(classes))
    plt.xticks(x_tick_marks, ['precision', 'recall', 'f1-score'], rotation=45)
    plt.yticks(y_tick_marks, classes)
    plt.tight_layout()
    plt.ylabel('Classes')
    plt.xlabel('Measures')
    plt.show()
    
    return classes

def plot_confusion_matrix(cm, classes, title='Confusion matrix', cmap=plt.cm.Blues):

    print cm
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

    plt.show()