import requests

API_KEY = "dc6570fdefd02dcceb5465a24a89af9e"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(lat, lon):
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric"
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code != 200 or "weather" not in data:
            return {
                "success": False,
                "message": "Sorry, I couldn't fetch weather info at the moment."
            }

        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        city = data.get("name", "Unknown Location")

        return {
            "success": True,
            "message": f"🌤️ Weather in {city}: {weather}, Temperature: {temp}°C",
            "city": city,
            "temperature": temp,
            "description": weather
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching weather: {str(e)}"
        }
