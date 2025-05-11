# Voice Chatbot for Road Safety

A Flask-based web application that integrates voice commands to interact with a chatbot. The chatbot can provide real-time suggestions like nearby rest stops, weather conditions, and fatigue detection, all while ensuring safety during a road trip.

## Features
- Voice-enabled chatbot to provide driving suggestions
- Weather data integration based on location
- Fatigue detection and nearby rest stop suggestions
- Real-time API for accident-prone areas and weather updates
- Integration with AssemblyAI for voice transcription

## Project Structure

```bash
voice_chatbot/
├── app.py                   # Main Flask application
├── templates/
│   └── index.html           # Frontend HTML
├── static/
│   ├── css/
│   │   └── styles.css       # Styling for the frontend
│   └── js/
│       └── scripts.js       # JavaScript for frontend interaction
├── data/
│   └── rest_stops.json      # JSON file with rest stop data
├── utils/
│   ├── weather.py           # Weather data retrieval logic
│   ├── emergency.py         # Logic for emergency data and fatigue detection
│   └── fatigue.py           # Fatigue detection logic
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
