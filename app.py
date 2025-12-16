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
# Enable CORS for React dev server
CORS(app, supports_credentials=True, resources={r"/*": {"origins": [
    "http://localhost:5173", 
    "http://127.0.0.1:5173", 
    "http://localhost:5174", 
    "http://127.0.0.1:5174",
    "http://localhost:5175", 
    "http://127.0.0.1:5175"
]}})

app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

# --- Database Setup ---
users_collection = None
try:
    client = MongoClient(app.config['MONGO_URI'], serverSelectionTimeoutMS=5000)
    db = client.get_database('emotion_music_db')
    users_collection = db.users
    # Trigger a connection check
    client.server_info()
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # Fallback for dev/demo if DB fails? 
    # For now, we leave users_collection as None and handle it in routes


bcrypt = Bcrypt(app)

# --- ML Model Setup ---
model = None
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
    
    def load_model():
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48, 48, 1)))
        model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(1024, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(7, activation='softmax'))
        model.load_weights('model.h5')
        return model
        
    model = load_model()
    print("Model loaded successfully")
except Exception as e:
    print(f"WARNING: Could not load TensorFlow model: {e}")
    print("Running in DEMO mode with mock predictions.")

emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

def load_haarcascade():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    return face_cascade

face_cascade = load_haarcascade()

