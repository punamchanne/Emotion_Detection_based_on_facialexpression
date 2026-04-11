from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import numpy as np
import cv2
import pandas as pd
import base64
import os
from collections import Counter
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
    # keep users_collection as None; routes handle it

# --- ML Model Setup ---
model = None
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D

    def load_model():
        m = Sequential()
        m.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)))
        m.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        m.add(MaxPooling2D(pool_size=(2, 2)))
        m.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        m.add(MaxPooling2D(pool_size=(2, 2)))
        m.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        m.add(MaxPooling2D(pool_size=(2, 2)))
        m.add(Dropout(0.25))
        m.add(Flatten())
        m.add(Dense(1024, activation='relu'))
        m.add(Dropout(0.5))
        m.add(Dense(7, activation='softmax'))
        m.load_weights('model.h5')
        return m

    model = load_model()
    print("Model loaded successfully")
except Exception as e:
    print(f"WARNING: Could not load TensorFlow model: {e}")
    print("Running in DEMO mode with mock predictions.")

emotion_dict = {
    0: "Angry",
    1: "Disgusted",
    2: "Fearful",
    3: "Happy",
    4: "Neutral",
    5: "Sad",
    6: "Surprised",
}

def load_haarcascade():
    return cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

face_cascade = load_haarcascade()

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

@app.route('/predict', methods=['POST'])
def predict():
    """
    Optional: This is kept if you later want server-side prediction.
    Currently your React Dashboard uses face-api.js expressions, not this route.
    """
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = (request.json or {}).get('image')
        if not data:
            return jsonify({'emotion': 'Neutral'})

        header, encoded = data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        emotion = "Neutral"

        if model:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            emotion = "Neutral"
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                prediction = model.predict(cropped_img, verbose=0)
                max_index = int(np.argmax(prediction))
                emotion = emotion_dict[max_index]
                break
        else:
            import random
            emotions_pool = ["Happy", "Sad", "Angry", "Surprised", "Fearful", "Disgusted", "Neutral"]
            emotion = random.choice(emotions_pool)

        return jsonify({'emotion': emotion})

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'emotion': 'Neutral'})

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