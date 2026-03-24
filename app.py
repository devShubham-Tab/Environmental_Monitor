from flask import Flask, jsonify, render_template, request
from data_generator import generate_sensor_data
import rules
import datetime
import os

app = Flask(__name__)

# In-memory storage for historical data (for graphical analysis)
MAX_HISTORY = 20
histories = {}

def get_history(location):
    if location not in histories:
        histories[location] = {
            'timestamps': [],
            'temperature': [],
            'humidity': [],
            'aqi': [],
            'ph': []
        }
    return histories[location]

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    location = request.args.get('location', 'Global')
    
    # Generate new sensor data (real API calls)
    payload = generate_sensor_data(location)
    current_data = payload['data']
    actual_location = payload['location_name']
    is_random = payload['is_random']
    
    # Evaluate thresholds
    statuses = rules.evaluate_all(current_data)
    
    # Update history for the ACTUALLY resolved location
    history = get_history(actual_location)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    history['timestamps'].append(now)
    history['temperature'].append(current_data['temperature'])
    history['humidity'].append(current_data['humidity'])
    history['aqi'].append(current_data['aqi'])
    history['ph'].append(current_data['ph'])
    
    # Keep only the last MAX_HISTORY entries
    if len(history['timestamps']) > MAX_HISTORY:
        for key in history:
            history[key].pop(0)
            
    # Compile messages based on statuses
    alerts = []
    if statuses['temperature'] == 'danger':
        alerts.append("CRITICAL: Heatwave conditions! Extreme temperature detected.")
    elif statuses['temperature'] == 'warning':
        alerts.append("WARNING: Temperature is rising above safe limits.")
        
    if statuses['aqi'] == 'danger':
        alerts.append("CRITICAL: Hazardous Air Quality! Avoid outdoor activities.")
    elif statuses['aqi'] == 'warning':
        alerts.append("WARNING: Moderate Air Quality. Sensitive groups should limit outdoor exertion.")
        
    if statuses['humidity'] == 'danger':
        alerts.append("CRITICAL: Extreme humidity levels detected.")
        
    if statuses['ph'] == 'danger':
        alerts.append("CRITICAL: Severe water pH abnormality detected! High risk of contamination.")
        
    if not alerts:
        alerts.append("All environmental parameters are within safe limits.")

    response = {
        'location_name': actual_location,
        'is_random': is_random,
        'current': current_data,
        'status': statuses,
        'history': history,
        'alerts': alerts
    }
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
