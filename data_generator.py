import random
import requests
import hashlib

PREDEFINED_CITIES = ["New York", "London", "Tokyo", "Delhi", "Sydney", "Paris", "Berlin", "Dubai", "Singapore", "Los Angeles", "Mumbai", "Toronto"]

def get_coordinates(location_name):
    # Free Geocoding API from Open-Meteo
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_name}&count=1"
    try:
        res = requests.get(url, timeout=5).json()
        if "results" in res and len(res["results"]) > 0:
            return res["results"][0]["latitude"], res["results"][0]["longitude"], res["results"][0]["name"]
    except Exception as e:
        print("Geocoding error:", e)
    return None, None, location_name

def fetch_weather_and_aqi(lat, lon):
    # Weather
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m"
    # AQI (US AQI)
    aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
    
    temp, hum, aqi = 25.0, 50.0, 50 # fallbacks
    try:
        w_res = requests.get(weather_url, timeout=5).json()
        if "current" in w_res:
            temp = w_res["current"]["temperature_2m"]
            hum = w_res["current"]["relative_humidity_2m"]
            
        a_res = requests.get(aqi_url, timeout=5).json()
        if "current" in a_res:
             aqi = a_res["current"]["us_aqi"]
    except Exception as e:
        print("API error:", e)
        
    return temp, hum, aqi

def generate_sensor_data(location='Global'):
    """
    Fetches real data from Open-Meteo API. If Global, picks a random city.
    """
    is_random = False
    actual_name = location
    
    if location.lower() == 'global':
        is_random = True
        actual_name = random.choice(PREDEFINED_CITIES)
        
    lat, lon, resolved_name = get_coordinates(actual_name)
    
    # If API fails or city not found, fallback to simulation logic
    if lat is None:
        seed = int(hashlib.md5(actual_name.encode('utf-8')).hexdigest(), 16) % 100
        random.seed()
        offset = (seed / 100.0) * 10 - 5
        
        temp = round(random.uniform(20.0, 45.0) + offset, 1)
        hum = round(random.uniform(20.0, 60.0) + offset, 1)
        aqi = random.randint(30, 250) + int(offset * 5)
    else:
        actual_name = resolved_name
        temp, hum, aqi = fetch_weather_and_aqi(lat, lon)
        if aqi is None: aqi = 50 # Safe fallback if AQI not available
        if hum is None: hum = 50
        if temp is None: temp = 25
        
    # pH is still simulated
    ph = round(random.uniform(6.5, 8.5) + random.uniform(-1, 1), 1)
    
    return {
        'location_name': actual_name,
        'is_random': is_random,
        'data': {
            'temperature': round(temp, 1),
            'humidity': round(hum, 1),
            'aqi': round(aqi),
            'ph': ph
        }
    }
