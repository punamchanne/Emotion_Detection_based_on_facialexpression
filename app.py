from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import base64
import os
import traceback

from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
app = Flask(__name__)

# IMPORTANT: Allow React dev server (5173) with cookies/sessions
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]}},
)

app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

# IMPORTANT: Local dev uses HTTP, so cookies must NOT be Secure
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

# Optional (safe defaults)
app.config['SESSION_COOKIE_HTTPONLY'] = True

bcrypt = Bcrypt(app)

# --- Database Setup ---
users_collection = None
try:
    client = MongoClient(app.config['MONGO_URI'], serverSelectionTimeoutMS=5000)
    db = client.get_database('emotion_music_db')
    users_collection = db.users
    client.server_info()
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# --- Coffee Recommendations (Enhanced) ---
COFFEE_RECOMMENDATIONS = {
    "Happy": [
        {"name": "Strong Espresso", "brand": "Starbucks Espresso", "why": "To keep your energy high!"},
        {"name": "Sweet Caramel Coffee", "brand": "Costa Coffee", "why": "A sweet drink for a sweet mood."},
        {"name": "Vanilla Latte", "brand": "Blue Tokai", "why": "A classic sweet treat for you."}
    ],
    "Sad": [
        {"name": "Hot Mocha", "brand": "Starbucks Mocha", "why": "Chocolate and coffee to make you feel better."},
        {"name": "Creamy Cappuccino", "brand": "Bru Cappuccino", "why": "Warm and soothing for comfort."},
        {"name": "Hot Chocolate Coffee", "brand": "Homemade Style", "why": "The best drink to feel cozy."}
    ],
    "Angry": [
        {"name": "Iced Americano", "brand": "Starbucks Iced Coffee", "why": "Cool down with a cold drink."},
        {"name": "Black Coffee", "brand": "Nescafé Gold", "why": "To help you focus and stay calm."},
        {"name": "Cold Brew", "brand": "Blue Tokai", "why": "Very smooth and refreshing."}
    ],
    "Fearful": [
        {"name": "Decaf Latte", "brand": "Nescafé Decaf", "why": "Very gentle and calming."},
        {"name": "Warm Milk Coffee", "brand": "Classic Bru", "why": "Light and easy on your nerves."},
        {"name": "Hazelnut Coffee", "brand": "Artisan Blend", "why": "Smells good and helps you relax."}
    ],
    "Disgusted": [
        {"name": "Fresh Cappuccino", "brand": "Bru Mild", "why": "A light and fresh taste."},
        {"name": "Ginger Coffee", "brand": "Special Blend", "why": "Strong and fresh smell."},
        {"name": "Flat White", "brand": "Costa", "why": "Very soft and smooth."}
    ],
    "Neutral": [
        {"name": "Regular Coffee", "brand": "Nescafé Gold", "why": "A perfect drink for any time."},
        {"name": "Hazelnut Latte", "brand": "Starbucks", "why": "Adding a little flavor to your day."},
        {"name": "French Press", "brand": "Blue Tokai", "why": "Nice and simple coffee."}
    ],
    "Surprised": [
        {"name": "Sparkling Coffee", "brand": "Modern Cafe", "why": "Something new and exciting!"},
        {"name": "Nitro Cold Brew", "brand": "Starbucks Nitro", "why": "A fun and bubbly drink."},
        {"name": "Irish Coffee Style", "brand": "Specialty", "why": "A fun twist for a surprise!"}
    ],
}

# --- Routes ---

@app.route('/check-auth')
def check_auth():
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']})
    return jsonify({'authenticated': False}), 401

@app.route('/get-face')
def get_face():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_data = users_collection.find_one({'username': session['user']})
    if user_data and 'face_image' in user_data:
        return jsonify({'face_image': user_data['face_image']})
    return jsonify({'face_image': None})

@app.route('/')
def index():
    # If someone opens backend in browser, just show auth state (optional)
    if 'user' in session:
        return jsonify({'ok': True, 'user': session['user']})
    return jsonify({'ok': True, 'user': None})

@app.route('/login', methods=['POST'])
def login():
    # React sends JSON
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    try:
        if users_collection is None:
            return jsonify({'success': False, 'message': 'Database connection invalid'}), 500

        user = users_collection.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = username
            return jsonify({'success': True, 'user': username})

        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

    try:
        if users_collection is None:
            return jsonify({'success': False, 'message': 'Database connection invalid'}), 500

        if users_collection.find_one({'username': username}):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        face_image = data.get('face_image')  # Local storage or DB string
        
        users_collection.insert_one({
            'username': username, 
            'password': hashed_password,
            'face_image': face_image
        })

        return jsonify({'success': True, 'message': 'Account created'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/coffee', methods=['POST'])
def coffee():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    emotion = (request.json or {}).get('emotion', 'Neutral')
    recs = COFFEE_RECOMMENDATIONS.get(emotion, COFFEE_RECOMMENDATIONS["Neutral"])
    return jsonify({"emotion": emotion, "recommendations": recs})

if __name__ == '__main__':
    # Run on 5000 for backend
    app.run(debug=True, use_reloader=False, port=5000)