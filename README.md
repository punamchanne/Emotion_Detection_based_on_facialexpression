# 🎵 MoodMelody - Emotion-Based Music Recommendation System

An intelligent music recommendation system that detects your facial emotions in real-time and plays music that matches your mood. Built with React, Flask, and AI-powered emotion detection.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18.3-61DAFB)
![Flask](https://img.shields.io/badge/Flask-3.1-000000)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🎭 **Real-Time Emotion Detection** - Uses face-api.js for client-side facial expression analysis
- 🎵 **Smart Music Recommendations** - Matches songs to your detected emotion
- 🔐 **User Authentication** - Secure login/registration with MongoDB
- 🎲 **Random Playback** - Randomly selects songs from your local music library
- 📱 **Modern UI** - Beautiful, responsive React interface with glassmorphism design
- 🎨 **7 Emotion Categories** - Happy, Sad, Angry, Surprised, Fearful, Disgusted, Neutral
- 🔊 **Auto-Play** - Automatically plays music based on detected mood
- 💾 **Local Music Support** - Play your own MP3/WAV/OGG files

## 🚀 Demo

1. **Sign Up/Login** - Create an account or log in
2. **Start Analysis** - Click the button to activate your webcam
3. **Emotion Detection** - AI analyzes your facial expression
4. **Music Playback** - Enjoy songs that match your mood!

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **face-api.js** - Client-side facial emotion detection
- **Axios** - HTTP client for API requests
- **React Router** - Navigation and routing

### Backend
- **Flask** - Python web framework
- **MongoDB Atlas** - Cloud database for user management
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-Bcrypt** - Password hashing and security
- **Python-dotenv** - Environment variable management

### AI/ML
- **face-api.js** - TensorFlow.js-based facial recognition
- **Tiny Face Detector** - Lightweight face detection model
- **Face Expression Net** - Emotion classification model

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 20.19+ or 22.12+**
- **MongoDB Atlas Account** (free tier works)
- **Webcam** (for emotion detection)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/road2tec/Emotion-based-music-recommendation-system.git
cd Emotion-based-music-recommendation-system
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to client directory
cd client

# Install Node dependencies
npm install

# Return to root directory
cd ..
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Flask Configuration
SECRET_KEY=your_secret_key_here

# MongoDB Configuration
MONGO_URI=your_mongodb_connection_string_here
```

**To get your MongoDB URI:**
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Get your connection string
4. Replace `<password>` with your database password
5. Add it to `.env`

### 5. Add Your Music Files

Organize your music files in the following structure:

```
static/songs/
├── Happy/
│   ├── song1.mp3
│   ├── song2.mp3
│   └── ...
├── Sad/
│   ├── song1.mp3
│   └── ...
├── Angry/
├── Surprised/
├── Fearful/
├── Disgusted/
└── Neutral/
```

**Supported formats:** `.mp3`, `.wav`, `.ogg`

## 🚀 Running the Application

### Option 1: Run Both Servers Separately

**Terminal 1 - Backend (Flask):**
```bash
python app.py
```
Backend will run on: `http://localhost:5000`

**Terminal 2 - Frontend (React):**
```bash
cd client
npm run dev
```
Frontend will run on: `http://localhost:5173` (or 5174/5175 if port is busy)

### Option 2: Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## 📖 Usage Guide

### First Time Setup
1. **Register** - Create a new account with username and password
2. **Login** - Sign in with your credentials

### Using the System
1. **Allow Camera Access** - Grant permission when prompted
2. **Position Yourself** - Ensure your face is visible and well-lit
3. **Click "Start Analysis"** - The system will capture your expression
4. **Emotion Detected** - Your mood will be displayed
5. **Music Plays** - A random song matching your emotion will auto-play
6. **Browse Songs** - Click on any song card to play it

### Tips for Best Results
- 🌞 **Good Lighting** - Face the light source
- 📷 **Clear View** - Keep your face centered in the camera
- 😊 **Express Clearly** - Make distinct facial expressions
- 🔄 **Try Again** - Click "Start Analysis" to re-scan

## 🎨 Emotion Categories

| Emotion | Description | Music Style |
|---------|-------------|-------------|
| 😊 Happy | Joyful, upbeat expressions | Uplifting, energetic tracks |
| 😢 Sad | Melancholic, down expressions | Slow, emotional ballads |
| 😠 Angry | Frustrated, intense expressions | Heavy, aggressive music |
| 😮 Surprised | Shocked, amazed expressions | Dynamic, unexpected tracks |
| 😨 Fearful | Anxious, worried expressions | Tense, atmospheric music |
| 🤢 Disgusted | Repulsed expressions | Edgy, unconventional tracks |
| 😐 Neutral | Calm, relaxed expressions | Chill, ambient music |

## 🔒 Security Features

- ✅ **Password Hashing** - Bcrypt encryption for user passwords
- ✅ **Session Management** - Secure Flask sessions
- ✅ **Environment Variables** - Sensitive data stored in `.env`
- ✅ **CORS Protection** - Configured for specific origins
- ✅ **Client-Side Detection** - No facial data sent to server

## 📁 Project Structure

```
Emotion-based-music-recommendation-system/
├── client/                      # React frontend
│   ├── src/
│   │   ├── App.jsx             # Main app component
│   │   ├── Dashboard.jsx       # Main dashboard with emotion detection
│   │   ├── Login.jsx           # Login component
│   │   ├── Register.jsx        # Registration component
│   │   ├── api.js              # Axios configuration
│   │   └── index.css           # Global styles
│   ├── package.json
│   └── vite.config.js
├── static/
│   ├── css/                    # Legacy CSS (for HTML templates)
│   ├── js/                     # Legacy JS (for HTML templates)
│   └── songs/                  # Music files organized by emotion
├── templates/                  # Flask HTML templates (legacy)
├── app.py                      # Flask backend
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🐛 Troubleshooting

### Camera Not Working
- Check browser permissions (allow camera access)
- Ensure no other application is using the camera
- Try a different browser (Chrome/Edge recommended)

### "No Face Detected" Error
- Improve lighting conditions
- Move closer to the camera
- Ensure face is centered and clearly visible
- Try making more distinct facial expressions

### Songs Not Playing
- Check that music files exist in `static/songs/[Emotion]/`
- Verify file formats are `.mp3`, `.wav`, or `.ogg`
- Check browser console for errors (F12)

### Database Connection Issues
- Verify MongoDB URI in `.env` file
- Check MongoDB Atlas cluster is running
- Ensure IP address is whitelisted in MongoDB Atlas

### Port Already in Use
- The React dev server will automatically try ports 5173, 5174, 5175
- Update CORS settings in `app.py` if using a different port

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Road2Tech**
- GitHub: [@road2tec](https://github.com/road2tec)

## 🙏 Acknowledgments

- [face-api.js](https://github.com/justadudewhohacks/face-api.js) - For facial emotion detection
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [React](https://react.dev/) - UI library
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Database hosting
- [Vite](https://vitejs.dev/) - Build tool

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Contact the maintainer

---

**⭐ If you found this project helpful, please consider giving it a star!**

Made with ❤️ by Road2Tech
