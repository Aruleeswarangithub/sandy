from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from utils.weather import get_weather
from utils.fatigue import get_fatigue_alert
from utils.emergency_sms import send_emergency_sms
import json
import logging
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load rest stops data
try:
    with open('data/rest_stops.json', 'r') as f:
        rest_stops_data = json.load(f)
except Exception as e:
    logging.error(f"Failed to load rest_stops.json: {e}")
    rest_stops_data = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()
    lat = data.get('lat')
    lng = data.get('lng')

    logging.info(f"Received message: {message}, lat: {lat}, lng: {lng}")

    if not message:
        return jsonify({'response': "❓ I didn't catch that. Can you please rephrase?"})

    if lat is None or lng is None:
        return jsonify({'response': "⚠️ Location missing. Please allow location access."})

    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return jsonify({'response': "⚠️ Invalid location format. Please try again."})

    # Handle weather queries
    if "weather" in message:
        weather = get_weather(lat, lng)
        return jsonify({'response': weather['message'] if isinstance(weather, dict) else str(weather)})

    # Handle fatigue detection
    elif any(keyword in message for keyword in ["fatigue", "tired", "sleepy"]):
        result = get_fatigue_alert(lat, lng)
        response = {'response': result['message']}
        if result['status'] == 'fatigue' and result.get('options'):
            response['buttons'] = result['options']
        return jsonify(response)

    # Handle emergency
    elif any(keyword in message for keyword in ["emergency", "help me", "sos"]):
        sms_result = send_emergency_sms(lat, lng)
        return jsonify({'response': f"🚨 Emergency SMS sent!\n📩 {sms_result}"})

    # Handle place categories (like nearest ATM, mechanic, etc.)
    elif any(keyword in message for keyword in ["nearest", "show", "find"]):
        # Define synonyms for categories
        category_synonyms = {
            "fuel": ["fuel", "petrol", "gas"],
            "cafe": ["cafe", "coffee"],
            "hotel": ["hotel", "lodge"],
            "restaurant": ["restaurant", "food"],
            "toilet": ["toilet", "washroom", "restroom"],
            "rest": ["rest", "rest area"],
            "hospital": ["hospital", "clinic"],
            "service": ["service", "service center"],
            "atm": ["atm", "cash"],
            "mechanic": ["mechanic", "repair"],
            "parking": ["parking", "car park"],
            "charging": ["charging", "ev", "ev charging", "charging station"]
        }

        # Flatten keyword list and find match from message
        matched_category = None
        for key, synonyms in category_synonyms.items():
            if any(re.search(rf'\b{re.escape(word)}\b', message) for word in synonyms):
                matched_category = key
                break

        if matched_category:
            matched_places = []
            for place in rest_stops_data:
                category = place.get('category', '').lower().strip()
                name = place.get('name', '').strip()
                location = place.get('location', '').strip()
                link = place.get('link', '').strip()

                # Match category string loosely (to catch "ev charging", "restroom", etc.)
                if matched_category in category and name and location and link:
                    matched_places.append({
                        "name": name,
                        "location": location,
                        "link": link,
                        "category": category
                    })

            if matched_places:
                return jsonify({
                    'response': f"📍 Nearby {matched_category.title()} Places:",
                    'places': matched_places[:5],  # Limit to top 5 results
                    'category': matched_category
                })
            else:
                return jsonify({'response': f"❌ No nearby {matched_category.title()} places found."})
        else:
            return jsonify({'response': "❓ Please mention a specific category like ATM, restroom, charging station, etc."})

    # Help guide
    elif "help" in message:
        return jsonify({'response': (
            "🤖 You can ask me:\n"
            "- What's the weather like?\n"
            "- Am I tired?\n"
            "- Show nearest cafe/hotel/fuel\n"
            "- Send emergency message\n"
        )})

    # Default fallback
    else:
        return jsonify({'response': f"🤔 I heard: '{message}'. Try asking about weather, rest stops, or fatigue."})

@app.route('/api/weather/<lat>/<lon>')
def weather(lat, lon):
    try:
        result = get_weather(float(lat), float(lon))
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in /api/weather: {e}")
        return jsonify({'error': 'Failed to fetch weather data'}), 500

@app.route("/api/sos", methods=["POST"])
def emergency_sos():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")

    if not lat or not lon:
        return jsonify({"success": False, "message": "Latitude and longitude required"}), 400

    try:
        result = send_emergency_sms(float(lat), float(lon))
        return jsonify({"success": True, "message": result})
    except Exception as e:
        logging.error(f"Emergency SMS failed: {e}")
        return jsonify({"success": False, "message": "Failed to send emergency SMS"}), 500

if __name__ == '__main__':
    app.run(debug=True)
