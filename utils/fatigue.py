from apscheduler.schedulers.background import BackgroundScheduler
from geopy.distance import geodesic
import json
import os
import time

# Load rest stops data
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'rest_stops.json')

def load_rest_stops():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def get_fatigue_alert(lat, lon, heart_rate=None, fatigue_level=None):
    try:
        # Mock fatigue logic
        if heart_rate is not None and heart_rate < 60:
            tired = True
        elif fatigue_level is not None and fatigue_level >= 7:
            tired = True
        else:
            tired = False

        if not tired:
            return {
                "status": "alert",
                "message": "✅ You seem alert. Keep driving safely.",
                "options": []
            }

        # If tired, find nearest rest stop
        rest_stops = load_rest_stops()
        current_location = (lat, lon)
        nearby = []

        for stop in rest_stops:
            stop_location = (stop["lat"], stop["lon"])
            distance = geodesic(current_location, stop_location).km
            if distance <= 20:
                nearby.append((distance, stop))

        if not nearby:
            return {
                "status": "fatigue",
                "message": "😴 Fatigue detected! No rest stops within 20 km. Please pull over safely.",
                "options": []
            }

        nearby.sort()
        nearest = nearby[0][1]

        # Extract rest stop types for buttons
        options = list({stop['type'] for _, stop in nearby[:5]})  # Top 5 closest
        return {
            "status": "fatigue",
            "message": f"😴 Fatigue Alert: You seem tired.\nNearest Rest Stop: {nearest['name']} - {nearby[0][0]:.1f} km away.\nWould you like to stop at a nearby location?",
            "options": options
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking fatigue: {str(e)}",
            "options": []
        }

# Scheduler function
def check_fatigue_periodically():
    lat = 28.6139  # Mock location
    lon = 77.2090
    heart_rate = 55  # Simulated value
    result = get_fatigue_alert(lat, lon, heart_rate=heart_rate)
    print("[Fatigue Monitor]", result["message"])
    if result["options"]:
        print("Available rest stops:", result["options"])

# Set up the scheduler to run the check every 2 minutes
def start_fatigue_monitor():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_fatigue_periodically, trigger="interval", minutes=2)
    scheduler.start()

# Keep the scheduler running
if __name__ == "__main__":
    start_fatigue_monitor()

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        pass
