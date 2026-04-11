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
    const [coffeeRecommendations, setCoffeeRecommendations] = useState([]);
    const [selectedCoffee, setSelectedCoffee] = useState(null);
    const [cameraReady, setCameraReady] = useState(false);
    const [isPersonDetected, setIsPersonDetected] = useState(false);
    const [isVerified, setIsVerified] = useState(false);
    const [referenceDescriptor, setReferenceDescriptor] = useState(null);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await api.get('/check-auth');
                setUser(res.data.user);
                fetchUserFace();
            } catch (err) {
                navigate('/login');
            }
        };

        const loadModels = async () => {
            setStatus("Loading High-Accuracy AI...");
            try {
                await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
                await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
                await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
                await faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL);
                setModelsLoaded(true);
                setStatus("AI ready. Starting camera...");
                startCamera();
            } catch (err) {
                console.error(err);
                setStatus("Error loading AI. Refresh page.");
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

    const fetchUserFace = async () => {
        try {
            const res = await api.get('/get-face');
            if (res.data.face_image) {
                const img = await faceapi.fetchImage(res.data.face_image);
                const detection = await faceapi
                    .detectSingleFace(img)
                    .withFaceLandmarks()
                    .withFaceDescriptor();
                if (detection) setReferenceDescriptor(detection.descriptor);
            }
        } catch (e) {
            console.error("Error fetching registered face:", e);
        }
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.onloadedmetadata = () => {
                    setCameraReady(true);
                    setStatus("Searching for person...");
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
            }, 1000); // 1 second intervals for better recognition
        }
        return () => clearInterval(intervalId);
    }, [cameraReady, modelsLoaded, isScanning, referenceDescriptor]);

    const handleScan = async () => {
        if (!modelsLoaded || !cameraReady || !videoRef.current) return;
        setIsScanning(true);
        try {
            const detections = await faceapi
                .detectSingleFace(videoRef.current)
                .withFaceLandmarks()
                .withFaceExpressions()
                .withFaceDescriptor();

            if (!detections) {
                setIsPersonDetected(false);
                setIsVerified(false);
                setStatus("Status: No Person Detected");
                return;
            }

            setIsPersonDetected(true);
            if (referenceDescriptor && detections.descriptor) {
                const distance = faceapi.euclideanDistance(referenceDescriptor, detections.descriptor);
                if (distance < 0.55) {
                    setIsVerified(true);
                    setStatus("Authorized User Verified!");
                } else {
                    setIsVerified(false);
                    setStatus("Unauthorized Face Detected!");
                }
            } else {
                setIsVerified(true); 
                setStatus("Face Detected");
            }

            const expressions = detections.expressions || {};
            const dominant = Object.keys(expressions).reduce((a, b) =>
                expressions[a] > expressions[b] ? a : b
            );
            const formattedEmotion = dominant.charAt(0).toUpperCase() + dominant.slice(1);
            
            if (formattedEmotion !== emotionResult || coffeeRecommendations.length === 0) {
                setEmotionResult(formattedEmotion);
                try {
                    const coffeeRes = await api.post('/coffee', { emotion: formattedEmotion });
                    const recs = coffeeRes.data.recommendations || [];
                    if (recs.length > 0) {
                        setCoffeeRecommendations(recs);
                        setSelectedCoffee(recs[0]);
                    }
                } catch (e) {
                    console.error("Coffee API error:", e);
                }
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsScanning(false);
        }
    };

    const handleLogout = async () => {
        await api.get('/logout');
        navigate('/login');
    };

    return (
        <div className="dashboard-layout">
            <header className="dashboard-header">
                <div className="brand">
                    <h1>AI Coffee Recommender</h1>
                </div>
                <div className="user-controls">
                    <span>Logged in: <strong>{user}</strong></span>
                    <button className="btn-logout" onClick={handleLogout}>Logout</button>
                </div>
            </header>

            <main className="dashboard-main">
                <div className="scanner-container">
                    <div className={`video-wrapper ${isScanning ? 'scanning' : ''} ${!isVerified && isPersonDetected ? 'unauthorized' : ''}`} style={{ position: 'relative' }}>
                        <video ref={videoRef} id="video" autoPlay muted playsInline></video>
                        <div className="scan-overlay">
                            {isPersonDetected && !isVerified && (
                                <div className="warning-overlay" style={{
                                    position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
                                    background: 'rgba(255, 0, 0, 0.2)', border: '4px solid #ff5252',
                                    display: 'flex', justifyContent: 'center', alignItems: 'center',
                                    color: 'white', fontWeight: 'bold', zIndex: 10
                                }}>
                                    UNAUTHORIZED PERSON
                                </div>
                            )}
                            <div className="scan-line"></div>
                        </div>
                    </div>

                    <div className="info-panel" style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                        {/* Status Message (Always visible) */}
                        <div className="detection-status" style={{ 
                            fontSize: '1.4rem', 
                            fontWeight: 'bold',
                            color: !isPersonDetected ? '#ff5252' : (isVerified ? '#00c853' : '#ff9100'),
                            marginBottom: '1rem'
                        }}>
                             {status}
                        </div>

                        {/* Only show these if a person is detected AND verified */}
                        {isVerified && isPersonDetected && (
                            <div className="analysis-results" style={{ animation: 'fadeIn 0.8s ease' }}>
                                <div style={{ fontSize: '2.5rem', fontWeight: 900, color: '#fff', marginBottom: '0.5rem' }}>
                                    Hello, {user}!
                                </div>
                                
                                {emotionResult && (
                                    <div className="emotion-display" style={{ fontSize: '1.6rem', color: '#64ffda', marginBottom: '1.5rem' }}>
                                        Mood: <strong>{emotionResult}</strong>
                                    </div>
                                )}

                                {coffeeRecommendations.length > 0 && (
                                    <div key={emotionResult} className="coffee-section" style={{ 
                                        background: 'rgba(255, 255, 255, 0.05)', 
                                        padding: '2rem', 
                                        borderRadius: '16px',
                                        border: '2px solid rgba(255, 255, 255, 0.1)',
                                        maxWidth: '500px',
                                        margin: '0 auto',
                                        animation: 'slideUp 0.6s ease-out'
                                    }}>
                                        <h3 style={{ marginBottom: '1rem', color: '#ffbd59' }}>Coffee Recommendations</h3>
                                        
                                        <select 
                                            className="form-control" 
                                            style={{ background: '#2c2c2c', border: '1px solid #ffbd59', color: 'white', marginBottom: '1.5rem' }}
                                            value={coffeeRecommendations.findIndex(c => c.name === selectedCoffee?.name)}
                                            onChange={(e) => {
                                                const index = parseInt(e.target.value);
                                                setSelectedCoffee(coffeeRecommendations[index]);
                                            }}
                                        >
                                            {coffeeRecommendations.map((coffee, idx) => (
                                                <option key={idx} value={idx}>{coffee.name}</option>
                                            ))}
                                        </select>

                                        {selectedCoffee && (
                                            <div key={selectedCoffee.name} className="selected-coffee-details" style={{ textAlign: 'left', animation: 'fadeIn 0.5s' }}>
                                                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#ffbd59' }}>
                                                    {selectedCoffee.name}
                                                </div>
                                                <div style={{ fontSize: '0.9rem', opacity: 0.7 }}>
                                                    Brand: {selectedCoffee.brand}
                                                </div>
                                                <div style={{ padding: '0.8rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', marginTop: '0.5rem' }}>
                                                    {selectedCoffee.why}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}

                        {isPersonDetected && !isVerified && (
                             <div className="warning-text" style={{ fontSize: '1.2rem', color: '#ff5252', marginTop: '1.5rem' }}>
                                 Safety Alert: Unauthorized Person Detected! Access Denied.
                             </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;