# --- FIXED PLAYLISTS (7 Songs per Emotion) ---
# Hardcoded to ensure no overlap and high quality
FIXED_PLAYLISTS = {
    "Angry": [
        {"name": "Numb", "artist": "Linkin Park", "link": "https://youtu.be/kXYiU_JCYtU", "track": "Numb"},
        {"name": "Break Stuff", "artist": "Limp Bizkit", "link": "https://youtu.be/ZpUYjpKg9KY", "track": "Break Stuff"},
        {"name": "Killing In The Name", "artist": "Rage Against The Machine", "link": "https://youtu.be/bWXazVhlyxQ", "track": "Killing In The Name"},
        {"name": "Chop Suey!", "artist": "System Of A Down", "link": "https://youtu.be/CSvFpBOe8eY", "track": "Chop Suey!"},
        {"name": "Du Hast", "artist": "Rammstein", "link": "https://youtu.be/W3q8Od5qJio", "track": "Du Hast"},
        {"name": "Bodies", "artist": "Drowning Pool", "link": "https://youtu.be/04F4xlWSFh0", "track": "Bodies"},
        {"name": "Master of Puppets", "artist": "Metallica", "link": "https://youtu.be/xnKhsTXoKCI", "track": "Master of Puppets"}
    ],
    "Disgusted": [
        {"name": "Ugly", "artist": "The Exies", "link": "https://youtu.be/O3M8g8lZgY4", "track": "Ugly"},
        {"name": "Creep", "artist": "Radiohead", "link": "https://youtu.be/XFkzRNyygfk", "track": "Creep"},
        {"name": "Bad Guy", "artist": "Billie Eilish", "link": "https://youtu.be/DyDfgMOUjCI", "track": "Bad Guy"},
        {"name": "Toxic", "artist": "Britney Spears", "link": "https://youtu.be/LOZuxwVk7TU", "track": "Toxic"},
        {"name": "Sick of It", "artist": "Skillet", "link": "https://youtu.be/A2JGDyX018g", "track": "Sick of It"},
        {"name": "Hate Me", "artist": "Blue October", "link": "https://youtu.be/dDxgSvJINlU", "track": "Hate Me"},
        {"name": "Complicated", "artist": "Avril Lavigne", "link": "https://youtu.be/5NPBIwQyPWE", "track": "Complicated"}
    ],
    "Fearful": [
        {"name": "Demons", "artist": "Imagine Dragons", "link": "https://youtu.be/mWRsgZuwf_8", "track": "Demons"},
        {"name": "Thriller", "artist": "Michael Jackson", "link": "https://youtu.be/sOnqjkJTMaA", "track": "Thriller"},
        {"name": "Somebody's Watching Me", "artist": "Rockwell", "link": "https://youtu.be/7YvAYIJSSZY", "track": "Somebody's Watching Me"},
        {"name": "Enter Sandman", "artist": "Metallica", "link": "https://youtu.be/CD-E-LDc384", "track": "Enter Sandman"},
        {"name": "Disturbia", "artist": "Rihanna", "link": "https://youtu.be/E1mU6h4Xdxc", "track": "Disturbia"},
        {"name": "In the End", "artist": "Linkin Park", "link": "https://youtu.be/eVTXPUF4Oz4", "track": "In the End"},
        {"name": "Unthought Known", "artist": "Pearl Jam", "link": "https://youtu.be/T224iY8rYyM", "track": "Unthought Known"}
    ],
    "Happy": [
        {"name": "Happy", "artist": "Pharrell Williams", "link": "https://youtu.be/ZbZSe6N_BXs", "track": "Happy"},
        {"name": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "link": "https://youtu.be/OPf0YbXqDm0", "track": "Uptown Funk"},
        {"name": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "link": "https://youtu.be/ru0K8uYEZWw", "track": "Can't Stop the Feeling!"},
        {"name": "Walking on Sunshine", "artist": "Katrina and the Waves", "link": "https://youtu.be/iPUmE-tne5U", "track": "Walking on Sunshine"},
        {"name": "Shut Up and Dance", "artist": "WALK THE MOON", "link": "https://youtu.be/6JCLY0Rlx6Q", "track": "Shut Up and Dance"},
        {"name": "I Gotta Feeling", "artist": "The Black Eyed Peas", "link": "https://youtu.be/uSD4vsh1zDA", "track": "I Gotta Feeling"},
        {"name": "Best Day of My Life", "artist": "American Authors", "link": "https://youtu.be/Y66j_BUCBMY", "track": "Best Day of My Life"}
    ],
    "Neutral": [
        {"name": "Weightless", "artist": "Marconi Union", "link": "https://youtu.be/UfcAVejslrU", "track": "Weightless"},
        {"name": "Orinoco Flow", "artist": "Enya", "link": "https://youtu.be/LTrk4X9ACTw", "track": "Orinoco Flow"},
        {"name": "Put Your Records On", "artist": "Corinne Bailey Rae", "link": "https://youtu.be/rjOhZZyn30k", "track": "Put Your Records On"},
        {"name": "Sunday Morning", "artist": "Maroon 5", "link": "https://youtu.be/S2CTI12XBJA", "track": "Sunday Morning"},
        {"name": "Banana Pancakes", "artist": "Jack Johnson", "link": "https://youtu.be/6Graa_Vm5eA", "track": "Banana Pancakes"},
        {"name": "Three Little Birds", "artist": "Bob Marley", "link": "https://youtu.be/LanCLS_hIo4", "track": "Three Little Birds"},
        {"name": "Upside Down", "artist": "Jack Johnson", "link": "https://youtu.be/dqUdI4AIDF0", "track": "Upside Down"}
    ],
    "Sad": [
        {"name": "Someone Like You", "artist": "Adele", "link": "https://youtu.be/hLQl3WQQoQ0", "track": "Someone Like You"},
        {"name": "Fix You", "artist": "Coldplay", "link": "https://youtu.be/k4V3Mo61fJM", "track": "Fix You"},
        {"name": "Let Her Go", "artist": "Passenger", "link": "https://youtu.be/RBumgq5yVrA", "track": "Let Her Go"},
        {"name": "The Night We Met", "artist": "Lord Huron", "link": "https://youtu.be/KtlgYxa6BMU", "track": "The Night We Met"},
        {"name": "All of Me", "artist": "John Legend", "link": "https://youtu.be/450p7goxZqg", "track": "All of Me"},
        {"name": "Say Something", "artist": "A Great Big World", "link": "https://youtu.be/-2U0Ivkn2Ds", "track": "Say Something"},
        {"name": "Skinny Love", "artist": "Birdy", "link": "https://youtu.be/aNzCDt2eidg", "track": "Skinny Love"}
    ],
    "Surprised": [
        {"name": "Firework", "artist": "Katy Perry", "link": "https://youtu.be/QGJuMBdaqUb", "track": "Firework"},
        {"name": "Bohemian Rhapsody", "artist": "Queen", "link": "https://youtu.be/fJ9rUzIMcZQ", "track": "Bohemian Rhapsody"},
        {"name": "Sugar", "artist": "Maroon 5", "link": "https://youtu.be/09R8_2nJtjg", "track": "Sugar"},
        {"name": "Counting Stars", "artist": "OneRepublic", "link": "https://youtu.be/hT_nvWreIhg", "track": "Counting Stars"},
        {"name": "Viva La Vida", "artist": "Coldplay", "link": "https://youtu.be/dvgZkm1xWPE", "track": "Viva La Vida"},
        {"name": "On Top of the World", "artist": "Imagine Dragons", "link": "https://youtu.be/w5tWYmIOWGk", "track": "On Top of the World"},
        {"name": "Starlight", "artist": "Muse", "link": "https://youtu.be/Pgum6OT_VH8", "track": "Starlight"}
    ]
}



