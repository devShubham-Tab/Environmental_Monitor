from flask import Flask, jsonify, render_template, request
from data_generator import generate_sensor_data
import rules
import datetime
import os

app = Flask(__name__)

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
        'alerts': alerts
    }
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
