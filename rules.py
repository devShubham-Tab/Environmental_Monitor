def evaluate_temperature(temp):
    if temp < 35:
        return 'safe'
    elif 35 <= temp <= 45:
        return 'warning'
    else:
        return 'danger'

def evaluate_aqi(aqi):
    if aqi <= 100:
        return 'safe' # Good
    elif 100 < aqi <= 200:
        return 'warning' # Moderate
    else:
        return 'danger' # Hazardous

def evaluate_humidity(hum):
    if 30 <= hum <= 50:
        return 'safe'
    elif 20 <= hum < 30 or 50 < hum <= 60:
        return 'warning'
    else:
        return 'danger'

def evaluate_ph(ph):
    if 6.5 <= ph <= 8.5:
        return 'safe'
    elif 5.5 <= ph < 6.5 or 8.5 < ph <= 9.5:
        return 'warning'
    else:
        return 'danger'

def evaluate_all(data):
    return {
        'temperature': evaluate_temperature(data['temperature']),
        'humidity': evaluate_humidity(data['humidity']),
        'aqi': evaluate_aqi(data['aqi']),
        'ph': evaluate_ph(data['ph'])
    }
