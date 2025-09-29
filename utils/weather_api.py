import requests
from config import OPENWEATHER_API_KEY

def get_weather(lat, lon, api_key=OPENWEATHER_API_KEY):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    return {
        "temp": response['main']['temp'],
        "humidity": response['main']['humidity'], 
        "description": response['weather'][0]['description']
    }