from flask import Flask, request, jsonify, render_template
from twilio.rest import Client
import os

app = Flask(__name__)

# Load Twilio credentials from Render environment variables
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# OPTIONAL: Debug logging (REMOVE after verifying)
print("✅ TWILIO_ACCOUNT_SID:", ACCOUNT_SID)
print("✅ TWILIO_AUTH_TOKEN:", AUTH_TOKEN)

# Twilio settings
FROM_NUMBER = "+19787979973"  # Your Twilio number
TO_NUMBERS = ["+919361468491", "+918807561446"]  # Recipient numbers

def send_emergency_sms(lat, lon):
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        location_link = f"https://maps.google.com/?q={lat},{lon}"
        message_body = f"🚨 Emergency! Please help! Location: {location_link}"

        for number in TO_NUMBERS:
            message = client.messages.create(
                body=message_body,
                from_=FROM_NUMBER,
                to=number
            )
            print(f"✅ SMS sent to {number}, SID: {message.sid}")

        return "🚨 Emergency SMS sent successfully."
    except Exception as e:
        print(f"❌ Error sending SMS: {str(e)}")
        return f"❌ Failed to send emergency SMS: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')  # Make sure templates/index.html exists

@app.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    if not lat or not lon:
        return jsonify({"status": "❌ Latitude or longitude missing."}), 400

    result = send_emergency_sms(lat, lon)
    return jsonify({"status": result})

if __name__ == '__main__':
    app.run(debug=True)
