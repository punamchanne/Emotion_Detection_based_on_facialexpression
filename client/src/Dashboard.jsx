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

    useEffect(() => {
        let intervalId;
        if (cameraReady && modelsLoaded && !isScanning) {
            intervalId = setInterval(() => {
                handleScan();
            }, 2000); // Scan every 2 seconds
        }
        return () => clearInterval(intervalId);
    }, [cameraReady, modelsLoaded]); // Start loop when camera is ready

    const handleScan = async () => {
        if (!modelsLoaded || !cameraReady) return;

        setIsScanning(true);
        // setStatus("Scanning..."); 

        try {
            const options = new faceapi.TinyFaceDetectorOptions({ inputSize: 512, scoreThreshold: 0.3 });
            // Just detect face, no need for expressions if we only want presence
            const detections = await faceapi.detectSingleFace(videoRef.current, options);

            if (detections) {
                // Face found
                setEmotionResult("Present");
                setStatus("Status: Person Detected");
            } else {
                // No face found
                setEmotionResult("Unknown");
                setStatus("Status: No Person Detected");
            }
        } catch (err) {
            console.error(err);
            setStatus("Detection error.");
        } finally {
            setIsScanning(false);
        }
    };

    // Removed finishScanning as it's no longer needed for manual flow



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
                        <div className="status-display" style={{ marginTop: '1rem', fontSize: '1.2rem' }}>
                            {status}
                        </div>
                    </div>

                    {emotionResult && (
                        <div style={{ marginTop: '1rem', fontSize: '1.5rem', color: emotionResult === 'Present' ? 'green' : 'red' }}>
                            <strong>{emotionResult === 'Present' ? 'Person Detected' : 'No Person Detected'}</strong>
                        </div>
                    )}
                </div>


            </main>
        </div>
    );
};

export default Dashboard;
