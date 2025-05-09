from flask import Flask
from dotenv import load_dotenv
import os
from config import mongo_client
from routes.auth_routes import auth_bp
from routes.speaker_routes import speaker_bp
from routes.booking_routes import booking_bp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Test MongoDB connection
try:
    mongo_client.admin.command('ping')
    print("MongoDB connection successful!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(speaker_bp, url_prefix='/api')
app.register_blueprint(booking_bp, url_prefix='/api')

@app.route('/')
def health_check():
    return "SpeakEasy API is running."

#if __name__ == '__main__':
#    app.run(debug=True) 

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
