import numpy as np
import streamlit as st
import cv2
import pandas as pd
from collections import Counter
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D

# Page config
st.set_page_config(page_title="Emotion-based Music Recommendation", layout="wide")

# --- Data Loading & Preprocessing ---
@st.cache_resource
def load_data():
    print("Loading music dataset...")
    df = pd.read_csv("muse_v3.csv")
    df['link'] = df['lastfm_url']
    df['name'] = df['track']
    df['emotional'] = df['number_of_emotion_tags']
    df['pleasant'] = df['valence_tags']
    df = df[['name', 'emotional', 'pleasant', 'link', 'artist']]
    df = df.sort_values(by=["emotional", "pleasant"])
    df.reset_index(inplace=True, drop=True)
    return df

@st.cache_resource
def load_model():
    print("Loading model...")
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

@st.cache_resource
def load_haarcascade():
    print("Loading Haarcascade Classifier...")
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        print("Haarcascade Classifier failed to load.")
        return None
    else:
        print("Haarcascade Classifier loaded successfully.")
        return face_cascade

# Load data and model
df = load_data()
model = load_model()
face_cascade = load_haarcascade()

# Segment dataframe by emotion
df_sad = df[:18000]
df_fear = df[18000:36000]
df_angry = df[36000:54000]
df_neutral = df[54000:72000]
df_happy = df[72000:]

emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}

# --- Helper Functions ---
def get_recommendations(emotion_list):
    """Get song recommendations based on detected emotions"""
    data = pd.DataFrame()
    
    emotion_counts = Counter(emotion_list)
    sorted_emotions = [item for item, count in emotion_counts.most_common()]
    
    if len(sorted_emotions) > 5:
        sorted_emotions = sorted_emotions[:5]
        
    num_emotions = len(sorted_emotions)
    
    times = []
    if num_emotions == 1:
        times = [30]
    elif num_emotions == 2:
        times = [30, 20]
    elif num_emotions == 3:
        times = [55, 20, 15]
    elif num_emotions == 4:
        times = [30, 29, 18, 9]
    else:
        times = [10, 7, 6, 5, 2]
        
    for i, emotion in enumerate(sorted_emotions):
        count = times[i] if i < len(times) else 5
        
        if emotion == 'Neutral':
            data = pd.concat([data, df_neutral.sample(n=count)], ignore_index=True)
        elif emotion == 'Angry':
            data = pd.concat([data, df_angry.sample(n=count)], ignore_index=True)
        elif emotion == 'Fearful' or emotion == 'fear':
            data = pd.concat([data, df_fear.sample(n=count)], ignore_index=True)
        elif emotion == 'Happy' or emotion == 'happy':
            data = pd.concat([data, df_happy.sample(n=count)], ignore_index=True)
        else:
            data = pd.concat([data, df_sad.sample(n=count)], ignore_index=True)
            
    return data, sorted_emotions[0] if sorted_emotions else "Neutral"

def process_emotions(emotion_list):
    """Process and deduplicate emotions by frequency"""
    emotion_counts = Counter(emotion_list)
    result = []
    for emotion, count in emotion_counts.items():
        result.extend([emotion] * count)
    
    unique_list = []
    for x in result:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
# --- UI Layout ---
st.markdown("<h2 style='text-align: center; color: #2c3e50'><b>🎵 Emotion Based Music Recommendation</b></h2>", 
            unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: #7f8c8d;'><b>Click on a song name to visit its link</b></h5>",
            unsafe_allow_html=True)
st.markdown("---")

# Create columns for button layout
col1, col2, col3 = st.columns(3)

emotion_list = []

with col2:
    if st.button('🎬 SCAN EMOTION (Click here)', use_container_width=True):
        st.info("📹 Opening webcam... This will scan your face for 20 frames.")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("❌ Cannot access webcam. Please check your camera.")
        else:
            count = 0
            emotion_list = []
            stframe = st.empty()
            status_text = st.empty()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
                count += 1
                
                # Draw rectangles and detect emotions
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y - 50), (x + w, y + h + 10), (255, 0, 0), 2)
                    roi_gray = gray[y:y + h, x:x + w]
                    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                    prediction = model.predict(cropped_img, verbose=0)
                    max_index = int(np.argmax(prediction))
                    emotion = emotion_dict[max_index]
                    emotion_list.append(emotion)
                    
                    cv2.putText(frame, emotion, (x + 20, y - 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Display frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                stframe.image(frame_rgb, channels="RGB", use_column_width=True)
                status_text.text(f"Frame: {count}/20")
                
                if count >= 20:
                    break
            
            cap.release()
            
            if emotion_list:
                emotion_list = process_emotions(emotion_list)
                st.success(f"✅ Emotions detected: {', '.join(emotion_list)}")
            else:
                st.warning("⚠️ No faces detected. Please try again.")

st.markdown("---")

# Recommendation section
if emotion_list:
    rec_df, dominant = get_recommendations(emotion_list)
    
    st.markdown(f"<h3 style='text-align: center;'>🎵 Recommended Songs for: <span style='color: #e74c3c;'>{dominant}</span></h3>", 
                unsafe_allow_html=True)
    st.markdown("---")
    
    if len(rec_df) > 0:
        for idx, (_, row) in enumerate(rec_df.head(30).iterrows(), 1):
            link = row['link']
            name = row['name']
            artist = row['artist']
            
            st.markdown(f"<h4 style='text-align: center;'><a href='{link}' target='_blank'>{idx}. {name}</a></h4>", 
                       unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center; color: #7f8c8d;'><i>{artist}</i></h5>", 
                       unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("No recommendations available.")
else:
    st.info("👉 Click the 'SCAN EMOTION' button to start detecting emotions and get personalized music recommendations!")
