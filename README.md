# ☕ AI Coffee Recommender (Face Detection)

An intelligent system that captures your face, detects your mood, and suggests the perfect coffee to match how you feel. Built with React and Flask.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18.3-61DAFB)
![Flask](https://img.shields.io/badge/Flask-3.1-000000)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248)

## ✨ Main Features

- 📸 **Face Capture Registration** - Take a photo of yourself when you sign up to create your account.
- 🎭 **Real-Time Mood Detection** - The AI looks at your face and understands if you are happy, sad, or neutral.
- ☕ **Smart Coffee Suggestions** - Gives you a choice of 3 different coffees that match your current mood.
- 🔐 **Secure Login** - Keep your account safe with a username and password.
- 📱 **Beautiful Design** - A smooth and easy-to-use interface that looks great on your screen.

## 🚀 How it Works

1. **Sign Up** - Create an account and capture your face using your camera.
2. **Log In** - Sign in to your dashboard.
3. **Scan Your Face** - The AI will automatically start looking for your expression.
4. **Get Coffee Ideas** - Pick from the coffees shown in the dropdown menu.

## 🛠️ Technology Used

- **React** for the website interface.
- **Flask (Python)** for the backend server.
- **MongoDB** for storing user details safely.
- **face-api.js** for detecting facial expressions.

## 📋 What you need

- **Python 3.11** or newer.
- **Node.js** (for running the react part).
- **Webcam** (to see your face).

## 🔧 Setup Guide

### 1. Download the code
```bash
cd AI-Coffee-Recommender
```

### 2. Setup Backend (Server)
```bash
# Create and start virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install tools
pip install -r requirements.txt
```

### 3. Setup Frontend (Website)
```bash
cd client
npm install
cd ..
```

### 4. Setup Database
Create a `.env` file and add your MongoDB link:
```env
SECRET_KEY=any_secret_key
MONGO_URI=your_mongodb_link
```

## 🚀 Running the App

**Start Backend:**
```bash
python app.py
```

**Start Frontend:**
```bash
cd client
npm run dev
```

Open `http://localhost:5173` in your browser.

## ☕ Mood & Coffee Guide

| Your Mood | Coffee Suggestion | Why? |
|-----------|-------------------|------|
| 😊 Happy | Sweet Latte / Espresso | To keep you feeling energetic and joyful! |
| 😢 Sad | Hot Mocha / Cappuccino | To make you feel warm and comfortable. |
| 😠 Angry | Iced Americano / Cold Brew | To help you cool down and relax. |
| 😨 Fearful | Decaf / Warm Milk Coffee | Gentle drinks to help you feel calm. |
| 😐 Neutral | Regular Coffee / Hazelnut | Good balanced choice for your day. |
| 😮 Surprised | Sparkling Coffee / New Flavors | Something fun and different for your mood! |

## 🤝 Need Help?
If the camera doesn't start, make sure you have allowed camera permissions in your browser.

---

**⭐ If you like this project, give it a star!**
