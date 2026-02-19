import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import * as faceapi from '@vladmandic/face-api';
import api from './api';

const MODEL_URL = 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/';

const Dashboard = () => {
    const navigate = useNavigate();
    const videoRef = useRef(null);


    const [user, setUser] = useState(null);
    const [status, setStatus] = useState('Initializing...');
    const [isScanning, setIsScanning] = useState(false);
    const [modelsLoaded, setModelsLoaded] = useState(false);
    const [emotionResult, setEmotionResult] = useState(null);

    const [cameraReady, setCameraReady] = useState(false);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await api.get('/check-auth');
                setUser(res.data.user);
            } catch (err) {
                navigate('/login');
            }
        };

        const loadModels = async () => {
            setStatus("Loading AI models...");
            try {
                await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
                await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);
                setModelsLoaded(true);
                setStatus("Models loaded. Starting camera...");
                startCamera();
            } catch (err) {
                console.error(err);
                setStatus("Error loading AI models. Refresh page.");
            }
        };

        checkAuth();
        loadModels();

        return () => {
            if (videoRef.current && videoRef.current.srcObject) {
                videoRef.current.srcObject.getTracks().forEach(track => track.stop());
            }
        };
    }, [navigate]);

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.onloadedmetadata = () => {
                    setCameraReady(true);
                    setStatus("Ready to scan");
                };
            }
        } catch (err) {
            console.error(err);
            setStatus("Error accessing camera. Please allow permissions.");
        }
    };

    const handleScan = async () => {
        if (!modelsLoaded || isScanning || !cameraReady) return;

        setIsScanning(true);
        setStatus("Snapshotting...");
        setEmotionResult(null);


        await new Promise(r => setTimeout(r, 500));

        try {
            const options = new faceapi.TinyFaceDetectorOptions({ inputSize: 512, scoreThreshold: 0.2 });
            const detections = await faceapi.detectSingleFace(videoRef.current, options).withFaceExpressions();

            if (detections) {
                const expressions = detections.expressions;
                console.log("Detected Expressions:", expressions);

                // Anti-neutral bias: find the strongest non-neutral emotion
                let dominantExpression = 'neutral';
                let maxNonNeutralScore = 0;

                // Check all non-neutral emotions first
                const emotionPriority = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted'];

                for (const emotion of emotionPriority) {
                    const score = expressions[emotion] || 0;
                    if (score > maxNonNeutralScore) {
                        maxNonNeutralScore = score;
                        dominantExpression = emotion;
                    }
                }

                // Only use neutral if it's VERY dominant (>0.85) AND no other emotion is significant (>0.15)
                if (expressions.neutral > 0.85 && maxNonNeutralScore < 0.15) {
                    dominantExpression = 'neutral';
                }

                // Extra boost for clear emotions (lower threshold)
                if (expressions.happy > 0.25) dominantExpression = 'happy';
                if (expressions.sad > 0.25) dominantExpression = 'sad';
                if (expressions.angry > 0.25) dominantExpression = 'angry';
                if (expressions.surprised > 0.25) dominantExpression = 'surprised';
                if (expressions.fearful > 0.25) dominantExpression = 'fearful';
                if (expressions.disgusted > 0.25) dominantExpression = 'disgusted';

                console.log(`Selected emotion: ${dominantExpression} (neutral: ${expressions.neutral}, max non-neutral: ${maxNonNeutralScore})`);

                const formattedEmotion = dominantExpression.charAt(0).toUpperCase() + dominantExpression.slice(1);
                finishScanning(formattedEmotion);
            } else {
                setStatus("No face detected. Try moving closer.");
                setIsScanning(false);
            }
        } catch (err) {
            console.error(err);
            setStatus("Detection error. Try again.");
            setIsScanning(false);
        }
    };

    const finishScanning = async (emotion) => {
        setStatus(`Detected: ${emotion}.`);
        setEmotionResult(emotion);
        setIsScanning(false);
        // Reset status after a delay to allow re-scanning
        setTimeout(() => setStatus("Ready to scan again"), 2000);
    };



    const handleLogout = async () => {
        await api.get('/logout');
        navigate('/login');
    };

    return (
        <div className="dashboard-layout">
            <header className="dashboard-header">
                <div className="brand">
                    <h1>MoodMelody</h1>
                </div>
                <div className="user-controls">
                    <span>Welcome, {user}</span>
                    <button className="btn-logout" onClick={handleLogout}>Logout</button>
                </div>
            </header>

            <main className="dashboard-main">
                <div className="scanner-container">
                    <div className={`video-wrapper ${isScanning ? 'scanning' : ''}`}>
                        <video ref={videoRef} id="video" autoPlay muted playsInline></video>
                        <div className="scan-overlay">
                            <div className="scan-line"></div>
                        </div>
                    </div>

                    <div className="controls-wrapper">
                        <button
                            className="btn-primary"
                            style={{ width: '200px' }}
                            onClick={handleScan}
                            disabled={!cameraReady || isScanning}
                        >
                            {isScanning ? 'Scanning...' : 'Start Analysis'}
                        </button>
                        <div className="status-display">{status}</div>
                    </div>

                    {emotionResult && (
                        <div style={{ marginTop: '1rem', fontSize: '1.5rem', color: 'var(--primary-color)' }}>
                            Detected Mood: <strong>{emotionResult}</strong>
                        </div>
                    )}
                </div>


            </main>
        </div>
    );
};

export default Dashboard;