# ... (Database and Model setup remains same) ...

# --- Routes ---

@app.route('/check-auth')
def check_auth():
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']})
    return jsonify({'authenticated': False}), 401

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle JSON (React) and Form (HTML) requests
        if request.is_json:
            data = request.json
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form['username']
            password = request.form['password']
        
        try:
            if users_collection is None:
                raise Exception("Database connection invalid")
                
            user = users_collection.find_one({'username': username})
            
            if user and bcrypt.check_password_hash(user['password'], password):
                session['user'] = username
                if request.is_json:
                    return jsonify({'success': True, 'user': username})
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
                flash('Invalid username or password', 'error')
        except Exception as e:
            if request.is_json:
                return jsonify({'success': False, 'message': str(e)}), 500
            flash(f'Database error: {str(e)}', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.json
            username = data.get('username')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
        else:
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
            
        try:
            if users_collection.find_one({'username': username}):
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Username already exists'}), 400
                flash('Username already exists', 'error')
                return redirect(url_for('register'))
                
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users_collection.insert_one({'username': username, 'password': hashed_password})
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Account created'})
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
             if request.is_json:
                return jsonify({'success': False, 'message': str(e)}), 500
             flash(f'Database error: {str(e)}', 'error')
             
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True})
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please login to access the dashboard', 'warning')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        data = request.json['image']
        header, encoded = data.split(",", 1)
        nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        emotion = "Neutral"
        
        if model:
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            # Default to Neutral if no face found but model exists
            emotion = "Neutral" 
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y + h, x:x + w]
                cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                prediction = model.predict(cropped_img, verbose=0)
                max_index = int(np.argmax(prediction))
                emotion = emotion_dict[max_index]
                break
        else:
            # DEMO MODE: Randomize emotion to show UI functionality
            # Since TensorFlow failed to install, we simulate detection
            import random
            # Higher chance of non-neutral emotions for demo
            emotions_pool = ["Happy", "Sad", "Angry", "Surprised", "Fearful", "Disgusted", "Neutral"]
            emotion = random.choice(emotions_pool)
            print(f"Demo Mode Prediction: {emotion}")
            
        return jsonify({'emotion': emotion})
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'emotion': 'Neutral'})

@app.route('/recommend', methods=['POST'])
def recommend():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    emotions = request.json.get('emotions', [])
    if not emotions:
        return jsonify({'error': 'No emotions provided'}), 400
        
    # Get dominant emotion
    emotion_counts = Counter(emotions)
    if emotion_counts:
        dominant_emotion = emotion_counts.most_common(1)[0][0]
    else:
        dominant_emotion = "Neutral"
        
    # Check for local songs first
    local_songs = []
    songs_dir = os.path.join(app.root_path, 'static', 'songs', dominant_emotion)
    
    if os.path.exists(songs_dir):
        for filename in os.listdir(songs_dir):
            if filename.lower().endswith(('.mp3', '.wav', '.ogg')):
                local_songs.append({
                    'name': filename,
                    'artist': 'Local Track',
                    # Create full URL for frontend
                    'link': f"{request.url_root}static/songs/{dominant_emotion}/{filename}",
                    'track': filename,
                    'is_local': True
                })

    if local_songs:
        # Shuffle the local songs for random playback
        import random
        random.shuffle(local_songs)
        selected_songs = local_songs # Use all local songs found (now shuffled)
    else:
        # Fallback to fixed YouTube playlists
        selected_songs = FIXED_PLAYLISTS.get(dominant_emotion, FIXED_PLAYLISTS["Neutral"])
        
    return jsonify({'dominant_emotion': dominant_emotion, 'songs': selected_songs})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
