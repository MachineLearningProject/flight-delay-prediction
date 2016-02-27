
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

    return filtered_data
